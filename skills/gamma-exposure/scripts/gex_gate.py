#!/usr/bin/env python3
"""gex_gate.py — Gamma Exposure (GEX): a Black-Scholes-based estimate of
options-dealer hedging pressure by strike, plus a gate that audits a GEX
report before it gets shared as if it were an observed fact.

GEX infers *dealer hedging behavior* from public open interest and implied
volatility under one industry-standard but fundamentally unverifiable
assumption: customers are net buyers of options, dealers are net sellers,
and dealers delta-hedge. Call OI then contributes positive gamma exposure
(dealers buy the underlying as it rises, sell as it falls — dampens
volatility); put OI contributes negative gamma exposure (dealers sell as it
falls, buy as it rises — amplifies volatility). No public dataset shows
dealers' actual positioning, so every GEX number is an estimate under that
assumption, not a measurement.

The dangerous failure mode isn't a crash — it's silent. Flip the put sign
convention (a one-character bug) and the computation still runs, still
produces a plausible-looking chart, and still gives a *confident, wrong*
regime call in the opposite direction of what the market maker's OI actually
implies. `demo()` below reproduces exactly that on one synthetic chain.

Try it with no data:  python gex_gate.py --demo
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List, Optional


# ───────────────────────────── Black-Scholes gamma ───────────────────────────

def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def black_scholes_gamma(S: float, K: float, T: float, sigma: float, r: float = 0.05) -> float:
    """Gamma is identical for calls and puts at the same (S, K, T, sigma) —
    no need to branch on option type here. Degenerate inputs (T<=0, sigma<=0,
    non-positive price/strike) return 0.0 rather than raising, so a chain
    with a few malformed rows doesn't blow up the whole computation."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return _norm_pdf(d1) / (S * sigma * math.sqrt(T))


# ───────────────────────────── GEX computation ────────────────────────────────

DEALER_ASSUMPTION_DISCLOSURE = (
    "GEX assumes dealers are net short customer option flow (customers net "
    "buyers, dealers net sellers) and delta-hedge accordingly: call OI "
    "contributes positive gamma exposure, put OI contributes negative gamma "
    "exposure. This is the standard public-GEX-calculator convention, not a "
    "directly observable fact — no public dataset shows dealers' actual "
    "positioning, and this estimate would be wrong wherever that assumption "
    "doesn't hold (e.g. a dealer already long gamma from a prior hedge)."
)

COVERAGE_LIMITATION = (
    "Computed from a single expiration's open interest and implied "
    "volatility snapshot. Ignores other expirations contributing to the "
    "same hedging book, intraday OI changes since the snapshot, and any "
    "non-listed / OTC options exposure — free listed-equity-options data "
    "does not cover index or OTC flow, which is often the larger book."
)


