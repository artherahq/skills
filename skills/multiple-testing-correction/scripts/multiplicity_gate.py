#!/usr/bin/env python3
"""multiplicity_gate.py — multiple-testing correction (Bonferroni / Benjamini-
Hochberg FDR) for a batch of significance tests, plus a Fundamental Law of
Active Management (Grinold 1989, IR ~= IC * sqrt(Breadth)) check for whether
"many independent signals" is actually "few correlated bets wearing a
disguise."

Both problems share one root cause: judging a portfolio of tests (or a
portfolio of bets) by single-test arithmetic. Test 20 factors at the 5%
level and ~1 will look significant from pure noise alone — no factor did
anything. Claim 20 "independent" signals and size conviction by
sqrt(20) — if they actually share 70% pairwise correlation because they're
the same model family, the true breadth is closer to 3.

Try it with no data:  python multiplicity_gate.py --demo
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, Optional

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ───────────────────────────── p-values ──────────────────────────────────────

def t_stat_to_pvalue(t_stat: float, df: int) -> float:
    """Two-sided p-value from a t-statistic. Uses the t distribution (exact
    for small samples; converges to the normal as df grows) rather than
    always assuming normality — a small-sample study shouldn't borrow a
    large-sample distribution's confidence."""
    if df <= 0:
        return 1.0
    if HAS_SCIPY:
        return float(2 * (1 - stats.t.cdf(abs(t_stat), df=df)))
    # Normal-approximation fallback so this degrades instead of hard-failing
    # when scipy isn't installed — fine for df large enough that t ~ normal.
    return float(2 * (1 - _phi(abs(t_stat))))


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ───────────────────────────── corrections ───────────────────────────────────

def bonferroni_correction(p_values: Dict[str, float], alpha: float = 0.05) -> Dict[str, bool]:
    """Threshold alpha/n. Most conservative: controls P(at least one false
    positive across the whole batch) <= alpha (family-wise error rate)."""
    n = len(p_values)
    if n == 0:
        return {}
    threshold = alpha / n
    return {name: (p <= threshold) for name, p in p_values.items()}


def benjamini_hochberg_correction(p_values: Dict[str, float], alpha: float = 0.05) -> Dict[str, bool]:
    """Standard BH step-up procedure. Sort p-values ascending; find the
    largest k where p_(k) <= (k/n)*alpha; reject the null for the k smallest.
    Controls the *expected proportion* of false positives among the results
    called significant (FDR), not the probability of any false positive at
    all — less conservative than Bonferroni, and the more common choice in
    modern quant research (it's the same "don't let batch size buy you false
    confidence" logic behind Bailey & Lopez de Prado's Deflated Sharpe
    Ratio, which this catalog's backtest-validation skill uses for the
    single-strategy-selection version of this problem)."""
    n = len(p_values)
    if n == 0:
        return {}
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    rejected = {name: False for name, _ in items}

    threshold_k = -1
    for k in range(n, 0, -1):
        _, p = items[k - 1]
        if p <= (k / n) * alpha:
            threshold_k = k
            break

    if threshold_k > 0:
        for name, _ in items[:threshold_k]:
            rejected[name] = True
    return rejected


# ───────────────────────────── breadth / Fundamental Law ─────────────────────

def effective_breadth(n_bets: int, avg_pairwise_correlation: float) -> float:
    """Effective number of independent bets from N nominal bets sharing an
    average pairwise correlation rho: N_eff = N / (1 + (N-1)*rho). rho=0
    returns N unchanged (truly independent bets); rho=1 collapses to 1 (they
    are all the same bet wearing N costumes). This is the standard
    diversification-ratio formula — the same shape risk-assessment's
    "effective N" concentration metric uses, applied here to bet count
    instead of position weight."""
    if n_bets <= 0:
        return 0.0
    rho = max(0.0, min(1.0, avg_pairwise_correlation))
    return n_bets / (1 + (n_bets - 1) * rho)


def fundamental_law_ir(ic: float, breadth: float) -> float:
    """Grinold (1989): Information Ratio ~= Information Coefficient * sqrt(Breadth).
    This is a theoretical ceiling under optimal weighting, not a promise —
    label it as such wherever it's reported."""
    if breadth <= 0:
        return 0.0
    return ic * math.sqrt(breadth)


# ───────────────────────────── the gate ──────────────────────────────────────

