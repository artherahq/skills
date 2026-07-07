#!/usr/bin/env python3
"""
validation_gauntlet.py — the honest-backtest validation gauntlet.

A backtest is a *claim*, not a result. This script runs the four checks that
separate a tradable edge from a research artefact, holding the strategy fixed:

  1  Honest metrics : CAGR, vol, Sharpe, Sortino, maxDD, Calmar, win rate,
                      profit factor — computed one way, no cherry-picking.
  2  Cost ladder    : the same returns net of 0/5/10/25/50 bps per unit of
                      turnover. An edge that dies at 10 bps was never an edge.
  3  Split stability: in-sample vs out-of-sample Sharpe (chronological split,
                      no shuffling). Decay > 50% is the classic overfit smell.
  4  Robustness     : stationary block bootstrap CI for the Sharpe ratio and
                      p(SR <= 0); plus the Deflated Sharpe Ratio when the
                      number of tried variants (--trials) is disclosed.

Verdict: PASS / WARN / FAIL with machine-readable reasons. Exit code 0 only on
PASS or WARN — a FAIL exits 1 so completion gates can enforce it.

Inputs:
  --returns  CSV with columns: date, return   (periodic simple returns)
  --weights  optional wide CSV: date + one column per asset (portfolio weights
             AFTER rebalance). Enables real turnover -> cost ladder.
  --freq     daily|weekly|monthly (annualization; default daily)
  --trials   how many strategy variants were tried before this one (honesty
             input for the Deflated Sharpe Ratio; default 1)
  --split    in-sample fraction for the stability check (default 0.7)
  --json     write the full machine-readable report to this path

Try it with no data:  python validation_gauntlet.py --demo
The demo contrasts a genuine (persistent) signal with an overfit (lucky-noise)
strategy on the same synthetic market — the second must FAIL the gauntlet.

Depends only on pandas + numpy. Bootstrap and DSR are implemented inline.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

PERIODS = {"daily": 252, "weekly": 52, "monthly": 12}
COST_LADDER_BPS = [0, 5, 10, 25, 50]
EULER_GAMMA = 0.5772156649015329


# ───────────────────────────── metrics (one way, no options) ─────────────────
def _ann(r: np.ndarray, p: int) -> dict:
    r = np.asarray(r, dtype=float)
    n = len(r)
    if n < 2:
        return {}
    equity = np.cumprod(1 + r)
    total = float(equity[-1] - 1)
    years = n / p
    cagr = float(equity[-1] ** (1 / years) - 1) if equity[-1] > 0 and years > 0 else float("nan")
    vol = float(np.std(r, ddof=1) * math.sqrt(p))
    sharpe = float(np.mean(r) / np.std(r, ddof=1) * math.sqrt(p)) if np.std(r, ddof=1) > 0 else float("nan")
    downside = r[r < 0]
    sortino = (float(np.mean(r) / np.std(downside, ddof=1) * math.sqrt(p))
               if len(downside) > 1 and np.std(downside, ddof=1) > 0 else float("nan"))
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1
    maxdd = float(dd.min())
    calmar = float(cagr / abs(maxdd)) if maxdd < 0 and not math.isnan(cagr) else float("nan")
    wins = r[r > 0]
    losses = r[r < 0]
    win_rate = float(len(wins) / max(1, len(wins) + len(losses)))
    profit_factor = (float(wins.sum() / abs(losses.sum()))
                     if len(losses) and losses.sum() < 0 else float("nan"))
    return {
        "observations": n, "total_return": round(total, 6), "cagr": round(cagr, 6),
        "volatility": round(vol, 6), "sharpe": round(sharpe, 4), "sortino": round(sortino, 4),
        "max_drawdown": round(maxdd, 6), "calmar": round(calmar, 4),
        "win_rate": round(win_rate, 4), "profit_factor": round(profit_factor, 4),
    }


def turnover_series(weights: pd.DataFrame) -> np.ndarray:
    """Per-period one-way turnover: 0.5 * Σ|w_t − w_{t−1}| (first period = full entry)."""
    w = weights.fillna(0.0).to_numpy(dtype=float)
    prev = np.vstack([np.zeros((1, w.shape[1])), w[:-1]])
    return 0.5 * np.abs(w - prev).sum(axis=1)


# ───────────────────────────── robustness: bootstrap + DSR ───────────────────
def stationary_bootstrap_sharpe(r: np.ndarray, p: int, n_boot: int = 2000,
                                avg_block: int = 20, seed: int = 7) -> dict:
    """Politis–Romano stationary bootstrap of the annualized Sharpe."""
    rng = np.random.default_rng(seed)
    r = np.asarray(r, dtype=float)
    n = len(r)
    if n < 30 or np.std(r, ddof=1) == 0:
        return {"skipped": True, "reason": "insufficient observations"}
    stats = np.empty(n_boot)
    q = 1.0 / avg_block
    for b in range(n_boot):
        idx = np.empty(n, dtype=int)
        idx[0] = rng.integers(n)
        restart = rng.random(n) < q
        for t in range(1, n):
            idx[t] = rng.integers(n) if restart[t] else (idx[t - 1] + 1) % n
        s = r[idx]
        sd = np.std(s, ddof=1)
        stats[b] = np.mean(s) / sd * math.sqrt(p) if sd > 0 else 0.0
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return {
        "skipped": False, "n_boot": n_boot, "avg_block": avg_block,
        "sharpe_ci95": [round(float(lo), 4), round(float(hi), 4)],
        "p_sharpe_le_0": round(float(np.mean(stats <= 0)), 4),
    }


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _phi_inv(u: float) -> float:
    """Acklam-style rational approximation of the normal quantile (|err| < 1e-9)."""
    if not 0 < u < 1:
        raise ValueError("u in (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if u < plow:
        ql = math.sqrt(-2 * math.log(u))
        return (((((c[0] * ql + c[1]) * ql + c[2]) * ql + c[3]) * ql + c[4]) * ql + c[5]) / \
               ((((d[0] * ql + d[1]) * ql + d[2]) * ql + d[3]) * ql + 1)
    if u > phigh:
        ql = math.sqrt(-2 * math.log(1 - u))
        return -(((((c[0] * ql + c[1]) * ql + c[2]) * ql + c[3]) * ql + c[4]) * ql + c[5]) / \
               ((((d[0] * ql + d[1]) * ql + d[2]) * ql + d[3]) * ql + 1)
    ql = u - 0.5
    r = ql * ql
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * ql / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def deflated_sharpe(r: np.ndarray, p: int, trials: int) -> dict:
    """Bailey & López de Prado Deflated Sharpe Ratio.

    Answers: given that `trials` variants were tried, what is the probability
    that THIS Sharpe is above the maximum expected from pure noise?
    """
    r = np.asarray(r, dtype=float)
    n = len(r)
    sd = np.std(r, ddof=1)
    if n < 30 or sd == 0:
        return {"skipped": True, "reason": "insufficient observations"}
    sr_per = float(np.mean(r) / sd)                    # per-period Sharpe
    mean, std = float(np.mean(r)), sd
    g3 = float(np.mean(((r - mean) / std) ** 3))
    g4 = float(np.mean(((r - mean) / std) ** 4))
    trials = max(1, int(trials))
    if trials == 1:
        sr0 = 0.0
    else:
        sr0 = math.sqrt(1.0 / n) * (
            (1 - EULER_GAMMA) * _phi_inv(1 - 1.0 / trials)
            + EULER_GAMMA * _phi_inv(1 - 1.0 / (trials * math.e))
        )
    denom = math.sqrt(max(1e-12, 1 - g3 * sr_per + (g4 - 1) / 4 * sr_per ** 2))
    z = (sr_per - sr0) * math.sqrt(n - 1) / denom
    dsr = _phi(z)
    return {
        "skipped": False, "trials": trials,
        "sharpe_annualized": round(sr_per * math.sqrt(p), 4),
        "noise_max_sharpe_annualized": round(sr0 * math.sqrt(p), 4),
        "dsr": round(dsr, 4),
    }


# ───────────────────────────── the gauntlet ──────────────────────────────────
def run_gauntlet(returns: pd.Series, *, weights: pd.DataFrame | None = None,
                 freq: str = "daily", trials: int = 1, split: float = 0.7,
                 seed: int = 7) -> dict:
    p = PERIODS[freq]
    r = returns.dropna().to_numpy(dtype=float)
    flags: list[dict] = []

    def flag(severity: str, code: str, detail: str):
        flags.append({"severity": severity, "code": code, "detail": detail})

    metrics = _ann(r, p)
    if not metrics:
        return {"verdict": "FAIL", "flags": [{"severity": "fail", "code": "no_data",
                                              "detail": "fewer than 2 return observations"}]}
    if metrics["observations"] < p:
        flag("warn", "short_history",
             f"only {metrics['observations']} obs (<1 year at {freq} frequency); every statistic is fragile")

    # 2 — cost ladder
    cost_ladder = []
    if weights is not None and len(weights) == len(r):
        tno = turnover_series(weights)
        for bps in COST_LADDER_BPS:
            net = r - tno * bps / 1e4
            m = _ann(net, p)
            cost_ladder.append({"cost_bps": bps, "sharpe": m["sharpe"], "cagr": m["cagr"]})
        metrics["avg_turnover"] = round(float(np.mean(tno)), 4)
        alive = [c for c in cost_ladder if not math.isnan(c["sharpe"]) and c["sharpe"] > 0]
        if cost_ladder[0]["sharpe"] > 0 and (len(alive) < 3):  # dies at/below 10 bps
            flag("fail", "cost_fragile",
                 "positive gross Sharpe does not survive a 10 bps per-turnover cost")
    else:
        flag("warn", "no_cost_check",
             "no weights supplied — turnover/cost ladder skipped; gross figures only")

    # 3 — split stability
    split_report: dict = {}
    n_is = int(len(r) * split)
    if n_is >= 30 and len(r) - n_is >= 30:
        m_is, m_oos = _ann(r[:n_is], p), _ann(r[n_is:], p)
        split_report = {"in_sample_sharpe": m_is["sharpe"], "out_of_sample_sharpe": m_oos["sharpe"],
                        "split": split}
        if m_is["sharpe"] > 0.5:
            decay = 1 - (m_oos["sharpe"] / m_is["sharpe"])
            split_report["sharpe_decay"] = round(float(decay), 4)
            if m_oos["sharpe"] <= 0:
                flag("fail", "oos_negative", "out-of-sample Sharpe <= 0 while in-sample looked good")
            elif decay > 0.5:
                flag("warn", "oos_decay", f"out-of-sample Sharpe decays {decay:.0%} vs in-sample")
    else:
        flag("warn", "no_split_check", "series too short for a meaningful IS/OOS split")

    # 4 — robustness
    boot = stationary_bootstrap_sharpe(r, p, seed=seed)
    if not boot.get("skipped"):
        if boot["p_sharpe_le_0"] > 0.10:
            flag("fail", "not_robust",
                 f"bootstrap p(Sharpe<=0) = {boot['p_sharpe_le_0']:.2%} — indistinguishable from zero")
        elif boot["p_sharpe_le_0"] > 0.05:
            flag("warn", "weak_robustness",
                 f"bootstrap p(Sharpe<=0) = {boot['p_sharpe_le_0']:.2%}")
    dsr = deflated_sharpe(r, p, trials)
    if not dsr.get("skipped") and trials > 1 and dsr["dsr"] < 0.95:
        flag("warn" if dsr["dsr"] >= 0.5 else "fail", "selection_bias",
             f"DSR {dsr['dsr']:.2f} after disclosing {trials} trials — "
             "the Sharpe is not clearly above the best-of-N noise expectation")

    severities = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")
    return {"verdict": verdict, "freq": freq, "metrics": metrics,
            "cost_ladder": cost_ladder, "split_stability": split_report,
            "bootstrap": boot, "deflated_sharpe": dsr, "flags": flags}


# ───────────────────────────── demo: genuine vs lucky ────────────────────────
def demo() -> int:
    """Same synthetic market, two strategies: a persistent edge and pure noise
    selected as best-of-200. The gauntlet must separate them."""
    rng = np.random.default_rng(42)
    n = 1500
    base = rng.normal(0.0002, 0.01, n)

    genuine = 0.00035 + 0.35 * np.roll(base, 1) * np.sign(np.roll(base, 1)) * 0.02 + rng.normal(0, 0.006, n)
    candidates = rng.normal(0.0, 0.01, (200, n))
    lucky = candidates[np.argmax(candidates[:, : n // 2].mean(axis=1))]

    print("═" * 68)
    print("DEMO — validation gauntlet: genuine edge vs best-of-200 noise")
    print("═" * 68)
    results = {}
    for name, r, trials in (("genuine_edge", genuine, 1), ("lucky_noise", lucky, 200)):
        rep = run_gauntlet(pd.Series(r), freq="daily", trials=trials)
        results[name] = rep
        print(f"\n▶ {name}  (disclosed trials: {trials})")
        m = rep["metrics"]
        print(f"  sharpe {m['sharpe']:+.2f} · maxDD {m['max_drawdown']:.1%} · "
              f"p(SR<=0) {rep['bootstrap'].get('p_sharpe_le_0', 'n/a')} · "
              f"DSR {rep['deflated_sharpe'].get('dsr', 'n/a')}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
        print(f"  VERDICT: {rep['verdict']}")
    ok = results["genuine_edge"]["verdict"] != "FAIL" and results["lucky_noise"]["verdict"] == "FAIL"
    print("\n" + ("demo OK — gauntlet separates signal from selection bias" if ok
                  else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Honest-backtest validation gauntlet")
    ap.add_argument("--returns", help="CSV: date,return")
    ap.add_argument("--weights", help="optional wide CSV: date + one column per asset")
    ap.add_argument("--freq", default="daily", choices=sorted(PERIODS))
    ap.add_argument("--trials", type=int, default=1,
                    help="number of strategy variants tried before this one")
    ap.add_argument("--split", type=float, default=0.7)
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()
    if not args.returns:
        ap.error("--returns is required (or use --demo)")

    rets = pd.read_csv(args.returns, parse_dates=["date"]).set_index("date")["return"]
    weights = None
    if args.weights:
        weights = pd.read_csv(args.weights, parse_dates=["date"]).set_index("date")
        weights = weights.reindex(rets.index)

    report = run_gauntlet(rets, weights=weights, freq=args.freq,
                          trials=args.trials, split=args.split)
    out = json.dumps(report, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 0 if report["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
