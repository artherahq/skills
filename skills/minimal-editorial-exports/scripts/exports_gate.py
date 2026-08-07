#!/usr/bin/env python3
"""exports_gate.py — audits a minimal-editorial cover/title-slide spec
against SKILL.md's Design Rules and Checklist as code, the same pattern
`minimal-editorial-poster`'s `poster_gate.py` uses for its own compiled
prompt (these two skills are siblings; keep the two gates' shape aligned
if one changes).

The failure mode this catches: a "minimal" cover that quietly isn't — a
sidebar and nav carried over from the report body, a second color fighting
the accent, texture faked onto a PPTX slide that can't render it, or
negative space that's "less dense than the body" instead of genuinely 70%+.
Each of these reads as a reasonable cover brief right up until it's checked
against the rules that make it actually minimal rather than a smaller
dashboard.

Try it with no data:  python exports_gate.py --demo
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

# Rule 5 + the Checklist's "no borrowed dashboard chrome" — straight out of
# SKILL.md's own Design Rules.
FORBIDDEN_TERMS = [
    "sidebar", "nav bar", "navbar", "navigation", "multi-panel grid",
    "dashboard chrome", "multiple panels",
]

_GENERIC_SANS = ["inter", "arial", "helvetica", "system-ui", "-apple-system", "roboto"]
_RESTRAINED_HINTS = ["serif", "mono", "typewriter", "georgia", "courier", "garamond", "playfair"]

# Rule 4: texture only renders on formats with a real paint surface.
_TEXTURE_CAPABLE_FORMATS = {"html_pdf"}
_NON_REPORT_BODY_SURFACES = {"cover", "title_slide", "standalone_chart", "canva_onepager"}


def compile_brief(spec: Dict[str, Any]) -> str:
    """Renders a short structured summary — not an image-gen prompt like
    poster_gate's compile_prompt, since this styles real export pipelines
    (report_generator.py / pdf_report.py / report_exporters.py /
    canva_client.py), not a from-scratch generated image."""
    accent = spec.get("accent_color") or {}
    texture = spec.get("texture") or ""
    lines = [
        "EXPORT COVER SPEC",
        f"Surface: {spec.get('surface', '?')} ({spec.get('export_format', '?')})",
        f"Quiet space: {spec.get('quiet_pct', '?')}%",
        f"Focal point: {spec.get('focal_point_type', '?')} — {spec.get('focal_point', '?')}",
        f"Accent: {accent.get('name', '?')} ({accent.get('source', 'no source stated')})",
        f"Typography: {spec.get('typography', '?')}",
        f"Texture: {texture or 'none — format does not support it or none chosen'}",
        "Chrome: none borrowed from report body",
    ]
    return "\n".join(lines)


def audit_export_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic checklist audit mirroring SKILL.md's Checklist. Not
    aesthetic judgment — only checks the spec itself makes answerable."""
    findings: List[Dict[str, str]] = []

    def flag(severity: str, code: str, message: str) -> None:
        findings.append({"severity": severity, "code": code, "message": message})

    # Rule 1 / Checklist item 1 — genuinely 70%+ quiet.
    pct = spec.get("quiet_pct")
    if pct is None:
        flag("fail", "missing_quiet_pct", "no quiet_pct declared")
    elif pct < 70:
        flag("fail", "insufficient_quiet_space",
             f"quiet_pct={pct} — rule is 70%+ genuinely quiet, not just less dense than the body")
    elif pct < 75:
        flag("warn", "borderline_quiet_space",
             f"quiet_pct={pct} is at the low edge of the 70%+ rule")

    # Checklist item 6 — this style governs covers/slides, never the body.
    surface = spec.get("surface")
    if surface not in _NON_REPORT_BODY_SURFACES:
        flag("fail", "wrong_surface_for_style",
             f"surface='{surface}' — this style is for cover/title/single-focal surfaces "
             f"only ({sorted(_NON_REPORT_BODY_SURFACES)}), never the dense report body")

    # Rule 2 / Checklist item 2 — one accent, tied to real meaning.
    accent = spec.get("accent_color")
    if not accent or not (accent.get("name") or "").strip():
        flag("fail", "missing_accent_color", "no accent_color declared")
    elif not (accent.get("source") or "").strip():
        flag("warn", "accent_not_grounded",
             f"accent color '{accent.get('name')}' has no source — should tie to real signal "
             "meaning (gain/loss, buy/sell) or at least be a deliberate single choice, not "
             "an arbitrary mood color")

    # Rule 3 / Checklist item 3 — restrained type, not the dashboard default.
    typography = spec.get("typography") or ""
    if not typography.strip():
        flag("fail", "missing_typography", "no typography declared")
    else:
        low = typography.lower()
        looks_generic = any(g in low for g in _GENERIC_SANS)
        looks_restrained = any(r in low for r in _RESTRAINED_HINTS)
        if looks_generic and not looks_restrained:
            flag("warn", "typography_reads_as_dashboard_default",
                 f"typography='{typography}' names a generic dashboard sans with no serif/"
                 "monospace restraint signal — confirm this isn't just the safe default")

    # Rule 4 / Checklist item 4 — texture only where the format renders it.
    export_format = spec.get("export_format")
    texture = (spec.get("texture") or "").strip()
    if texture and export_format not in _TEXTURE_CAPABLE_FORMATS:
        flag("fail", "texture_unsupported_by_format",
             f"texture='{texture}' declared for export_format='{export_format}', which cannot "
             f"render it (only {sorted(_TEXTURE_CAPABLE_FORMATS)} can) — let space/type do the "
             "work instead of faking grain")

    # Rule 5 / Checklist item 5 — no borrowed dashboard chrome, and no
    # forbidden term leaking into the fields meant to avoid it.
    haystack_fields = {
        "focal_point": spec.get("focal_point") or "",
        "typography": typography,
        "texture": texture,
        "accent_name": (accent or {}).get("name") or "" if accent else "",
        "chrome_notes": spec.get("chrome_notes") or "",
    }
    for field_name, text in haystack_fields.items():
        low = text.lower()
        for term in FORBIDDEN_TERMS:
            if term in low:
                flag("fail", "borrowed_dashboard_chrome",
                     f"'{term}' found inside '{field_name}' — a cover that reuses the report "
                     "body's chrome isn't restrained, it's just a smaller dashboard")

    # Checklist item 7 — batch variation, only checkable when the caller
    # says this export is part of a batch.
    if spec.get("is_batch"):
        if not (spec.get("variation_axis") or "").strip() or not (spec.get("variation_reason") or "").strip():
            flag("warn", "no_batch_variation_declared",
                 "is_batch=true but no variation_axis/variation_reason declared — a batch "
                 "with one fixed recipe becomes its own template")

    severities = {f["severity"] for f in findings}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")
    return {"verdict": verdict, "findings": findings}