def run_gate(
    test_results: Dict[str, dict],
    *,
    alpha: float = 0.05,
    naive_t_threshold: float = 2.0,
    ic: Optional[float] = None,
    n_bets: Optional[int] = None,
    avg_pairwise_correlation: Optional[float] = None,
) -> dict:
    """test_results: {name: {"t_stat": float, "n_periods": int}, ...} — one
    entry per hypothesis actually tested (factor, strategy variant, sub-
    period, whatever the batch is). n_periods is the sample size backing
    that specific t-stat; df = n_periods - 1.

    ic / n_bets / avg_pairwise_correlation are optional and independent of
    the correction above — supply them to also get a breadth-illusion check.
    """
    flags: list[dict] = []

    def flag(severity: str, code: str, detail: str):
        flags.append({"severity": severity, "code": code, "detail": detail})

    p_values: Dict[str, float] = {}
    naive_significant: Dict[str, bool] = {}
    for name, r in test_results.items():
        t_stat, n_periods = r.get("t_stat"), r.get("n_periods")
        if t_stat is None or not n_periods:
            continue
        p_values[name] = t_stat_to_pvalue(t_stat, df=n_periods - 1)
        naive_significant[name] = abs(t_stat) >= naive_t_threshold

    n = len(p_values)
    result: dict = {"n_tests": n, "alpha": alpha}

    if n == 1:
        flag("warn", "insufficient_batch",
             "exactly 1 test supplied — multiplicity correction has nothing to correct; "
             "a single test's naive threshold is the right call here")
        bonferroni, bh = {}, {}
    elif n == 0:
        # Caller isn't running the multiplicity-correction half at all (e.g. a
        # breadth-only call) — nothing to flag, this is a legitimate no-op.
        bonferroni, bh = {}, {}
    else:
        bonferroni = bonferroni_correction(p_values, alpha=alpha)
        bh = benjamini_hochberg_correction(p_values, alpha=alpha)

        naive_count = sum(naive_significant.values())
        bonferroni_count = sum(bonferroni.values())
        bh_count = sum(bh.values())

        result["naive_significant_count"] = naive_count
        result["bonferroni_significant_count"] = bonferroni_count
        result["bh_fdr_significant_count"] = bh_count

        if naive_count > 0 and bh_count == 0:
            flag("fail", "significance_evaporates",
                 f"naive |t|>={naive_t_threshold} flagged {naive_count}/{n} as significant; "
                 f"zero survive BH-FDR correction at alpha={alpha} — this batch's apparent "
                 "significance is consistent with pure noise at this batch size")
        elif naive_count > bh_count:
            flag("warn", "correction_reduced_significant_set",
                 f"naive flagged {naive_count}/{n}, BH-FDR keeps {bh_count} — "
                 f"proceed only with the BH-FDR survivors: "
                 f"{sorted(k for k, v in bh.items() if v)}")

    result["per_test"] = {
        name: {
            "t_stat": test_results[name]["t_stat"],
            "p_value": round(p_values[name], 6) if name in p_values else None,
            "naive_significant": naive_significant.get(name, False),
            "significant_bonferroni": bool(bonferroni.get(name, False)),
            "significant_bh_fdr": bool(bh.get(name, False)),
        }
        for name in test_results
    }

    # ── breadth / Fundamental Law (independent of the correction above) ──
    if ic is not None and n_bets is not None and avg_pairwise_correlation is not None:
        nominal_breadth = float(n_bets)
        eff_breadth = effective_breadth(n_bets, avg_pairwise_correlation)
        ir_nominal = fundamental_law_ir(ic, nominal_breadth)
        ir_effective = fundamental_law_ir(ic, eff_breadth)
        result["breadth"] = {
            "ic": ic, "n_bets": n_bets, "avg_pairwise_correlation": avg_pairwise_correlation,
            "nominal_breadth": nominal_breadth,
            "effective_breadth": round(eff_breadth, 2),
            "ir_nominal_theoretical": round(ir_nominal, 4),
            "ir_effective_theoretical": round(ir_effective, 4),
        }
        if nominal_breadth > 0 and eff_breadth / nominal_breadth < 0.5:
            inflation = ir_nominal / ir_effective if ir_effective > 0 else float("inf")
            flag("warn", "breadth_illusion",
                 f"{n_bets} nominal bets at rho={avg_pairwise_correlation:.2f} average correlation "
                 f"collapse to {eff_breadth:.1f} effective bets — treating them as independent "
                 f"overstates the Fundamental-Law IR ceiling by {inflation:.1f}x")

    severities = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")
    result["flags"] = flags
    result["verdict"] = verdict
    return result


