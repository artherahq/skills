#!/usr/bin/env python3
"""
factor_evaluate.py — is this factor real, or noise wearing a rank?

Evaluates a cross-sectional factor panel against forward returns with the
checks an allocator actually asks about, computed one way:

  1  IC series      : per-period cross-sectional Spearman rank IC vs the NEXT
                      period's return; mean IC, IC-IR (mean/std), t-stat,
                      hit rate. Rank IC, not Pearson — factors are orderings.
  2  Decay          : mean IC at 1/5/10/21-period horizons. An edge that only
                      exists at horizon 1 with high factor turnover is a cost
                      donation (hand the survivor to backtest-validation).
  3  Quantile spread: mean next-period return per factor quintile, Q5−Q1
                      long-short spread (annualized), and monotonicity — a
                      real factor orders the middle, not just the extremes.
  4  Stability      : first-half vs second-half mean IC (sign flips kill), and
                      factor rank autocorrelation (turnover proxy).

Verdict: valid / valid_but_moderate / weak / invalid — with the flag list that
produced it. Exit 0 for the first two, 1 for weak/invalid, so completion gates
can enforce "no strategy built on an invalid factor".

PIT WARNING: this harness evaluates the panel it is given. If factor values
embed look-ahead (restated fundamentals, period-end dating), the IC is fiction
— run the point-in-time-research skill on the data pipeline first.

Inputs:
  --factor   long CSV: date,symbol,value   (factor as-of each date, PIT-clean)
  --returns  wide CSV: date + one column of periodic simple returns per symbol
  --freq     daily|weekly|monthly (default daily; sets annualization + horizons)
  --json     write the machine-readable report here

Try it with no data:  python factor_evaluate.py --demo
The demo evaluates a genuinely predictive factor and a pure-noise factor on
the same synthetic universe — the second must come out invalid.

Depends only on pandas + numpy; Spearman and t-stats implemented inline.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

PERIODS = {"daily": 252, "weekly": 52, "monthly": 12}
HORIZONS = {"daily": [1, 5, 10, 21], "weekly": [1, 2, 4, 8], "monthly": [1, 2, 3, 6]}
N_QUANTILES = 5


# ─────────────────────────── inline stats ───────────────────────────────────
def _rank(a: np.ndarray) -> np.ndarray:
    """Average ranks (ties averaged), 1-based."""
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1, dtype=float)
    # average ties
    vals, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    if len(vals) != len(a):
        sums = np.zeros(len(vals))
        np.add.at(sums, inv, ranks)
        ranks = (sums / counts)[inv]
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra, rb = _rank(a), _rank(b)
    sa, sb = np.std(ra), np.std(rb)
    if sa == 0 or sb == 0:
        return float("nan")
    return float(np.mean((ra - ra.mean()) * (rb - rb.mean())) / (sa * sb))


def t_stat(series: np.ndarray) -> float:
    s = series[~np.isnan(series)]
    if len(s) < 3 or np.std(s, ddof=1) == 0:
        return float("nan")
    return float(np.mean(s) / (np.std(s, ddof=1) / math.sqrt(len(s))))


# ─────────────────────────── panel alignment ────────────────────────────────
def align_panel(factor: pd.DataFrame, returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """factor(long: date,symbol,value) → wide, aligned with returns on shared
    dates/symbols. Factor at t is scored against returns at t+h (shifted later)."""
    wide = factor.pivot_table(index="date", columns="symbol", values="value", aggfunc="last")
    symbols = [s for s in wide.columns if s in returns.columns]
    dates = wide.index.intersection(returns.index)
    return wide.loc[dates, symbols], returns.loc[dates, symbols]


def ic_series(fwide: pd.DataFrame, rets: pd.DataFrame, horizon: int) -> pd.Series:
    """Per-date Spearman IC of factor(t) vs cumulative return over (t, t+h]."""
    fwd = (1 + rets).rolling(horizon).apply(np.prod, raw=True).shift(-horizon) - 1
    out = {}
    for dt in fwide.index:
        f = fwide.loc[dt]
        r = fwd.loc[dt] if dt in fwd.index else None
        if r is None:
            continue
        mask = f.notna() & r.notna()
        if mask.sum() >= 5:
            out[dt] = spearman(f[mask].to_numpy(), r[mask].to_numpy())
    return pd.Series(out, dtype=float).dropna()


def quantile_spread(fwide: pd.DataFrame, rets: pd.DataFrame, p: int) -> dict:
    """Mean next-period return per factor quintile; Q5−Q1 annualized spread."""
    fwd = rets.shift(-1)
    buckets = {q: [] for q in range(1, N_QUANTILES + 1)}
    for dt in fwide.index:
        f = fwide.loc[dt]
        r = fwd.loc[dt] if dt in fwd.index else None
        if r is None:
            continue
        mask = f.notna() & r.notna()
        if mask.sum() < N_QUANTILES * 2:
            continue
        fq = f[mask]
        try:
            labels = pd.qcut(fq.rank(method="first"), N_QUANTILES, labels=False) + 1
        except ValueError:
            continue
        for q in range(1, N_QUANTILES + 1):
            sel = labels == q
            if sel.any():
                buckets[q].append(float(r[mask][sel.to_numpy()].mean()))
    means = {q: (float(np.mean(v)) if v else float("nan")) for q, v in buckets.items()}
    ordered = [means[q] for q in range(1, N_QUANTILES + 1)]
    diffs = np.diff(ordered)
    monotone_share = float(np.mean(diffs > 0)) if not any(math.isnan(x) for x in ordered) else float("nan")
    spread = ordered[-1] - ordered[0] if not any(math.isnan(x) for x in (ordered[0], ordered[-1])) else float("nan")
    return {
        "quantile_mean_returns": {f"Q{q}": round(means[q], 6) for q in means},
        "long_short_spread_annualized": round(spread * p, 4) if not math.isnan(spread) else None,
        "monotone_share": round(monotone_share, 2) if not math.isnan(monotone_share) else None,
    }


def rank_autocorr(fwide: pd.DataFrame) -> float:
    """Mean period-to-period Spearman of factor ranks — 1 = static, low = churny."""
    vals = []
    idx = fwide.index
    for a, b in zip(idx[:-1], idx[1:]):
        f0, f1 = fwide.loc[a], fwide.loc[b]
        mask = f0.notna() & f1.notna()
        if mask.sum() >= 5:
            vals.append(spearman(f0[mask].to_numpy(), f1[mask].to_numpy()))
    return float(np.nanmean(vals)) if vals else float("nan")


# ─────────────────────────── evaluation ─────────────────────────────────────
def evaluate(factor: pd.DataFrame, returns: pd.DataFrame, *, freq: str = "daily") -> dict:
    p = PERIODS[freq]
    fwide, rets = align_panel(factor, returns)
    if fwide.shape[0] < 30 or fwide.shape[1] < 5:
        return {"judgement": "invalid",
                "flags": [{"severity": "fail", "code": "insufficient_panel",
                           "detail": f"{fwide.shape[0]} dates × {fwide.shape[1]} symbols; "
                                     "need ≥30 dates and ≥5 symbols"}]}

    ic1 = ic_series(fwide, rets, 1)
    mean_ic = float(ic1.mean())
    ic_ir = float(mean_ic / ic1.std(ddof=1)) if ic1.std(ddof=1) > 0 else float("nan")
    decay = {}
    for h in HORIZONS[freq]:
        s = ic_series(fwide, rets, h)
        if len(s):
            decay[f"h{h}"] = round(float(s.mean()), 4)

    q = quantile_spread(fwide, rets, p)
    ac = rank_autocorr(fwide)

    half = len(ic1) // 2
    ic_a, ic_b = float(ic1.iloc[:half].mean()), float(ic1.iloc[half:].mean())

    flags: list[dict] = []
    def flag(sev: str, code: str, detail: str):
        flags.append({"severity": sev, "code": code, "detail": detail})

    sign = 1 if mean_ic >= 0 else -1
    if abs(mean_ic) < 0.02:
        flag("fail", "no_signal", f"|mean IC| = {abs(mean_ic):.4f} < 0.02 — indistinguishable from noise")
    elif abs(mean_ic) < 0.03:
        flag("warn", "weak_signal", f"|mean IC| = {abs(mean_ic):.4f} — thin edge, costs will matter")
    if not math.isnan(ic_ir) and abs(ic_ir) < 0.30 and abs(mean_ic) >= 0.02:
        flag("warn", "inconsistent_ic", f"IC-IR {ic_ir:.2f} — the mean hides wild swings")
    if len(ic1) >= 60 and ic_a * ic_b < 0 and max(abs(ic_a), abs(ic_b)) > 0.02:
        flag("fail", "sign_flip", f"IC flips sign between halves ({ic_a:+.3f} → {ic_b:+.3f})")
    if q["monotone_share"] is not None and sign > 0 and q["monotone_share"] < 0.5:
        flag("warn", "non_monotone",
             f"only {q['monotone_share']:.0%} of adjacent quantile steps are ordered — extremes-only factor")
    if not math.isnan(ac) and ac < 0.5 and abs(mean_ic) >= 0.02:
        flag("warn", "high_turnover",
             f"factor rank autocorrelation {ac:.2f} — churny; net-of-cost viability must go through backtest-validation")

    severities = [f["severity"] for f in flags]
    if "fail" in severities:
        judgement = "invalid" if any(f["code"] == "no_signal" for f in flags) else "weak"
    elif severities.count("warn") >= 2:
        judgement = "valid_but_moderate"
    elif severities:
        judgement = "valid_but_moderate"
    else:
        judgement = "valid"

    return {
        "judgement": judgement,
        "ic": {
            "mean": round(mean_ic, 4), "ir": round(ic_ir, 4) if not math.isnan(ic_ir) else None,
            "t_stat": round(t_stat(ic1.to_numpy()), 2),
            "hit_rate": round(float((ic1 * sign > 0).mean()), 4),
            "periods": int(len(ic1)),
            "first_half": round(ic_a, 4), "second_half": round(ic_b, 4),
        },
        "decay": decay,
        "quantiles": q,
        "rank_autocorrelation": round(ac, 4) if not math.isnan(ac) else None,
        "flags": flags,
        "next_step": ("backtest-validation" if judgement in ("valid", "valid_but_moderate")
                      else "discard_or_redesign"),
    }


# ─────────────────────────── demo ───────────────────────────────────────────
def demo() -> int:
    """Same synthetic universe; a genuinely predictive factor vs pure noise."""
    rng = np.random.default_rng(23)
    n_dates, n_sym = 300, 40
    idx = pd.bdate_range("2024-01-02", periods=n_dates)
    symbols = [f"S{i:02d}" for i in range(n_sym)]

    signal = rng.normal(0, 1, (n_dates, n_sym))
    noise_r = rng.normal(0, 0.02, (n_dates, n_sym))
    rets = pd.DataFrame(0.004 * np.vstack([np.zeros((1, n_sym)), signal[:-1]]) + noise_r,
                        index=idx, columns=symbols)

    def to_long(mat):
        df = pd.DataFrame(mat, index=idx, columns=symbols)
        return df.stack().rename("value").rename_axis(["date", "symbol"]).reset_index()

    genuine = to_long(signal)                                   # 真:今天的因子驱动明天的收益
    noise = to_long(rng.normal(0, 1, (n_dates, n_sym)))          # 假:与收益无关的排序

    print("═" * 68)
    print("DEMO — factor evaluation: predictive factor vs pure-noise factor")
    print("═" * 68)
    outcomes = {}
    for name, panel in (("genuine_factor", genuine), ("noise_factor", noise)):
        rep = evaluate(panel, rets, freq="daily")
        outcomes[name] = rep["judgement"]
        ic = rep.get("ic", {})
        print(f"\n▶ {name}")
        if ic:
            print(f"  IC {ic['mean']:+.3f} · IR {ic['ir']} · t {ic['t_stat']} · hit {ic['hit_rate']:.0%} · "
                  f"Q5-Q1 {rep['quantiles']['long_short_spread_annualized']}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
        print(f"  JUDGEMENT: {rep['judgement']}  →  next: {rep['next_step']}")
    ok = outcomes["genuine_factor"] in ("valid", "valid_but_moderate") and \
         outcomes["noise_factor"] == "invalid"
    print("\n" + ("demo OK — IC discipline separates prediction from ranking noise"
                  if ok else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cross-sectional factor evaluation")
    ap.add_argument("--factor", help="long CSV: date,symbol,value")
    ap.add_argument("--returns", help="wide CSV: date + one return column per symbol")
    ap.add_argument("--freq", default="daily", choices=sorted(PERIODS))
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()
    if not (args.factor and args.returns):
        ap.error("--factor and --returns are required (or use --demo)")

    factor = pd.read_csv(args.factor, parse_dates=["date"])
    rets = pd.read_csv(args.returns, parse_dates=["date"]).set_index("date")
    report = evaluate(factor, rets, freq=args.freq)
    out = json.dumps(report, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 0 if report["judgement"] in ("valid", "valid_but_moderate") else 1


if __name__ == "__main__":
    sys.exit(main())