# ───────────────────────────── demo ──────────────────────────────────────────

def _bad_spec_dashboard_cover() -> Dict[str, Any]:
    """A "minimal" cover that quietly isn't: dense, two colors, borrowed
    chrome, texture faked onto a format that can't render it, dashboard
    default type."""
    return {
        "surface": "cover",
        "export_format": "pptx",
        "quiet_pct": 25,
        "focal_point": "full summary panel with sidebar navigation and a multi-panel grid",
        "focal_point_type": "text",
        "accent_color": {"name": "brand blue", "hex": "#2563EB", "source": ""},
        "typography": "Inter, system-ui",
        "texture": "subtle paper grain",
        "chrome_notes": "",
    }


def _good_spec_minimal_cover() -> Dict[str, Any]:
    """The corrected compile for a report showing a positive headline return."""
    return {
        "surface": "cover",
        "export_format": "html_pdf",
        "quiet_pct": 82,
        "focal_point": "headline return: +4.2%",
        "focal_point_type": "number",
        "accent_color": {"name": "signal green", "hex": "#1F8A4C",
                          "source": "this report's actual positive return, the real gain/loss signal"},
        "typography": "Georgia headline, monospace caption",
        "texture": "subtle paper grain",
        "chrome_notes": "",
    }


def demo() -> int:
    print("=" * 72)
    print("DEMO — same report, two compiled cover specs")
    print("=" * 72)

    bad = _bad_spec_dashboard_cover()
    bad_result = audit_export_spec(bad)
    print("\n[dense cover wearing a 'minimal' label]")
    print(compile_brief(bad))
    print(f"\nverdict={bad_result['verdict']}  "
          f"findings={[f['code'] for f in bad_result['findings']]}")

    good = _good_spec_minimal_cover()
    good_result = audit_export_spec(good)
    print("\n" + "-" * 72)
    print("[corrected minimal-editorial cover]")
    print(compile_brief(good))
    print(f"\nverdict={good_result['verdict']}  "
          f"findings={[f['code'] for f in good_result['findings']]}")

    ok = (
        bad_result["verdict"] == "FAIL"
        and good_result["verdict"] in ("PASS", "WARN")
        and any(f["code"] == "insufficient_quiet_space" for f in bad_result["findings"])
        and any(f["code"] == "borrowed_dashboard_chrome" for f in bad_result["findings"])
        and any(f["code"] == "texture_unsupported_by_format" for f in bad_result["findings"])
    )
    print()
    print("=" * 72)
    print("demo OK — the gate separates the dense cover from the minimal-editorial "
          "compile correctly" if ok else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compile + audit a minimal-editorial-exports cover spec against SKILL.md's Checklist")
    ap.add_argument("--spec", help="JSON file with the compiled fields (see SKILL.md Design Rules)")
    ap.add_argument("--json", help="write machine-readable result here instead of stdout")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    if not args.spec:
        ap.error("--demo, or --spec <spec.json>, is required")
        return 2

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    result = audit_export_spec(spec)
    result["compiled_brief"] = compile_brief(spec)

    out = json.dumps(result, indent=2, default=str)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)

    return 0 if result["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
