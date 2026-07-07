#!/usr/bin/env python3
"""
risk_profile.py — portfolio risk decomposition on the portfolio's OWN history.

Answers "how risky is this, and where does the risk come from?" with numbers a
risk committee would accept, and refuses to invent what the data cannot show:

  1  Core metrics    : annualized vol, historical VaR95/99, CVaR95, max
                       drawdown + longest underwater stretch, worst day/month.
  2  Concentration   : top-weight share, HHI, effective number of positions.
  3  Diversification : average pairwise correlation, diversification ratio —
                       ten highly-correlated names are one position in disguise.
  4  Tail shape      : skew, excess kurtosis, Cornish–Fisher adjusted VaR.
  5  Stress          : (a) historical replay — the portfolio's own worst 5-day
                       and worst-month windows; (b) linear beta shock vs the
                       supplied benchmark for −10% / −20% market moves. With no
                       benchmark the beta shock is SKIPPED and said so — no
                       fabricated correlations.

Output: machine-readable JSON with `risk_level` (low / medium / medium_high /
high), the flag list that produced it, and `disclosure` lines that MUST be
surfaced with any conclusion. Exit 1 only on unusable inputs.

Inputs:
  --returns  wide CSV: date + one column of periodic simple returns per asset
  --weights  CSV: symbol,weight  (long-only or long/short; will be re-normalized
             by gross exposure and the normalization disclosed)
  --benchmark optional CSV: date,return — enables beta and the shock table
  --freq     daily|weekly|monthly (default daily)

Try it with no data:  python risk_profile.py --demo
The demo contrasts a 60%-in-one-name correlated tech book with an equal-weight
diversified book on the same history window.

Depends only on pandas + numpy; every statistic implemented inline.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

PERIODS = {"daily": 252, "weekly": 52, "monthly": 12}


# ─────────────────────────── portfolio assembly ─────────────────────────────
def portfolio_returns(returns: pd.DataFrame, weights: pd.Series) -> tuple[pd.Series, dict]:
    """Static-weight portfolio series; re-normalizes by gross exposure and
    discloses the adjustment instead of silently assuming it."""
    common = [c for c in returns.columns if c in weights.index]
    missing = [s for s in weights.index if s not in returns.columns]
    w = weights.loc[common].astype(float)
    gross = float(np.abs(w).sum())
    note = {}
    if not math.isclose(gross, 1.0, rel_tol=1e-3) and gross > 0:
        w = w / gross
        note["weights_renormalized_from_gross"] = round(gross, 4)
    if missing:
        note["symbols_without_history"] = missing
    port = (returns[common] * w).sum(axis=1)
    return port.dropna(), note


# ─────────────────────────── core statistics ────────────────────────────────
def var_cvar(r: np.ndarray, level: float) -> tuple[float, float]:
    """Historical VaR/CVaR at `level` (e.g. 0.95) — losses are negative numbers."""
    q = float(np.quantile(r, 1 - level))
    tail = r[r <= q]
    cvar = float(tail.mean()) if len(tail) else q
    return q, cvar

def cornish_fisher_var(r: np.ndarray, level: float) -> float:
    """CF-adjusted parametric VaR — lets skew/kurtosis widen the tail honestly."""
    z = {0.95: -1.6449, 0.99: -2.3263}[level]
    mu, sd = float(np.mean(r)), float(np.std(r, ddof=1))
    if sd == 0:
        return 0.0
    s = float(np.mean(((r - mu) / sd) ** 3))
    k = float(np.mean(((r - mu) / sd) ** 4)) - 3
    zcf = z + (z * z - 1) * s / 6 + (z ** 3 - 3 * z) * k / 24 - (2 * z ** 3 - 5 * z) * s * s / 36
    return float(mu + zcf * sd)

def drawdown_stats(r: np.ndarray) -> dict:
    equity = np.cumprod(1 + r)
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1
    under = dd < 0
    longest = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        longest = max(longest, cur)
    return {"max_drawdown": round(float(dd.min()), 6),
            "longest_underwater_periods": int(longest)}

def worst_windows(r: pd.Series, p: int) -> dict:
    five = r.rolling(5).apply(lambda x: float(np.prod(1 + x) - 1), raw=True)
    month = r.rolling(max(2, p // 12)).apply(lambda x: float(np.prod(1 + x) - 1), raw=True)
    out = {}
    if five.notna().any():
        i = five.idxmin()
        out["worst_5p_window"] = {"end": str(i)[:10], "return": round(float(five.min()), 6)}
    if month.notna().any():
        i = month.idxmin()
        out["worst_month_window"] = {"end": str(i)[:10], "return": round(float(month.min()), 6)}
    return out


# ─────────────────────────── concentration / diversification ────────────────
def concentration(weights: pd.Series) -> dict:
    w = np.abs(weights.to_numpy(dtype=float))
    w = w / w.sum() if w.sum() > 0 else w
    hhi = float(np.sum(w ** 2))
    return {
        "top_position": {"symbol": str(weights.abs().idxmax()), "share": round(float(w.max()), 4)},
        "hhi": round(hhi, 4),
        "effective_n": round(1.0 / hhi, 2) if hhi > 0 else 0.0,
        "positions": int(len(w)),
    }

def diversification(returns: pd.DataFrame, weights: pd.Series) -> dict:
    common = [c for c in returns.columns if c in weights.index]
    if len(common) < 2:
        return {"skipped": True, "reason": "fewer than 2 positions with history"}
    sub = returns[common].dropna()
    corr = sub.corr().to_numpy()
    n = corr.shape[0]
    avg_corr = float((corr.sum() - n) / (n * (n - 1)))
    w = np.abs(weights.loc[common].to_numpy(dtype=float))
    w = w / w.sum()
    vols = sub.std(ddof=1).to_numpy()
    port_vol = float(np.sqrt(w @ sub.cov().to_numpy() @ w))
    dr = float((w @ vols) / port_vol) if port_vol > 0 else float("nan")
    return {"avg_pairwise_corr": round(avg_corr, 4),
            "diversification_ratio": round(dr, 4)}


# ─────────────────────────── stress ─────────────────────────────────────────
def beta_and_shocks(port: pd.Series, benchmark: pd.Series | None) -> dict:
    if benchmark is None:
        return {"skipped": True,
                "reason": "no benchmark supplied — beta shock table omitted (not fabricated)"}
    joined = pd.concat([port, benchmark], axis=1, join="inner").dropna()
    if len(joined) < 60:
        return {"skipped": True, "reason": "fewer than 60 overlapping observations"}
    pr, br = joined.iloc[:, 0].to_numpy(), joined.iloc[:, 1].to_numpy()
    var_b = float(np.var(br, ddof=1))
    beta = float(np.cov(pr, br, ddof=1)[0, 1] / var_b) if var_b > 0 else float("nan")
    shocks = {f"market_{int(s*100)}pct": round(beta * s, 4) for s in (-0.10, -0.20)}
    return {"skipped": False, "beta": round(beta, 4), "linear_shock_estimate": shocks,
            "note": "linear beta approximation; real crashes raise correlations beyond it"}


# ─────────────────────────── verdict ────────────────────────────────────────
def assess(returns: pd.DataFrame, weights: pd.Series, *,
           benchmark: pd.Series | None = None, freq: str = "daily") -> dict:
    p = PERIODS[freq]
    port, notes = portfolio_returns(returns, weights)
    if len(port) < 30:
        return {"risk_level": "unknown", "error": "fewer than 30 portfolio observations",
                "notes": notes}

    r = port.to_numpy(dtype=float)
    vol = float(np.std(r, ddof=1) * math.sqrt(p))
    var95, cvar95 = var_cvar(r, 0.95)
    var99, _ = var_cvar(r, 0.99)
    mu, sd = float(np.mean(r)), float(np.std(r, ddof=1))
    skew = float(np.mean(((r - mu) / sd) ** 3)) if sd > 0 else 0.0
    ekurt = (float(np.mean(((r - mu) / sd) ** 4)) - 3) if sd > 0 else 0.0

    conc = concentration(weights)
    div = diversification(returns, weights)
    dd = drawdown_stats(r)

    flags: list[dict] = []
    def flag(sev: str, code: str, detail: str):
        flags.append({"severity": sev, "code": code, "detail": detail})

    if conc["top_position"]["share"] > 0.5:
        flag("high", "single_name_concentration",
             f"{conc['top_position']['symbol']} is {conc['top_position']['share']:.0%} of gross exposure")
    elif conc["top_position"]["share"] > 0.3:
        flag("medium", "concentration",
             f"top position {conc['top_position']['symbol']} at {conc['top_position']['share']:.0%}")
    if conc["effective_n"] < 3 and conc["positions"] >= 3:
        flag("medium", "low_effective_n",
             f"{conc['positions']} positions behave like {conc['effective_n']} (HHI)")
    if not div.get("skipped") and div["avg_pairwise_corr"] > 0.7:
        flag("high", "diversification_illusion",
             f"avg pairwise correlation {div['avg_pairwise_corr']:.2f} — the book is one bet in disguise")
    if vol > 0.35:
        flag("high", "high_volatility", f"annualized volatility {vol:.0%}")
    elif vol > 0.20:
        flag("medium", "elevated_volatility", f"annualized volatility {vol:.0%}")
    if dd["max_drawdown"] < -0.30:
        flag("high", "deep_drawdown", f"max drawdown {dd['max_drawdown']:.0%} in the sample")
    if ekurt > 3 or skew < -1:
        flag("medium", "fat_tails",
             f"skew {skew:.2f}, excess kurtosis {ekurt:.2f} — normal-VaR understates the tail")

    highs = sum(1 for f in flags if f["severity"] == "high")
    meds = sum(1 for f in flags if f["severity"] == "medium")
    risk_level = ("high" if highs >= 2 else
                  "medium_high" if highs == 1 else
                  "medium" if meds >= 2 else
                  "low_medium" if meds == 1 else "low")

    main_source = flags[0]["code"] if flags else "none_detected"
    return {
        "risk_level": risk_level,
        "main_risk_source": main_source,
        "metrics": {
            "annualized_volatility": round(vol, 4),
            "var_95": round(var95, 6), "var_99": round(var99, 6),
            "cvar_95": round(cvar95, 6),
            "cornish_fisher_var_95": round(cornish_fisher_var(r, 0.95), 6),
            "skew": round(skew, 4), "excess_kurtosis": round(ekurt, 4),
            **dd,
        },
        "worst_windows": worst_windows(port, p),
        "concentration": conc,
        "diversification": div,
        "stress": beta_and_shocks(port, benchmark),
        "flags": flags,
        "notes": notes,
        "disclosure": [
            "All figures are computed from the supplied history window only; they describe the past, not a guarantee about the future.",
            "Historical VaR/CVaR understate risks the sample never contained.",
            "This is research output, not individualized investment advice.",
        ],
    }


# ─────────────────────────── demo ───────────────────────────────────────────
def demo() -> int:
    """Concentrated correlated tech book vs equal-weight diversified book,
    same history window — risk levels must separate."""
    rng = np.random.default_rng(11)
    n = 750
    idx = pd.bdate_range("2023-01-02", periods=n)
    market = rng.normal(0.0004, 0.01, n)
    tech_factor = rng.normal(0.0003, 0.014, n)

    def asset(beta_m, beta_t, iv):
        return beta_m * market + beta_t * tech_factor + rng.normal(0, iv, n)

    rets = pd.DataFrame({
        "MEGA":  asset(1.0, 1.3, 0.006),
        "CHIP":  asset(1.1, 1.4, 0.008),
        "SAAS":  asset(0.9, 1.2, 0.009),
        "UTIL":  asset(0.4, 0.0, 0.006),
        "BOND":  rng.normal(0.0001, 0.003, n),
        "GOLD":  rng.normal(0.0002, 0.008, n) - 0.15 * market,
    }, index=idx)
    bench = pd.Series(market, index=idx)

    books = {
        "concentrated_tech": pd.Series({"MEGA": 0.60, "CHIP": 0.25, "SAAS": 0.15}),
        "diversified":       pd.Series({"MEGA": 0.20, "CHIP": 0.15, "SAAS": 0.15,
                                        "UTIL": 0.20, "BOND": 0.20, "GOLD": 0.10}),
    }
    print("═" * 68)
    print("DEMO — risk profile: concentrated tech book vs diversified book")
    print("═" * 68)
    levels = {}
    for name, w in books.items():
        rep = assess(rets, w, benchmark=bench)
        levels[name] = rep["risk_level"]
        m = rep["metrics"]
        print(f"\n▶ {name}")
        print(f"  vol {m['annualized_volatility']:.1%} · VaR95 {m['var_95']:.2%} · "
              f"CVaR95 {m['cvar_95']:.2%} · maxDD {m['max_drawdown']:.1%} · "
              f"effN {rep['concentration']['effective_n']}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():6}] {f['code']}: {f['detail']}")
        print(f"  RISK LEVEL: {rep['risk_level']}")
    order = ["low", "low_medium", "medium", "medium_high", "high"]
    ok = order.index(levels["concentrated_tech"]) > order.index(levels["diversified"])
    print("\n" + ("demo OK — concentration and correlation are visible in the verdict"
                  if ok else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Portfolio risk decomposition")
    ap.add_argument("--returns", help="wide CSV: date + one return column per asset")
    ap.add_argument("--weights", help="CSV: symbol,weight")
    ap.add_argument("--benchmark", help="optional CSV: date,return")
    ap.add_argument("--freq", default="daily", choices=sorted(PERIODS))
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()
    if not (args.returns and args.weights):
        ap.error("--returns and --weights are required (or use --demo)")

    rets = pd.read_csv(args.returns, parse_dates=["date"]).set_index("date")
    wdf = pd.read_csv(args.weights)
    weights = pd.Series(wdf["weight"].to_numpy(dtype=float), index=wdf["symbol"].astype(str))
    bench = None
    if args.benchmark:
        bench = pd.read_csv(args.benchmark, parse_dates=["date"]).set_index("date")["return"]

    report = assess(rets, weights, benchmark=bench, freq=args.freq)
    out = json.dumps(report, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 1 if report.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
