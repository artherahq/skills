#!/usr/bin/env python3
"""
validate_strategy_spec.py — the completion gate for generated strategies.

A strategy that exists only as prose is not a strategy; it is a mood. This
validator enforces the spec contract BEFORE any code is written or backtest is
run, so downstream skills receive something checkable:

  structure  : every required field present and typed (see references/spec-schema.md)
  risk       : at least one hard risk control (stop, weight cap, exposure cap,
               or drawdown halt) — "we'll be careful" does not parse
  costs      : an explicit cost assumption in bps; gross-only specs are refused
  honesty    : `variants_tried` disclosed (feeds backtest-validation's DSR);
               `pit_reviewed` acknowledged for the data requirements
  overfit    : parameter budget preflight — observations per free parameter
               (history × universe breadth vs parameter count); < 30 warns,
               < 10 fails before a single line of code is written
  language   : forbidden claims ("guaranteed", "risk-free", "稳赚", "保证收益")
               anywhere in the spec fail it outright

Exit 0 = spec is fit to implement (PASS or WARN). Exit 1 = fix the spec first.

Usage:
  python validate_strategy_spec.py SPEC.json
  python validate_strategy_spec.py --demo     # a passing spec and a broken one

Stdlib only — runs anywhere.
"""
from __future__ import annotations

import argparse
import json
import sys

ARCHETYPES = {
    "momentum", "mean_reversion", "multi_factor", "pairs_trading",
    "technical", "ml_enhanced", "event_driven", "value",
}
RISK_CONTROL_KEYS = {
    "stop_loss_pct", "max_position_weight", "max_gross_exposure", "max_drawdown_halt_pct",
}
FORBIDDEN = [
    "guaranteed", "guarantee", "risk-free", "riskfree", "sure win", "cannot lose",
    "稳赚", "保证收益", "无风险", "必涨", "稳定盈利保证",
]
REQUIRED = {
    "strategy_name": str, "archetype": str, "market": str, "universe": (list, str),
    "signal": dict, "risk_control": dict, "position_sizing": (dict, str),
    "costs_bps": (int, float), "data_requirements": dict,
    "variants_tried": int, "backtest_config": dict,
}


def _walk_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_strings(v)


def _count_params(signal: dict) -> int:
    """Free numeric parameters in the signal definition (lookbacks, thresholds…)."""
    n = 0
    for v in (signal.get("parameters") or {}).values():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            n += 1
        elif isinstance(v, (list, tuple)):
            n += sum(1 for x in v if isinstance(x, (int, float)) and not isinstance(x, bool))
    return n


def validate(spec: dict) -> dict:
    flags: list[dict] = []

    def flag(sev: str, code: str, detail: str):
        flags.append({"severity": sev, "code": code, "detail": detail})

    # structure
    for key, typ in REQUIRED.items():
        if key not in spec:
            flag("fail", "missing_field", f"required field `{key}` is absent")
        elif not isinstance(spec[key], typ):
            flag("fail", "wrong_type", f"`{key}` should be {typ}")
    if flags and any(f["code"] == "missing_field" for f in flags):
        return _verdict(flags)

    if spec["archetype"] not in ARCHETYPES:
        flag("fail", "unknown_archetype",
             f"`{spec['archetype']}` not in {sorted(ARCHETYPES)}")

    sig = spec.get("signal", {})
    for k in ("entry_logic", "exit_logic"):
        if not str(sig.get(k, "")).strip():
            flag("fail", "empty_signal", f"signal.{k} is empty — untestable")

    # risk
    rc = spec.get("risk_control", {})
    if not any(k in rc and rc[k] is not None for k in RISK_CONTROL_KEYS):
        flag("fail", "no_hard_risk_control",
             f"need at least one of {sorted(RISK_CONTROL_KEYS)} with a value")

    # costs
    costs = spec.get("costs_bps")
    if isinstance(costs, (int, float)) and costs <= 0:
        flag("fail", "gross_only",
             "costs_bps must be > 0 — a strategy speced without costs is speced to disappoint")

    # honesty
    trials = spec.get("variants_tried")
    if isinstance(trials, int) and trials < 1:
        flag("fail", "trials_undisclosed", "variants_tried must be >= 1 (this spec counts as one)")
    dr = spec.get("data_requirements", {})
    if "pit_reviewed" not in dr:
        flag("fail", "pit_unacknowledged",
             "data_requirements.pit_reviewed must be present (true, or false with a plan)")
    elif dr.get("pit_reviewed") is False:
        flag("warn", "pit_pending",
             "data pipeline not yet PIT-reviewed — run point-in-time-research before trusting the backtest")

    # overfit preflight
    n_params = _count_params(sig)
    history = int(dr.get("history_periods") or 0)
    universe = spec.get("universe")
    breadth = len(universe) if isinstance(universe, list) and universe else 1
    if n_params > 0 and history > 0:
        obs_per_param = history * breadth / n_params
        if obs_per_param < 10:
            flag("fail", "overfit_preflight",
                 f"{n_params} free parameters vs ~{history * breadth} observations "
                 f"({obs_per_param:.0f}/param) — curve-fitting by construction")
        elif obs_per_param < 30:
            flag("warn", "thin_data_budget",
                 f"{obs_per_param:.0f} observations per free parameter — keep variants_tried honest")
    elif n_params == 0:
        flag("warn", "no_declared_parameters",
             "signal.parameters is empty — either the strategy has none (fine) or they are hidden in prose (not fine)")

    # forbidden language
    for text in _walk_strings(spec):
        low = text.lower()
        for bad in FORBIDDEN:
            if bad in low:
                flag("fail", "forbidden_claim", f"contains {bad!r} — remove the claim, not the word order")
                break

    return _verdict(flags)


