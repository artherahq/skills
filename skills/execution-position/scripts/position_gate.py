#!/usr/bin/env python3
"""
position_gate.py — the pre-trade gate: signal → size → risk checks → paper intent.

Converts "I want to buy X" into either a sized, cost-estimated PAPER order
intent, or a refusal with reasons. The gate's job is to be the boring adult:

  sizing     : volatility-target (weight = risk budget / asset vol) or
               fractional Kelly — Kelly ONLY from a user-declared edge
               (win rate + payoff), never from sample means, and always
               capped at fraction <= 0.25. Full Kelly on estimated edges is
               how accounts die.
  risk gates : per-position weight cap · gross exposure cap · cash
               sufficiency · stop-distance sanity (a stop inside ~1 daily
               sigma is a noise stop) · liquidity vs ADV when volume data
               is provided (skipped honestly otherwise).
  costs      : commission + spread + linear impact, labeled as an estimate.
  authority  : output intents are `paper_only: true`. Any request for live
               execution FAILS the gate — live orders are a human decision
               outside this skill.

Exit 0 = PASS/WARN (intent emitted). Exit 1 = FAIL (blocked, with reasons).

Input: a single JSON file (see references/order-schema.md):
  order      symbol, side, price, stop_price?, sizing{method,...}
  portfolio  equity, cash, positions{symbol: weight}
  limits     max_position_weight, max_gross_exposure, min_cash_pct?
  market     ann_vol? (or supply --history CSV), adv_shares?, spread_bps?

Try it with no data:  python position_gate.py --demo
The demo gates a disciplined vol-targeted entry (PASS) against a YOLO
all-in with a noise stop (FAIL).

Stdlib + optional pandas/numpy only when --history is used.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

KELLY_CAP = 0.25
COMMISSION_BPS_DEFAULT = 5.0
IMPACT_BPS_PER_1PCT_ADV = 2.0   # linear placeholder, labeled estimate


# ─────────────────────────── sizing ─────────────────────────────────────────
def size_vol_target(risk_budget_pct: float, ann_vol: float) -> float:
    """Weight such that position contributes ~risk_budget of annual portfolio risk."""
    if ann_vol <= 0:
        raise ValueError("ann_vol must be > 0 for vol-target sizing")
    return risk_budget_pct / ann_vol


def size_kelly(win_rate: float, payoff_ratio: float, fraction: float = 0.25) -> float:
    """Fractional Kelly from a DECLARED edge: f* = p - (1-p)/b, then scaled.

    The declared edge is the user's claim, not a computed fact — the report
    carries it verbatim so the claim stays auditable.
    """
    if not (0 < win_rate < 1) or payoff_ratio <= 0:
        raise ValueError("win_rate in (0,1) and payoff_ratio > 0 required")
    f_star = win_rate - (1 - win_rate) / payoff_ratio
    frac = min(fraction, KELLY_CAP)
    return max(0.0, f_star * frac)


# ─────────────────────────── gate ───────────────────────────────────────────
def run_gate(spec: dict, *, ann_vol_override: float | None = None) -> dict:
    flags: list[dict] = []

    def flag(sev: str, code: str, detail: str):
        flags.append({"severity": sev, "code": code, "detail": detail})

    order = spec.get("order") or {}
    pf = spec.get("portfolio") or {}
    limits = spec.get("limits") or {}
    market = spec.get("market") or {}

    for k in ("symbol", "side", "price"):
        if not order.get(k):
            flag("fail", "missing_order_field", f"order.{k} is required")
    if str(order.get("execution", "paper")).lower() == "live":
        flag("fail", "live_execution_refused",
             "this gate emits paper intents only — live execution is a human decision")
    equity = float(pf.get("equity") or 0)
    if equity <= 0:
        flag("fail", "no_equity", "portfolio.equity must be > 0")
    if any(f["severity"] == "fail" for f in flags):
        return _verdict(flags, None)

    price = float(order["price"])
    side = str(order["side"]).lower()
    ann_vol = ann_vol_override if ann_vol_override is not None else market.get("ann_vol")

    # sizing
    sizing = order.get("sizing") or {}
    method = str(sizing.get("method", "vol_target"))
    kelly_note = None
    try:
        if method == "vol_target":
            if not ann_vol:
                flag("fail", "no_volatility",
                     "vol_target sizing needs market.ann_vol or --history — refusing to guess")
                return _verdict(flags, None)
            weight = size_vol_target(float(sizing.get("risk_budget_pct", 0.02)), float(ann_vol))
        elif method == "kelly":
            wr, pr = sizing.get("win_rate"), sizing.get("payoff_ratio")
            if wr is None or pr is None:
                flag("fail", "kelly_without_declared_edge",
                     "kelly sizing requires a DECLARED win_rate and payoff_ratio — "
                     "computing an edge from sample means is not permitted here")
                return _verdict(flags, None)
            frac = float(sizing.get("fraction", KELLY_CAP))
            if frac > KELLY_CAP:
                flag("warn", "kelly_fraction_capped",
                     f"requested fraction {frac} capped at {KELLY_CAP} — full Kelly on an "
                     "estimated edge over-bets by construction")
            weight = size_kelly(float(wr), float(pr), frac)
            kelly_note = {"declared_win_rate": wr, "declared_payoff_ratio": pr}
            if weight == 0.0:
                flag("fail", "negative_edge", "declared edge is non-positive — no position")
                return _verdict(flags, None)
        elif method == "fixed_weight":
            weight = float(sizing.get("weight", 0))
        else:
            flag("fail", "unknown_sizing", f"method {method!r} not in vol_target/kelly/fixed_weight")
            return _verdict(flags, None)
    except ValueError as exc:
        flag("fail", "sizing_error", str(exc))
        return _verdict(flags, None)

    # risk gates
    max_w = float(limits.get("max_position_weight", 0.20))
    if weight > max_w:
        flag("warn", "position_capped", f"sized weight {weight:.1%} capped at limit {max_w:.1%}")
        weight = max_w

    positions = {k: float(v) for k, v in (pf.get("positions") or {}).items()}
    current_w = positions.get(order["symbol"], 0.0)
    target_w = current_w + weight if side == "buy" else current_w - weight
    if abs(target_w) > max_w + 1e-9:
        flag("fail", "position_limit",
             f"target weight {target_w:.1%} in {order['symbol']} exceeds cap {max_w:.1%} "
             f"(already holding {current_w:.1%})")

    gross_after = sum(abs(v) for k, v in positions.items() if k != order["symbol"]) + abs(target_w)
    max_gross = float(limits.get("max_gross_exposure", 1.0))
    if gross_after > max_gross + 1e-9:
        flag("fail", "gross_exposure_limit",
             f"gross exposure after trade {gross_after:.1%} exceeds cap {max_gross:.1%}")

    notional = weight * equity
    if side == "buy":
        cash = float(pf.get("cash") or 0)
        min_cash = float(limits.get("min_cash_pct", 0.0)) * equity
        if notional > cash - min_cash:
            flag("fail", "insufficient_cash",
                 f"needs {notional:,.0f} but only {max(0.0, cash - min_cash):,.0f} available "
                 "above the cash floor")

    # stop-distance sanity: a stop inside ~1 daily sigma is noise, not protection
    stop = order.get("stop_price")
    if stop is not None and ann_vol:
        daily_sigma = float(ann_vol) / math.sqrt(252)
        stop_dist = abs(price - float(stop)) / price
        if stop_dist < daily_sigma:
            flag("warn", "noise_stop",
                 f"stop distance {stop_dist:.2%} is inside one daily sigma ({daily_sigma:.2%}) — "
                 "it will trigger on noise, not on thesis failure")
    elif stop is None:
        flag("warn", "no_stop", "no stop_price declared — exit discipline undefined")

    # liquidity
    adv = market.get("adv_shares")
    shares = notional / price if price > 0 else 0.0
    liquidity = {"skipped": True, "reason": "no market.adv_shares supplied"}
    if adv:
        pct_adv = shares / float(adv)
        liquidity = {"skipped": False, "order_pct_of_adv": round(pct_adv * 100, 3)}
        if pct_adv > 0.10:
            flag("fail", "liquidity_limit",
                 f"order is {pct_adv:.1%} of ADV — exiting would move the market against you")
        elif pct_adv > 0.02:
            flag("warn", "liquidity_notable", f"order is {pct_adv:.1%} of ADV")

    # cost estimate (labeled)
    spread_bps = float(market.get("spread_bps", 5.0))
    commission_bps = float(market.get("commission_bps", COMMISSION_BPS_DEFAULT))
    impact_bps = 0.0
    if adv and shares:
        impact_bps = IMPACT_BPS_PER_1PCT_ADV * (shares / float(adv)) * 100
    total_bps = commission_bps + spread_bps / 2 + impact_bps
    cost = {
        "commission_bps": commission_bps, "half_spread_bps": spread_bps / 2,
        "impact_bps_estimate": round(impact_bps, 2),
        "total_bps_estimate": round(total_bps, 2),
        "estimated_cost": round(notional * total_bps / 1e4, 2),
        "note": "linear estimate; real impact is convex in size and regime-dependent",
    }

    intent = {
        "paper_only": True,
        "symbol": order["symbol"], "side": side,
        "target_weight": round(target_w, 4),
        "delta_weight": round(weight if side == "buy" else -weight, 4),
        "notional": round(notional, 2),
        "shares_approx": round(shares, 2),
        "sizing_method": method,
        **({"kelly_inputs": kelly_note} if kelly_note else {}),
    }
    return _verdict(flags, intent, liquidity=liquidity, cost=cost)


def _verdict(flags, intent, **extra) -> dict:
    sevs = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in sevs else ("WARN" if "warn" in sevs else "PASS")
    out = {"verdict": verdict, "flags": flags,
           "intent": intent if verdict != "FAIL" else None}
    out.update(extra)
    if intent and verdict != "FAIL":
        out["disclosure"] = [
            "Paper intent only — no live order is implied or authorized.",
            "Cost figures are estimates; declared Kelly edges are the user's claim, carried verbatim.",
        ]
    return out


# ─────────────────────────── demo ───────────────────────────────────────────
GOOD = {
    "order": {"symbol": "AAPL", "side": "buy", "price": 230.0, "stop_price": 216.0,
              "sizing": {"method": "vol_target", "risk_budget_pct": 0.02}},
    "portfolio": {"equity": 100_000, "cash": 40_000,
                  "positions": {"MSFT": 0.20, "NVDA": 0.15}},
    "limits": {"max_position_weight": 0.20, "max_gross_exposure": 1.0, "min_cash_pct": 0.05},
    "market": {"ann_vol": 0.28, "adv_shares": 50_000_000, "spread_bps": 2},
}
YOLO = {
    "order": {"symbol": "MEME", "side": "buy", "price": 4.20, "stop_price": 4.15,
              "execution": "live",
              "sizing": {"method": "kelly", "win_rate": 0.9, "payoff_ratio": 5, "fraction": 1.0}},
    "portfolio": {"equity": 100_000, "cash": 100_000, "positions": {}},
    "limits": {"max_position_weight": 0.20, "max_gross_exposure": 1.0},
    "market": {"ann_vol": 1.2, "adv_shares": 80_000},
}


def demo() -> int:
    print("═" * 68)
    print("DEMO — pre-trade gate: disciplined entry vs YOLO")
    print("═" * 68)
    results = {}
    for name, spec in (("disciplined_entry", GOOD), ("yolo", YOLO)):
        rep = run_gate(spec)
        results[name] = rep["verdict"]
        print(f"\n▶ {name}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
        if rep.get("intent"):
            i = rep["intent"]
            print(f"  intent: {i['side']} {i['symbol']} Δw {i['delta_weight']:+.1%} "
                  f"(~{i['notional']:,.0f}) · paper_only={i['paper_only']} · "
                  f"est cost {rep['cost']['total_bps_estimate']} bps")
        print(f"  VERDICT: {rep['verdict']}")
    ok = results["disciplined_entry"] in ("PASS", "WARN") and results["yolo"] == "FAIL"
    print("\n" + ("demo OK — the gate sizes discipline and refuses YOLO" if ok
                  else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pre-trade position gate (paper intents only)")
    ap.add_argument("spec", nargs="?", help="path to order+portfolio+limits JSON")
    ap.add_argument("--history", help="optional CSV date,close to compute ann_vol")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)
    if args.demo:
        return demo()
    if not args.spec:
        ap.error("provide the spec JSON (or use --demo)")
    with open(args.spec) as f:
        spec = json.load(f)
    vol = None
    if args.history:
        import numpy as np
        import pandas as pd
        px = pd.read_csv(args.history, parse_dates=["date"]).set_index("date")["close"]
        r = px.pct_change().dropna().to_numpy()
        vol = float(np.std(r, ddof=1) * math.sqrt(252))
    report = run_gate(spec, ann_vol_override=vol)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
