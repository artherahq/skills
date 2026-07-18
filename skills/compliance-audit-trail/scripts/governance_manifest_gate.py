#!/usr/bin/env python3
"""
governance_manifest_gate.py — the due-diligence gate for a model/strategy
governance manifest.

An institutional counterparty's due-diligence questions are always some
variant of: how is the model validated, is risk control actually running, is
the data trustworthy, and where are the boundaries. A prose writeup answering
these is worth nothing if the claims aren't checkable — this validates a
structured manifest (see references/manifest-schema.md) against exactly the
gaps that make a governance document unconvincing to someone doing real
due diligence:

  evidence     : every capability claim needs a pointer (code path, test,
                 metric) — an unevidenced claim is a bare assertion, not
                 disclosure
  scope        : an asset/strategy listed as "production" must have actually
                 passed every gate the manifest itself declares required —
                 "a model file exists for this symbol" is not the same claim
                 as "this symbol passed the full validation pipeline"
  safety       : a risk control (circuit breaker, drawdown halt, stale-model
                 check, ...) declared present but never verified to actually
                 trigger is a documentation exercise, not risk management —
                 code existing and code running are different claims
  audit trail  : decisions need a persisted log; "we could reconstruct this
                 if asked" is not an audit trail
  disclosure   : an honest system has known limitations. A manifest with an
                 EMPTY limitations list is a stronger red flag than one with
                 several — it means either nothing was found, or something
                 was, and was left out

Exit 0 = manifest is fit to hand to a counterparty (PASS or WARN).
Exit 1 = fix the manifest (or the system) first.

Usage:
  python governance_manifest_gate.py MANIFEST.json
  python governance_manifest_gate.py --demo     # a disclosed manifest vs a hollow one

Stdlib only — runs anywhere.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta

REQUIRED_TOP_LEVEL = {
    "system_name": str, "as_of": str, "capability_claims": list,
    "production_scope": list, "required_gates": list,
    "risk_controls": list, "audit_trail": dict, "compliance_checks": list,
    "known_limitations": list,
}


def _parse_date(s: str):
    try:
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def validate(manifest: dict, *, staleness_days: int = 90) -> dict:
    flags: list[dict] = []

    def flag(sev: str, code: str, detail: str):
        flags.append({"severity": sev, "code": code, "detail": detail})

    for key, typ in REQUIRED_TOP_LEVEL.items():
        if key not in manifest:
            flag("fail", "missing_field", f"required field `{key}` is absent")
        elif not isinstance(manifest[key], typ):
            flag("fail", "wrong_type", f"`{key}` should be {typ.__name__}")
    if any(f["code"] == "missing_field" for f in flags):
        return _verdict(flags)

    # ── evidence: every capability claim must be checkable ──
    for i, claim in enumerate(manifest["capability_claims"]):
        evidence = str(claim.get("evidence", "")).strip()
        text = str(claim.get("claim", f"claim[{i}]"))
        if not evidence:
            flag("fail", "unverifiable_claim", f"{text!r} has no evidence pointer")

    # ── scope: production assets must clear every required gate ──
    required_gates = set(manifest["required_gates"])
    for entry in manifest["production_scope"]:
        asset = entry.get("asset", "<unnamed>")
        passed = set(entry.get("passed_gates", []))
        missing = required_gates - passed
        if missing:
            flag("fail", "production_scope_gate_missing",
                 f"{asset} is listed as production scope but missing gates: {sorted(missing)}")

    # ── safety: declared risk controls must show verified-triggering evidence ──
    for rc in manifest["risk_controls"]:
        name = rc.get("name", "<unnamed control>")
        if not rc.get("declared_present"):
            continue
        if not rc.get("verified_triggering"):
            flag("fail", "unverified_safety_mechanism",
                 f"{name!r} is declared present but not verified to actually trigger — "
                 "code existing is not the same claim as risk management running")
        elif not str(rc.get("evidence", "")).strip():
            flag("warn", "safety_evidence_thin",
                 f"{name!r} claims verified triggering with no evidence pointer")

    # ── audit trail ──
    at = manifest["audit_trail"]
    if not at.get("decision_log_exists"):
        flag("fail", "no_audit_trail",
             "audit_trail.decision_log_exists is false/absent — decisions must be persisted, "
             "not reconstructible-if-asked")
    elif not str(at.get("evidence", "")).strip():
        flag("warn", "audit_trail_evidence_thin", "decision log claimed but no evidence pointer given")

    # ── compliance checks ──
    for check in manifest["compliance_checks"]:
        if not check.get("implemented"):
            flag("warn", "compliance_gap",
                 f"{check.get('name', '<unnamed check>')} is declared but not implemented")

    # ── disclosure: an empty limitations list is a red flag, not a clean bill of health ──
    if len(manifest["known_limitations"]) == 0:
        flag("warn", "no_limitations_disclosed",
             "known_limitations is empty — every real system has boundaries; "
             "an empty list more often means omission than perfection")

    # ── staleness: a governance doc that never gets updated goes stale ──
    as_of = _parse_date(manifest.get("as_of", ""))
    if as_of is not None:
        age_days = (datetime.now() - as_of).days
        if age_days > staleness_days:
            flag("warn", "stale_manifest",
                 f"as_of is {age_days} days old (> {staleness_days}-day threshold) — "
                 "re-verify claims still hold before handing this to a counterparty")
    else:
        flag("warn", "unparseable_as_of", "as_of is not an ISO date — cannot check staleness")

    return _verdict(flags)


def _verdict(flags: list[dict]) -> dict:
    sevs = {f["severity"] for f in flags}
    verdict = "FAIL" if "fail" in sevs else ("WARN" if "warn" in sevs else "PASS")
    return {"verdict": verdict, "flags": flags,
            "next_step": ("fit_to_share" if verdict != "FAIL" else "fix_manifest_or_system")}


# ─────────────────────────── demo ───────────────────────────────────────────
DISCLOSED_MANIFEST = {
    "system_name": "Example Quant Signal Pipeline",
    "as_of": datetime.now().date().isoformat(),
    "capability_claims": [
        {"claim": "walk-forward training, no random k-fold",
         "evidence": "trainer.py:WalkForwardTrainer"},
        {"claim": "HAC-corrected significance test on production signals",
         "evidence": "jobs/test_production_signal_significance.py"},
    ],
    "required_gates": ["ic_significance", "backtest_gate", "hac_test"],
    "production_scope": [
        {"asset": "AAPL", "passed_gates": ["ic_significance", "backtest_gate", "hac_test"]},
    ],
    "risk_controls": [
        {"name": "account_drawdown_circuit_breaker", "declared_present": True,
         "verified_triggering": True,
         "evidence": "integration test: NAV report -> peak tracking -> breaker trip -> signal downgrade -> reset, run against real Redis"},
        {"name": "stale_model_check", "declared_present": True, "verified_triggering": True,
         "evidence": "StockMLPredictor.is_stale(), unit tested"},
    ],
    "audit_trail": {"decision_log_exists": True, "evidence": "AuditDatabase persists every DecisionAuditTrail row"},
    "compliance_checks": [
        {"name": "risk_limit_check", "implemented": True},
        {"name": "position_concentration_check", "implemented": True},
        {"name": "anti_money_laundering", "implemented": False},
    ],
    "known_limitations": [
        "no L2 order-book data — unsuitable for market-making or sub-minute strategies",
        "backtest costs exclude price impact/slippage beyond a Kyle's-Lambda capacity estimate",
        "production scope is 3 symbols — breadth is the current Sharpe/IR ceiling",
        "compliance rule set is not a full regulatory engine (no AML/suitability rules)",
    ],
}

HOLLOW_MANIFEST = {
    "system_name": "Totally Ready Quant System",
    "as_of": (datetime.now() - timedelta(days=400)).date().isoformat(),
    "capability_claims": [
        {"claim": "institutional-grade risk management", "evidence": ""},
        {"claim": "fully validated across all traded symbols", "evidence": ""},
    ],
    "required_gates": ["ic_significance", "backtest_gate", "hac_test"],
    "production_scope": [
        {"asset": "EVERYTHING", "passed_gates": []},
    ],
    "risk_controls": [
        {"name": "circuit_breaker", "declared_present": True, "verified_triggering": False},
    ],
    "audit_trail": {"decision_log_exists": False},
    "compliance_checks": [
        {"name": "risk_limit_check", "implemented": False},
    ],
    "known_limitations": [],
}


def demo() -> int:
    print("=" * 68)
    print("DEMO — governance manifest gate: disclosed system vs hollow claims")
    print("=" * 68)
    outcomes = {}
    for name, manifest in (("disclosed_pipeline", DISCLOSED_MANIFEST), ("totally_ready_system", HOLLOW_MANIFEST)):
        rep = validate(manifest)
        outcomes[name] = rep["verdict"]
        print(f"\n> {name}")
        for f in rep["flags"]:
            print(f"  [{f['severity'].upper():4}] {f['code']}: {f['detail']}")
        if not rep["flags"]:
            print("  (no flags)")
        print(f"  VERDICT: {rep['verdict']}  ->  {rep['next_step']}")
    ok = outcomes["disclosed_pipeline"] in ("PASS", "WARN") and outcomes["totally_ready_system"] == "FAIL"
    print("\n" + ("demo OK — the gate rewards disclosure and refuses hollow claims" if ok
                  else "demo UNEXPECTED — check implementation"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Governance manifest due-diligence gate")
    ap.add_argument("manifest", nargs="?", help="path to MANIFEST.json")
    ap.add_argument("--staleness-days", type=int, default=90)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)
    if args.demo:
        return demo()
    if not args.manifest:
        ap.error("provide MANIFEST.json (or use --demo)")
    with open(args.manifest) as f:
        manifest = json.load(f)
    report = validate(manifest, staleness_days=args.staleness_days)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
