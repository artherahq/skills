#!/usr/bin/env python3
"""pattern_audit.py — checks a UI component manifest against the reference
checklist for the trading-app pattern it claims to implement (X, TradingView,
Trading212), and flags the one failure mode that looks completely fine at a
glance: a hardcoded convention copied from the wrong market.

The clearest example is direction color on a watchlist/holdings row. US,
Hong Kong, and most Western markets use red=down/green=up. Mainland China and
Taiwan use the opposite: red=up/green=down (red is auspicious, associated with
rising prices). A component built and tested against US data, then pointed at
a CN/TW symbol feed without re-deriving the color rule, renders every single
quote backwards — and nothing crashes, nothing looks obviously wrong, the
colors are just confidently inverted for that market's users. `demo()` below
reproduces exactly that.

Try it with no data:  python pattern_audit.py --demo
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_PATTERNS_PATH = Path(__file__).resolve().parent.parent / "references" / "patterns.json"


def load_patterns(path: Path = DEFAULT_PATTERNS_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("patterns", {})


def audit_manifest(manifest: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic checklist audit — no aesthetic judgment, only checks
    the manifest itself declares are answerable: required/recommended/forbidden
    field presence, numeric/equality rules, and market-aware convention checks."""
    pattern_id = manifest.get("pattern")
    if pattern_id not in patterns:
        return {
            "verdict": "FAIL",
            "pattern": pattern_id,
            "product": None,
            "findings": [{
                "severity": "fail",
                "code": "unknown_pattern",
                "message": f"'{pattern_id}' is not a known pattern id. Run --list for the catalog.",
            }],
        }

    spec = patterns[pattern_id]
    fields = manifest.get("fields", {}) or {}
    market = manifest.get("market")
    findings: List[Dict[str, Any]] = []

    for req in spec.get("required_fields", []):
        if req not in fields or fields[req] in (None, False, ""):
            findings.append({
                "severity": "fail",
                "code": "missing_required_field",
                "field": req,
                "message": f"Required field '{req}' is missing or falsy for pattern '{pattern_id}'",
            })

    for rec in spec.get("recommended_fields", []):
        if rec not in fields or fields[rec] in (None, False, ""):
            findings.append({
                "severity": "warn",
                "code": "missing_recommended_field",
                "field": rec,
                "message": f"Recommended field '{rec}' is absent — pattern reads as thinner than the reference",
            })

    for forb in spec.get("forbidden_fields", []):
        if fields.get(forb) is True:
            findings.append({
                "severity": "fail",
                "code": "forbidden_condition_present",
                "field": forb,
                "message": f"Forbidden condition '{forb}' is present in this component",
            })

    for rule in spec.get("rules", []):
        field = rule["field"]
        if field not in fields:
            continue  # only enforce a rule on a field the manifest actually declares
        value = fields[field]
        severity = rule.get("severity", "warn")
        if "min" in rule:
            if not isinstance(value, (int, float)) or value < rule["min"]:
                findings.append({
                    "severity": severity, "code": "rule_violation", "field": field,
                    "message": rule["message"], "value": value, "min": rule["min"],
                })
        elif "equals" in rule:
            if value != rule["equals"]:
                findings.append({
                    "severity": severity, "code": "rule_violation", "field": field,
                    "message": rule["message"], "value": value, "expected": rule["equals"],
                })

    for field, market_map in spec.get("market_aware_fields", {}).items():
        if field not in fields:
            continue
        expected = market_map.get(market, market_map.get("default"))
        actual = fields[field]
        if expected is not None and actual != expected:
            findings.append({
                "severity": "fail",
                "code": "market_convention_mismatch",
                "field": field,
                "message": (
                    f"'{field}' is '{actual}' but market '{market or 'unspecified'}' convention "
                    f"expects '{expected}' — check for a convention hardcoded from a different market"
                ),
                "value": actual,
                "expected": expected,
            })

    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    verdict = "FAIL" if fail_count else ("WARN" if findings else "PASS")
    return {"verdict": verdict, "pattern": pattern_id, "product": spec.get("product"), "findings": findings}


def format_report(report: Dict[str, Any]) -> str:
    lines = [f"Verdict: {report['verdict']}  (pattern: {report['pattern']}, product: {report.get('product')})"]
    if not report["findings"]:
        lines.append("  No findings.")
    for f in report["findings"]:
        marker = {"fail": "FAIL", "warn": "WARN"}.get(f["severity"], f["severity"].upper())
        field = f.get("field", "")
        lines.append(f"  [{marker}] {f['code']}{f' (' + field + ')' if field else ''}: {f['message']}")
    return "\n".join(lines)


def demo() -> int:
    patterns = load_patterns()

    print("=== Case 1: CN-market watchlist row with a hardcoded US color convention ===")
    buggy_manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "CN",
        "fields": {
            "symbol": True, "price": True, "change_value": True, "change_percent": True,
            "direction_color": "red_down_green_up",  # copied from the US build, never re-derived for CN
            "tap_target_pt": 48,
            "price_font": "monospaced_tabular",
        },
    }
    buggy_report = audit_manifest(buggy_manifest, patterns)
    print(format_report(buggy_report))
    assert buggy_report["verdict"] == "FAIL"
    assert any(f["code"] == "market_convention_mismatch" for f in buggy_report["findings"])
    print("\n  -> Confirmed: identical component, wrong market convention, flagged as FAIL "
          "with no changes needed to reproduce the bug — this is the same shape of error as "
          "a sign-convention flip, just in a color instead of a number.\n")

    print("=== Case 2: same component, convention corrected for CN ===")
    fixed_manifest = dict(buggy_manifest)
    fixed_manifest["fields"] = dict(buggy_manifest["fields"])
    fixed_manifest["fields"]["direction_color"] = "red_up_green_down"
    fixed_report = audit_manifest(fixed_manifest, patterns)
    print(format_report(fixed_report))
    assert fixed_report["verdict"] in ("PASS", "WARN")
    print("\n  -> Same manifest, one field corrected, no longer flagged.\n")

    print("=== Case 3: an order ticket missing required fields ===")
    thin_manifest = {
        "pattern": "trading212_order_ticket",
        "fields": {
            "side_toggle": True,
            "confirm_action": True,
            # quantity_or_value_input and estimated_total both missing
        },
    }
    thin_report = audit_manifest(thin_manifest, patterns)
    print(format_report(thin_report))
    assert thin_report["verdict"] == "FAIL"
    assert sum(1 for f in thin_report["findings"] if f["code"] == "missing_required_field") == 2
    print("\nDemo complete — deterministic checklist audit, no LLM judgment involved.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Audit a UI component manifest against a trading-app reference pattern")
    ap.add_argument("--patterns", type=Path, default=DEFAULT_PATTERNS_PATH, help="path to patterns.json (default: bundled reference file)")
    ap.add_argument("--list", action="store_true", help="list available pattern ids and exit")
    ap.add_argument("--manifest", type=Path, help="JSON file describing the component to audit")
    ap.add_argument("--json", type=Path, help="write the machine-readable report here")
    ap.add_argument("--demo", action="store_true", help="run a self-contained demonstration, no files needed")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    patterns = load_patterns(args.patterns)

    if args.list:
        for pid, spec in sorted(patterns.items()):
            print(f"{pid}  ({spec.get('product')}) — {spec.get('description')}")
        return 0

    if not args.manifest:
        ap.print_help()
        return 1

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    report = audit_manifest(manifest, patterns)
    print(format_report(report))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