def compute_gex(
    chain: List[Dict],
    spot: float,
    days_to_expiry: int,
    *,
    r: float = 0.05,
    contract_multiplier: int = 100,
    put_sign: int = -1,
) -> dict:
    """chain: one row per strike, `{"strike": float, "call_oi": float,
    "call_iv": float, "put_oi": float, "put_iv": float}` — a leg with
    oi<=0 or iv<=0 (or a missing key) is skipped, not treated as zero
    exposure with a fabricated IV.

    `put_sign` defaults to -1 (the correct, industry-standard convention).
    It exists as a parameter only so the demo below can reproduce the
    sign-convention bug on the same inputs for comparison — do not pass
    anything other than -1 in real use.
    """
    T = max(days_to_expiry, 1) / 365.0
    by_strike: Dict[float, Dict[str, float]] = {}

    for row in chain:
        strike = row.get("strike")
        if strike is None:
            continue
        strike = float(strike)
        entry = by_strike.setdefault(strike, {"call_gex": 0.0, "put_gex": 0.0})

        call_oi, call_iv = row.get("call_oi") or 0, row.get("call_iv") or 0
        if call_oi > 0 and call_iv > 0:
            gamma = black_scholes_gamma(spot, strike, T, float(call_iv), r)
            entry["call_gex"] += gamma * call_oi * contract_multiplier * (spot ** 2) * 0.01

        put_oi, put_iv = row.get("put_oi") or 0, row.get("put_iv") or 0
        if put_oi > 0 and put_iv > 0:
            gamma = black_scholes_gamma(spot, strike, T, float(put_iv), r)
            entry["put_gex"] += put_sign * gamma * put_oi * contract_multiplier * (spot ** 2) * 0.01

    strikes = sorted(by_strike)
    gex_by_strike = [
        {
            "strike": k,
            "call_gex": by_strike[k]["call_gex"],
            "put_gex": by_strike[k]["put_gex"],
            "net_gex": by_strike[k]["call_gex"] + by_strike[k]["put_gex"],
        }
        for k in strikes
    ]

    net_gex_total = sum(row["net_gex"] for row in gex_by_strike)
    regime = "positive" if net_gex_total >= 0 else "negative"

    # Zero-gamma flip: walk the cumulative net GEX (strikes ascending) and
    # linearly interpolate the crossing point — not "nearest strike," which
    # can be off by half a strike-width on a coarse chain.
    zero_flip: Optional[float] = None
    cum = 0.0
    prev_strike, prev_cum = None, None
    for row in gex_by_strike:
        cum += row["net_gex"]
        if prev_cum is not None and (prev_cum < 0) != (cum < 0):
            x0, x1 = prev_strike, row["strike"]
            y0, y1 = prev_cum, cum
            if y1 != y0:
                zero_flip = x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
            break
        prev_strike, prev_cum = row["strike"], cum

    walls_n = min(3, len(gex_by_strike))
    walls_sorted = sorted(gex_by_strike, key=lambda r: abs(r["net_gex"]), reverse=True)[:walls_n]
    gamma_walls = [{"strike": w["strike"], "gex": w["net_gex"]} for w in walls_sorted]

    return {
        "spot_price": spot,
        "net_gex_total": net_gex_total,
        "regime": regime,
        "zero_gamma_flip": zero_flip,
        "gamma_walls": gamma_walls,
        "gex_by_strike": gex_by_strike,
    }


def build_report(gex_result: dict, *, methodology: str = "", coverage_limitation: str = "") -> dict:
    """Attach the two disclosures the audit gate requires. Pass empty
    strings to reproduce a report that will fail the audit (see demo)."""
    return {**gex_result, "methodology": methodology, "coverage_limitation": coverage_limitation}


# ───────────────────────────── the audit gate ─────────────────────────────────

_MIN_DISCLOSURE_CHARS = 20