def _verdict(flags: list[dict]) -> dict:
    sevs = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in sevs else ("WARN" if "warn" in sevs else "PASS")
    return {"verdict": verdict, "flags": flags,
            "next_step": ("implement_then_backtest-validation" if verdict != "FAIL"
                          else "fix_spec")}


# ─────────────────────────── demo ───────────────────────────────────────────
GOOD_SPEC = {
    "strategy_name": "US Large-Cap 12-1 Momentum",
    "archetype": "momentum",
    "market": "US",
    "universe": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "AVGO", "TSLA"],
    "signal": {
        "entry_logic": "rank by trailing 252d return excluding last 21d; hold top quartile",
        "exit_logic": "monthly rebalance; drop names leaving the top quartile",
        "parameters": {"lookback": 252, "skip": 21, "quantile": 0.25},
    },
    "risk_control": {"max_position_weight": 0.20, "max_drawdown_halt_pct": 25},
    "position_sizing": {"method": "equal_weight_within_selection"},
    "costs_bps": 10,
    "data_requirements": {"history_periods": 756, "fields": ["adj_close"], "pit_reviewed": True},
    "variants_tried": 3,
    "backtest_config": {"freq": "daily", "split": 0.7},
    "status": "spec_only",
}

BAD_SPEC = {
    "strategy_name": "Guaranteed Crypto Wealth Machine",
    "archetype": "momentum",
    "market": "CRYPTO",
    "universe": ["BTC-USD"],
    "signal": {
        "entry_logic": "buy when 9 indicators align (see notes: guaranteed profit setup)",
        "exit_logic": "",
        "parameters": {f"p{i}": i * 3 + 2 for i in range(12)},
    },
    "risk_control": {"note": "we will be careful"},
    "position_sizing": "all-in",
    "costs_bps": 0,
    "data_requirements": {"history_periods": 90, "fields": ["close"]},
    "variants_tried": 0,
    "backtest_config": {"freq": "daily"},
}


def demo() -> int:
    print("═" * 68)
    print("DEMO — strategy spec gate: a disciplined spec vs a mood with charts")
    print("═" * 68)
    outcomes = {}
    for name, spec in (("disciplined_momentum", GOOD_SPEC), ("wealth_machine", BAD_SPEC)):
        rep = validate(spec)
        outcomes[name] = rep["verdict"]
        print(f"\n▶ {name}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
        if not rep["flags"]:
            print("  (no flags)")
        print(f"  VERDICT: {rep['verdict']}  →  {rep['next_step']}")
    ok = outcomes["disciplined_momentum"] == "PASS" and outcomes["wealth_machine"] == "FAIL"
    print("\n" + ("demo OK — the gate refuses moods and passes specs" if ok
                  else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Strategy spec completion gate")
    ap.add_argument("spec", nargs="?", help="path to SPEC.json")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)
    if args.demo:
        return demo()
    if not args.spec:
        ap.error("provide SPEC.json (or use --demo)")
    with open(args.spec) as f:
        spec = json.load(f)
    report = validate(spec)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
