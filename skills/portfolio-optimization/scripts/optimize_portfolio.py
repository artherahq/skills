#!/usr/bin/env python3
"""
optimize_portfolio.py — estimation-robust weights, with the honesty check
most optimizers skip: does the clever method actually beat equal weight
out-of-sample?

Methods (deliberately none that require expected returns — sample means are
the noisiest input in finance, and optimizers amplify their noise):

  equal    equal weight (the benchmark everything must beat)
  invvol   inverse volatility
  minvar   long-only minimum variance (projected gradient on the simplex)
  erc      equal risk contribution / risk parity (cyclical rebalancing)
  hrp      hierarchical risk parity (López de Prado: cluster → quasi-diag →
           recursive bisection), implemented inline

All covariance estimation applies Ledoit–Wolf-style shrinkage toward the
identity-scaled target when the panel is short relative to breadth — and the
report says when and how much.

Modes:
  --method X         weights + diagnostics (risk contributions, effective N,
                     portfolio vol) for one method
  --method compare   walk-forward comparison: refit each method on a rolling
                     window, hold out the next block, and report OOS vol /
                     Sharpe vs equal weight. If the fancy method does not beat
                     EW out-of-sample, the report says `optimizer_no_edge` —
                     that is a result, not a failure of the script.

Inputs:
  --returns   wide CSV: date + one column of periodic simple returns per asset
  --max-weight optional cap per asset (post-normalization, long-only)
  --freq      daily|weekly|monthly (default daily)

Try it with no data:  python optimize_portfolio.py --demo

Depends only on pandas + numpy; clustering, shrinkage, simplex projection are
implemented inline.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

PERIODS = {"daily": 252, "weekly": 52, "monthly": 12}
METHODS = ["equal", "invvol", "minvar", "erc", "hrp"]


# ─────────────────────────── covariance with disclosed shrinkage ─────────────
def shrunk_cov(rets: np.ndarray) -> tuple[np.ndarray, float]:
    """Sample covariance shrunk toward its identity-scaled target.

    Intensity follows a Ledoit–Wolf-flavored heuristic driven by T/N — short,
    wide panels get more shrinkage. Returned so the report can disclose it.
    """
    t, n = rets.shape
    sample = np.cov(rets, rowvar=False, ddof=1)
    target = np.eye(n) * np.trace(sample) / n
    intensity = min(1.0, n / max(t, 1) * 0.5)
    return (1 - intensity) * sample + intensity * target, float(intensity)


# ─────────────────────────── weight engines ─────────────────────────────────
def _project_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {w >= 0, sum w = 1} (sort-based)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    theta = (css[rho] - 1) / (rho + 1.0)
    return np.maximum(v - theta, 0.0)


def w_equal(cov: np.ndarray) -> np.ndarray:
    n = cov.shape[0]
    return np.full(n, 1.0 / n)


def w_invvol(cov: np.ndarray) -> np.ndarray:
    iv = 1.0 / np.sqrt(np.diag(cov))
    return iv / iv.sum()


def w_minvar(cov: np.ndarray, iters: int = 500) -> np.ndarray:
    """Long-only min variance via projected gradient descent on the simplex."""
    n = cov.shape[0]
    w = np.full(n, 1.0 / n)
    lr = 1.0 / (np.linalg.norm(cov, 2) * 2 + 1e-12)
    for _ in range(iters):
        w = _project_simplex(w - lr * 2.0 * cov @ w)
    return w


def w_erc(cov: np.ndarray, iters: int = 500) -> np.ndarray:
    """Equal risk contribution via multiplicative cyclical updates."""
    n = cov.shape[0]
    w = w_invvol(cov).copy()
    for _ in range(iters):
        mrc = cov @ w
        rc = w * mrc
        target = rc.mean()
        w = w * np.sqrt(target / np.maximum(rc, 1e-12))
        w = np.maximum(w, 1e-12)
        w = w / w.sum()
    return w


def _single_linkage_order(corr: np.ndarray) -> list[int]:
    """Cluster assets on distance sqrt((1-ρ)/2), single linkage, and return the
    leaf order (quasi-diagonalization). O(n³) agglomerative — fine for books."""
    n = corr.shape[0]
    dist = np.sqrt(np.clip((1 - corr) / 2, 0, None))
    clusters: dict[int, list[int]] = {i: [i] for i in range(n)}
    d = {(i, j): dist[i, j] for i in range(n) for j in range(i + 1, n)}
    next_id = n
    while len(clusters) > 1:
        (a, b), _ = min(d.items(), key=lambda kv: kv[1])
        merged = clusters[a] + clusters[b]
        del clusters[a], clusters[b]
        d = {k: v for k, v in d.items() if a not in k and b not in k}
        for c, members in clusters.items():
            link = min(dist[x, y] for x in merged for y in members)
            d[(min(c, next_id), max(c, next_id))] = link
        clusters[next_id] = merged
        next_id += 1
    return clusters[next_id - 1]


def w_hrp(cov: np.ndarray) -> np.ndarray:
    """Hierarchical risk parity: quasi-diag order, then recursive bisection with
    inverse-variance allocation between halves."""
    std = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)
    order = _single_linkage_order(corr)
    w = np.ones(cov.shape[0])

    def cluster_var(items: list[int]) -> float:
        sub = cov[np.ix_(items, items)]
        iv = 1.0 / np.diag(sub)
        cw = iv / iv.sum()
        return float(cw @ sub @ cw)

    def bisect(items: list[int]):
        if len(items) <= 1:
            return
        mid = len(items) // 2
        left, right = items[:mid], items[mid:]
        vl, vr = cluster_var(left), cluster_var(right)
        alloc_left = 1 - vl / (vl + vr)
        for i in left:
            w[i] *= alloc_left
        for i in right:
            w[i] *= 1 - alloc_left
        bisect(left)
        bisect(right)

    bisect(order)
    return w / w.sum()


ENGINES = {"equal": w_equal, "invvol": w_invvol, "minvar": w_minvar,
           "erc": w_erc, "hrp": w_hrp}


def apply_cap(w: np.ndarray, cap: float | None) -> np.ndarray:
    """Iterative long-only cap: clip, renormalize the rest."""
    if cap is None or cap >= 1.0:
        return w
    w = w.copy()
    for _ in range(50):
        over = w > cap
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        under = ~over
        if w[under].sum() > 0:
            w[under] += excess * w[under] / w[under].sum()
        else:
            break
    return w / w.sum()


# ─────────────────────────── diagnostics ────────────────────────────────────
def diagnostics(cov: np.ndarray, w: np.ndarray, p: int, symbols: list[str]) -> dict:
    port_var = float(w @ cov @ w)
    mrc = cov @ w
    rc = w * mrc / port_var if port_var > 0 else np.zeros_like(w)
    hhi = float(np.sum(w ** 2))
    return {
        "weights": {s: round(float(x), 4) for s, x in zip(symbols, w)},
        "portfolio_vol_annualized": round(math.sqrt(port_var * p), 4),
        "effective_n": round(1.0 / hhi, 2) if hhi > 0 else 0.0,
        "risk_contributions": {s: round(float(x), 4) for s, x in zip(symbols, rc)},
        "max_risk_contribution": round(float(rc.max()), 4) if len(rc) else None,
    }


# ─────────────────────────── walk-forward comparison ─────────────────────────
def walk_forward_compare(rets: pd.DataFrame, p: int, *, window: int = 252,
                         hold: int = 21, cap: float | None = None) -> dict:
    """Refit each method on a rolling window, hold the weights for the next
    block, chain the OOS returns. The honesty engine of this skill."""
    r = rets.to_numpy(dtype=float)
    t = r.shape[0]
    if t < window + hold * 2:
        return {"skipped": True,
                "reason": f"need >= {window + hold * 2} observations for walk-forward, have {t}"}
    oos: dict[str, list[np.ndarray]] = {m: [] for m in METHODS}
    start = window
    while start + 1 <= t - 1:
        fit = r[start - window:start]
        cov, _ = shrunk_cov(fit)
        block = r[start:start + hold]
        for m in METHODS:
            w = apply_cap(ENGINES[m](cov), cap)
            oos[m].append(block @ w)
        start += hold
    table = {}
    for m in METHODS:
        series = np.concatenate(oos[m])
        sd = np.std(series, ddof=1)
        table[m] = {
            "oos_vol_annualized": round(float(sd * math.sqrt(p)), 4),
            "oos_sharpe": round(float(np.mean(series) / sd * math.sqrt(p)), 4) if sd > 0 else None,
            "oos_max_drawdown": round(float(
                (np.cumprod(1 + series) / np.maximum.accumulate(np.cumprod(1 + series)) - 1).min()), 4),
        }
    flags = []
    ew_sharpe = table["equal"]["oos_sharpe"] or 0
    for m in METHODS:
        if m == "equal":
            continue
        s = table[m]["oos_sharpe"]
        if s is not None and s <= ew_sharpe:
            flags.append({"severity": "info", "code": "optimizer_no_edge",
                          "detail": f"{m} did not beat equal weight out-of-sample "
                                    f"({s} vs {ew_sharpe}) — common, and worth knowing"})
    return {"skipped": False, "window": window, "hold": hold,
            "oos_table": table, "flags": flags}


# ─────────────────────────── entry ──────────────────────────────────────────
def optimize(rets: pd.DataFrame, *, method: str = "hrp", freq: str = "daily",
             max_weight: float | None = None) -> dict:
    p = PERIODS[freq]
    clean = rets.dropna()
    t, n = clean.shape
    if n < 2 or t < 30:
        return {"error": f"need >= 2 assets and >= 30 observations, have {n} × {t}"}
    symbols = list(clean.columns)
    r = clean.to_numpy(dtype=float)
    cov, intensity = shrunk_cov(r)

    notes = []
    if intensity > 0.05:
        notes.append(f"covariance shrunk toward identity target with intensity "
                     f"{intensity:.2f} (T={t} vs N={n}); raw sample cov would be noise-fitted")
    if t < 2 * n:
        notes.append(f"history ({t}) < 2× breadth ({n}) — every weight here is an estimate "
                     "with wide error bars; prefer hrp/erc over minvar")

    if method == "compare":
        report = {"mode": "compare",
                  "walk_forward": walk_forward_compare(clean, p, cap=max_weight),
                  "notes": notes}
        return report

    if method not in ENGINES:
        return {"error": f"unknown method {method!r}; choose from {METHODS + ['compare']}"}
    w = apply_cap(ENGINES[method](cov), max_weight)
    return {"mode": "weights", "method": method,
            **diagnostics(cov, w, p, symbols),
            "notes": notes,
            "disclosure": [
                "Weights minimize/balance historical risk only — no expected-return input, no return forecast implied.",
                "This is research output, not individualized investment advice.",
            ]}


# ─────────────────────────── demo ───────────────────────────────────────────
def demo() -> int:
    """Two correlated clusters + defensives: HRP must see the structure
    (cluster gets shared budget), ERC must equalize risk contributions."""
    rng = np.random.default_rng(31)
    n = 600
    idx = pd.bdate_range("2023-06-01", periods=n)
    tech = rng.normal(0.0004, 0.015, n)
    energy = rng.normal(0.0002, 0.012, n)
    rets = pd.DataFrame({
        "TECH1": tech + rng.normal(0, 0.004, n),
        "TECH2": tech + rng.normal(0, 0.004, n),
        "TECH3": tech + rng.normal(0, 0.005, n),
        "ENGY1": energy + rng.normal(0, 0.004, n),
        "ENGY2": energy + rng.normal(0, 0.005, n),
        "BOND":  rng.normal(0.0001, 0.003, n),
    }, index=idx)

    print("═" * 68)
    print("DEMO — 3 correlated tech + 2 energy + 1 bond: structure-aware weights")
    print("═" * 68)
    for method in ("equal", "erc", "hrp"):
        rep = optimize(rets, method=method)
        print(f"\n▶ {method}")
        print("  weights:", rep["weights"])
        print(f"  vol {rep['portfolio_vol_annualized']:.1%} · effN {rep['effective_n']} · "
              f"maxRC {rep['max_risk_contribution']}")
    cmp_rep = optimize(rets, method="compare")
    wf = cmp_rep["walk_forward"]
    print("\n▶ walk-forward OOS (fit 252, hold 21):")
    for m, row in wf["oos_table"].items():
        print(f"  {m:7} vol {row['oos_vol_annualized']:.1%} · sharpe {row['oos_sharpe']} · "
              f"maxDD {row['oos_max_drawdown']:.1%}")
    for f in wf["flags"]:
        print(f"  [INFO] {f['code']}: {f['detail']}")

    hrp = optimize(rets, method="hrp")["weights"]
    erc_rc = optimize(rets, method="erc")["risk_contributions"]
    tech_total = hrp["TECH1"] + hrp["TECH2"] + hrp["TECH3"]
    ok = hrp["BOND"] > 1 / 6 and tech_total < 0.5 and \
         max(erc_rc.values()) - min(erc_rc.values()) < 0.05
    print("\n" + ("demo OK — HRP sees the cluster, ERC equalizes risk" if ok
                  else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Estimation-robust portfolio optimization")
    ap.add_argument("--returns", help="wide CSV: date + one return column per asset")
    ap.add_argument("--method", default="hrp", choices=METHODS + ["compare"])
    ap.add_argument("--max-weight", type=float, default=None)
    ap.add_argument("--freq", default="daily", choices=sorted(PERIODS))
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()
    if not args.returns:
        ap.error("--returns is required (or use --demo)")
    rets = pd.read_csv(args.returns, parse_dates=["date"]).set_index("date")
    report = optimize(rets, method=args.method, freq=args.freq, max_weight=args.max_weight)
    out = json.dumps(report, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 1 if report.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