# ───────────────────────────── demo ──────────────────────────────────────────

def demo() -> int:
    """Two scenarios in one batch, on the same synthetic data generator, so
    the gate's separating power is visible rather than asserted:

    1. 30 factors, ALL pure noise (zero true effect). Naive |t|>=2 will
       still flag a handful "significant" by chance alone — that's the
       whole point of running 30 tests at a 5%-per-test threshold. BH-FDR
       should flag close to zero.
    2. 20 "independent" trading signals that are actually 70%-correlated
       (same model family) — shows the Fundamental-Law IR ceiling collapsing
       once breadth is corrected for that correlation.
    """
    if not HAS_NUMPY:
        print("numpy not installed — skipping demo (would need it for synthetic data)")
        return 0

    rng = np.random.default_rng(28)

    print("=" * 72)
    print("DEMO 1 — 30 pure-noise factors: naive threshold vs BH-FDR")
    print("=" * 72)
    n_periods = 240
    test_results = {}
    for i in range(30):
        # True effect is exactly zero for every one of these — any "signal"
        # found is definitionally a false positive.
        sample = rng.normal(0.0, 1.0, n_periods)
        mean, se = float(np.mean(sample)), float(np.std(sample, ddof=1) / math.sqrt(n_periods))
        t_stat = mean / se if se > 0 else 0.0
        test_results[f"factor_{i:02d}"] = {"t_stat": t_stat, "n_periods": n_periods}

    rep1 = run_gate(test_results, alpha=0.05)
    print(f"  naive |t|>=2.0 flagged:     {rep1['naive_significant_count']} / {rep1['n_tests']}")
    print(f"  Bonferroni-significant:    {rep1['bonferroni_significant_count']} / {rep1['n_tests']}")
    print(f"  BH-FDR-significant:        {rep1['bh_fdr_significant_count']} / {rep1['n_tests']}")
    for f in rep1["flags"]:
        print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
    print(f"  VERDICT: {rep1['verdict']}")

    print()
    print("=" * 72)
    print("DEMO 2 — 20 nominally-independent bets at 70% pairwise correlation")
    print("=" * 72)
    ic, n_bets, rho = 0.04, 20, 0.7
    rep2 = run_gate({}, ic=ic, n_bets=n_bets, avg_pairwise_correlation=rho)
    b = rep2["breadth"]
    print(f"  IC={ic}, nominal breadth={b['nominal_breadth']:.0f}, "
          f"effective breadth={b['effective_breadth']:.1f} (rho={rho})")
    print(f"  Fundamental Law IR if treated as independent: {b['ir_nominal_theoretical']:.3f}")
    print(f"  Fundamental Law IR corrected for correlation:  {b['ir_effective_theoretical']:.3f}")
    for f in rep2["flags"]:
        print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")

    ok = (
        rep1["naive_significant_count"] > rep1["bh_fdr_significant_count"]
        and any(f["code"] == "breadth_illusion" for f in rep2["flags"])
    )
    print()
    print("demo OK — correction visibly shrinks the noise batch's 'significant' count, "
          "and the breadth check catches the correlated-bets illusion" if ok
          else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Multiple-testing correction + Fundamental Law breadth gate")
    ap.add_argument("--tests", help='JSON file: {"name": {"t_stat": float, "n_periods": int}, ...}')
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--naive-t-threshold", type=float, default=2.0)
    ap.add_argument("--ic", type=float, help="average information coefficient, for the breadth check")
    ap.add_argument("--n-bets", type=int, help="nominal number of independent bets/signals")
    ap.add_argument("--avg-corr", type=float, help="average pairwise correlation among those bets")
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()
    if not args.tests and args.ic is None:
        ap.error("--tests (or --demo) is required; --ic/--n-bets/--avg-corr are optional add-ons")

    test_results = {}
    if args.tests:
        with open(args.tests) as f:
            test_results = json.load(f)

    report = run_gate(
        test_results, alpha=args.alpha, naive_t_threshold=args.naive_t_threshold,
        ic=args.ic, n_bets=args.n_bets, avg_pairwise_correlation=args.avg_corr,
    )
    out = json.dumps(report, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 0 if report["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