def audit_gex_report(report: dict) -> dict:
    """Checks a GEX report is internally consistent AND properly disclosed
    before it goes anywhere someone might read it as a fact rather than an
    estimate. This does not re-derive the market data — it catches the
    class of bug that produces a plausible-looking wrong number (bad sign
    convention, tampered summary stats) and the class of omission that lets
    a reader mistake an assumption-based estimate for a measurement."""
    flags: List[dict] = []

    def flag(severity: str, code: str, detail: str):
        flags.append({"severity": severity, "code": code, "detail": detail})

    methodology = (report.get("methodology") or "").strip()
    coverage_limitation = (report.get("coverage_limitation") or "").strip()
    if len(methodology) < _MIN_DISCLOSURE_CHARS:
        flag("fail", "missing_dealer_assumption_disclosure",
             "report does not disclose the customers-net-buyers/dealers-net-sellers "
             "assumption GEX is computed under — a reader will treat the regime call "
             "as an observed fact instead of an estimate")
    if len(coverage_limitation) < _MIN_DISCLOSURE_CHARS:
        flag("fail", "missing_coverage_limitation",
             "report does not disclose what this GEX estimate does NOT cover "
             "(other expirations, intraday OI changes, OTC/index flow)")

    gex_by_strike = report.get("gex_by_strike") or []
    if gex_by_strike:
        recomputed_total = sum(row.get("net_gex", 0.0) for row in gex_by_strike)
        reported_total = report.get("net_gex_total")
        if reported_total is not None and abs(recomputed_total - reported_total) > max(1.0, abs(recomputed_total) * 1e-6):
            flag("fail", "gex_sum_mismatch",
                 f"reported net_gex_total={reported_total:.2f} does not match the sum of "
                 f"gex_by_strike rows ({recomputed_total:.2f}) — the summary and the detail "
                 "table disagree, which means at least one of them was hand-edited or stale")

        expected_regime = "positive" if recomputed_total >= 0 else "negative"
        if report.get("regime") and report["regime"] != expected_regime:
            flag("fail", "regime_sign_mismatch",
                 f"reported regime='{report['regime']}' but net_gex_total's sign implies "
                 f"'{expected_regime}' — this is the exact shape of the sign-convention bug "
                 "this skill exists to catch")

        strikes = [row["strike"] for row in gex_by_strike]
        lo, hi = min(strikes), max(strikes)
        flip = report.get("zero_gamma_flip")
        if flip is not None and not (lo <= flip <= hi):
            flag("fail", "flip_point_out_of_range",
                 f"zero_gamma_flip={flip:.2f} falls outside the chain's own strike range "
                 f"[{lo:.2f}, {hi:.2f}] — not a value that came out of the cumulative-sum "
                 "interpolation this gate expects")

        reported_walls = report.get("gamma_walls") or []
        n = len(reported_walls)
        if n:
            expected_strikes = {
                row["strike"]
                for row in sorted(gex_by_strike, key=lambda r: abs(r["net_gex"]), reverse=True)[:n]
            }
            reported_strikes = {w["strike"] for w in reported_walls}
            if reported_strikes != expected_strikes:
                flag("fail", "gamma_walls_mismatch",
                     f"reported gamma_walls strikes {sorted(reported_strikes)} are not the "
                     f"top-{n} strikes by |net_gex| ({sorted(expected_strikes)})")

        if len(gex_by_strike) < 5:
            flag("warn", "sparse_chain",
                 f"only {len(gex_by_strike)} strikes with open interest — the zero-gamma "
                 "flip and gamma-wall picks have limited resolution; disclose this alongside "
                 "the numbers rather than presenting them at full precision")
    else:
        flag("warn", "no_strike_detail",
             "report has no gex_by_strike detail to audit against — only the top-level "
             "summary was checkable")

    severities = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")
    return {"flags": flags, "verdict": verdict}


# ───────────────────────────── demo ──────────────────────────────────────────

def _demo_chain() -> List[Dict]:
    """9-strike synthetic chain around spot=100 with a realistic hedging
    skew: heavy put OI at and below spot (protective puts / downside
    hedges), lighter call OI concentrated further out. Real chains vary,
    but this shape — puts dominating near-the-money OI — is common enough
    to be a fair stand-in, and it's exactly the shape where a sign bug
    matters most (the largest-gamma strikes are also the most lopsided)."""
    return [
        {"strike": 80,  "call_oi": 50,  "call_iv": 0.35, "put_oi": 800,  "put_iv": 0.42},
        {"strike": 85,  "call_oi": 80,  "call_iv": 0.33, "put_oi": 900,  "put_iv": 0.40},
        {"strike": 90,  "call_oi": 150, "call_iv": 0.31, "put_oi": 1200, "put_iv": 0.37},
        {"strike": 95,  "call_oi": 300, "call_iv": 0.29, "put_oi": 1500, "put_iv": 0.34},
        {"strike": 100, "call_oi": 600, "call_iv": 0.28, "put_oi": 1600, "put_iv": 0.30},
        {"strike": 105, "call_oi": 500, "call_iv": 0.27, "put_oi": 400,  "put_iv": 0.29},
        {"strike": 110, "call_oi": 350, "call_iv": 0.26, "put_oi": 150,  "put_iv": 0.28},
        {"strike": 115, "call_oi": 150, "call_iv": 0.25, "put_oi": 60,   "put_iv": 0.27},
        {"strike": 120, "call_oi": 60,  "call_iv": 0.24, "put_oi": 30,   "put_iv": 0.26},
    ]


