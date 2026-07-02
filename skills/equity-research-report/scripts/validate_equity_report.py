#!/usr/bin/env python3
"""Validate an equity-research manifest without third-party dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVIDENCE = {"market_data", "filing", "risk"}
REQUIRED_SECTIONS = {
    "executive_summary",
    "fundamentals",
    "valuation",
    "technical",
    "risk",
    "scenarios",
    "sources",
}
CORE_AGENTS = {"technical", "fundamental", "risk"}


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    report = dict(manifest.get("report") or {})
    metrics = dict(manifest.get("metrics") or {})
    agents = list(manifest.get("agents") or [])
    evidence = list(manifest.get("evidence") or [])
    sections = {str(item) for item in manifest.get("sections") or []}
    blocking: list[str] = []
    warnings: list[str] = []

    if not str(report.get("symbol") or "").strip():
        blocking.append("report.symbol is required")
    if not str(report.get("as_of") or "").strip():
        blocking.append("report.as_of is required")

    price = _number(metrics.get("price"))
    volume = _number(metrics.get("volume"))
    market_cap = _number(metrics.get("market_cap"))
    if price is None or price <= 0:
        blocking.append("reference price must be positive")
    if volume is not None and volume < 0:
        blocking.append("volume cannot be negative")
    if market_cap is not None:
        if market_cap <= 0 or market_cap > 100_000_000_000_000:
            warnings.append("market_cap is outside the plausibility range")
        if price and price > 0 and market_cap / price > 100_000_000_000:
            warnings.append("implied share count is outside the plausibility range")

    requested = {
        str(item.get("agent")) for item in agents if str(item.get("agent") or "").strip()
    }
    usable = {
        str(item.get("agent"))
        for item in agents
        if item.get("success") is True and str(item.get("analysis") or "").strip()
    }
    degraded = {
        str(item.get("agent")) for item in agents if item.get("degraded") is True
    } & usable
    agent_coverage = len(usable) / len(requested) if requested else 0.0
    requested_core = requested & CORE_AGENTS
    core_coverage = (
        len(usable & requested_core) / len(requested_core) if requested_core else 1.0
    )
    if not usable:
        blocking.append("no agent produced usable analysis")
    if agent_coverage < 0.60:
        warnings.append("agent coverage is below 60%")
    if core_coverage < 2 / 3:
        warnings.append("core-agent coverage is below 67%")
    if usable and len(degraded) / len(usable) > 0.50:
        warnings.append("more than half of usable agents are degraded")

    evidence_kinds = {
        str(item.get("kind"))
        for item in evidence
        if item.get("verified", True) is True
        and item.get("source")
        and item.get("as_of")
    }
    missing_evidence = sorted(REQUIRED_EVIDENCE - evidence_kinds)
    if missing_evidence:
        warnings.append(f"missing verified evidence: {', '.join(missing_evidence)}")
    missing_sections = sorted(REQUIRED_SECTIONS - sections)
    if missing_sections:
        warnings.append(f"missing report sections: {', '.join(missing_sections)}")

    data_status = str(report.get("data_status") or report.get("status") or "").lower()
    if data_status in {"unavailable", "data_unavailable", "failed", "blocked"}:
        blocking.append(f"data status is {data_status}")
    elif data_status in {"partial", "stale"}:
        warnings.append(f"data status is {data_status}")

    decision = "blocked" if blocking else "partial" if warnings else "complete"
    if report.get("status") == "complete" and decision != "complete":
        warnings.append("report claims complete but completion gates did not pass")
        decision = "blocked" if blocking else "partial"
    return {
        "decision": decision,
        "agent_coverage": round(agent_coverage, 4),
        "core_agent_coverage": round(core_coverage, 4),
        "usable_agents": sorted(usable),
        "degraded_agents": sorted(degraded),
        "evidence_kinds": sorted(evidence_kinds),
        "missing_evidence": missing_evidence,
        "missing_sections": missing_sections,
        "warnings": warnings,
        "blocking_reasons": blocking,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "blocked", "blocking_reasons": [str(exc)]}))
        return 3
    result = validate_manifest(manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["decision"] == "complete":
        return 0
    if result["decision"] == "partial" and args.allow_partial:
        return 0
    return 2 if result["decision"] == "partial" else 3


if __name__ == "__main__":
    raise SystemExit(main())