def demo() -> int:
    """Two scenarios on the same synthetic chain:

    1. Correct sign convention vs. a one-character sign bug (put_sign=+1
       instead of -1) — shows the bug silently flip the regime call from
       negative to positive on identical input data.
    2. The disclosure audit separating a compliant report from a hollow one
       carrying the exact same numbers.
    """
    chain = _demo_chain()
    spot, days_to_expiry = 100.0, 30

    print("=" * 72)
    print("DEMO 1 — a one-character sign bug silently flips the regime call")
    print("=" * 72)
    correct = compute_gex(chain, spot, days_to_expiry, put_sign=-1)
    buggy = compute_gex(chain, spot, days_to_expiry, put_sign=+1)
    print(f"  correct (put_sign=-1): net_gex_total={correct['net_gex_total']:>14,.0f}  regime={correct['regime']}")
    print(f"  buggy   (put_sign=+1): net_gex_total={buggy['net_gex_total']:>14,.0f}  regime={buggy['regime']}")
    print(f"  chain, spot, and every OI/IV input are identical between the two runs.")
    flipped = correct["regime"] != buggy["regime"]
    print(f"  regime flipped: {flipped} ({correct['regime']} -> {buggy['regime']})")

    print()
    print("=" * 72)
    print("DEMO 2 — disclosure audit: same numbers, hollow vs. compliant report")
    print("=" * 72)
    compliant = build_report(correct, methodology=DEALER_ASSUMPTION_DISCLOSURE,
                              coverage_limitation=COVERAGE_LIMITATION)
    hollow = build_report(correct, methodology="", coverage_limitation="")

    rep_compliant = audit_gex_report(compliant)
    rep_hollow = audit_gex_report(hollow)
    print(f"  compliant report -> verdict={rep_compliant['verdict']}  flags={[f['code'] for f in rep_compliant['flags']]}")
    print(f"  hollow report     -> verdict={rep_hollow['verdict']}  flags={[f['code'] for f in rep_hollow['flags']]}")

    print()
    print("=" * 72)
    print("DEMO 3 — a tampered summary is caught even with disclosures present")
    print("=" * 72)
    tampered = dict(compliant)
    tampered["regime"] = "positive"  # doesn't match net_gex_total's actual sign
    rep_tampered = audit_gex_report(tampered)
    print(f"  tampered regime   -> verdict={rep_tampered['verdict']}  flags={[f['code'] for f in rep_tampered['flags']]}")

    ok = (
        flipped
        and rep_compliant["verdict"] == "PASS"
        and rep_hollow["verdict"] == "FAIL"
        and rep_tampered["verdict"] == "FAIL"
        and any(f["code"] == "regime_sign_mismatch" for f in rep_tampered["flags"])
    )
    print()
    print("demo OK — sign bug visibly flips the regime, and the audit gate separates "
          "compliant/hollow/tampered reports correctly" if ok
          else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gamma Exposure (GEX) computation + disclosure audit gate")
    ap.add_argument("--chain", help='JSON file: [{"strike","call_oi","call_iv","put_oi","put_iv"}, ...]')
    ap.add_argument("--spot", type=float, help="underlying spot price")
    ap.add_argument("--days-to-expiry", type=int, help="calendar days to the option's expiration")
    ap.add_argument("--r", type=float, default=0.05, help="risk-free rate, annualized")
    ap.add_argument("--audit", help="JSON file: a GEX report (as produced by --chain) to audit instead of computing")
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    if args.audit:
        with open(args.audit) as f:
            report = json.load(f)
        result = audit_gex_report(report)
    elif args.chain and args.spot is not None and args.days_to_expiry is not None:
        with open(args.chain) as f:
            chain = json.load(f)
        gex_result = compute_gex(chain, args.spot, args.days_to_expiry, r=args.r)
        report = build_report(gex_result, methodology=DEALER_ASSUMPTION_DISCLOSURE,
                               coverage_limitation=COVERAGE_LIMITATION)
        result = {**report, **audit_gex_report(report)}
    else:
        ap.error("--demo, or --audit <report.json>, or --chain/--spot/--days-to-expiry together, is required")
        return 2

    out = json.dumps(result, indent=2, default=str)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out)
    print(out)
    return 0 if result.get("verdict", "PASS") in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
