#!/usr/bin/env python3
"""verify_contrast.py — recomputes WCAG 2.x text-on-background contrast for
every palette in references/color_palettes.md and diffs it against the
ratio the file itself claims.

references/color_palettes.md opens with a factual claim: "the contrast
numbers below are computed, not claimed... every palette here clears AA
(4.5:1) for body text." That claim was true when the file was generated,
but nothing has protected it since — a hand-edited hex value (fixing a
typo, swapping a Background color for a slightly different shade) would
silently invalidate the claim while the printed ratio next to it kept
saying otherwise. This is the same failure shape as any other reference
data that's asserted once and never re-checked: the number looks
authoritative and nobody has a reason to doubt it.

This script is the check. It parses each `## <name>` palette block, pulls
the Background/Text hex pair and the file's own printed "Text on
background: **X.XX:1**" line, recomputes the ratio from the hex values
via the standard WCAG relative-luminance formula, and flags any palette
where the recomputed ratio disagrees with the printed one (a stale claim)
or fails to actually clear AA (4.5:1) despite the file's blanket claim
that all of them do.

Try it with no data:  python verify_contrast.py --demo
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_AA_BODY_TEXT = 4.5
_RATIO_TOLERANCE = 0.05  # printed values are rounded to 2dp; allow rounding slack

_DEFAULT_PALETTES_PATH = (
    Path(__file__).resolve().parent.parent / "references" / "color_palettes.md"
)

_BLOCK_RE = re.compile(r"^## (.+)$", re.M)
_ROLE_HEX_RE = re.compile(r"^\|\s*(\w+)\s*\|\s*`(#[0-9A-Fa-f]{6})`\s*\|$", re.M)
_PRINTED_RATIO_RE = re.compile(r"Text on background:\s*\*\*([\d.]+):1\*\*")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _channel_linear(c: int) -> float:
    c_norm = c / 255.0
    return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    r_lin, g_lin, b_lin = _channel_linear(r), _channel_linear(g), _channel_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    l1, l2 = relative_luminance(hex_a), relative_luminance(hex_b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_palettes(text: str) -> List[Dict[str, Any]]:
    """Splits the reference file into per-palette blocks and extracts the
    fields this gate needs. Skips (doesn't crash on) a block missing a role
    or a printed ratio line — reports it as a parse finding instead."""
    headers = list(_BLOCK_RE.finditer(text))
    palettes: List[Dict[str, Any]] = []
    for i, m in enumerate(headers):
        name = m.group(1).strip()
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[start:end]

        roles = {role: hexv for role, hexv in _ROLE_HEX_RE.findall(block)}
        ratio_m = _PRINTED_RATIO_RE.search(block)

        palettes.append({
            "name": name,
            "background": roles.get("Background"),
            "text": roles.get("Text"),
            "printed_ratio": float(ratio_m.group(1)) if ratio_m else None,
        })
    return palettes


def audit_palettes(palettes: List[Dict[str, Any]]) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []

    def flag(severity: str, code: str, name: str, message: str) -> None:
        findings.append({"severity": severity, "code": code, "palette": name, "message": message})

    for p in palettes:
        name = p["name"]
        if not p["background"] or not p["text"]:
            flag("fail", "missing_role_hex", name,
                 "Background and/or Text role hex not found in this block")
            continue
        if p["printed_ratio"] is None:
            flag("fail", "missing_printed_ratio", name,
                 "no 'Text on background: **X.XX:1**' line found for this block")
            continue

        recomputed = contrast_ratio(p["background"], p["text"])
        p["recomputed_ratio"] = round(recomputed, 2)

        if abs(recomputed - p["printed_ratio"]) > _RATIO_TOLERANCE:
            flag("fail", "ratio_mismatch", name,
                 f"printed {p['printed_ratio']:.2f}:1 but recomputed {recomputed:.2f}:1 from "
                 f"Background={p['background']} / Text={p['text']} — the hex values and the "
                 "printed number have drifted apart")

        if recomputed < _AA_BODY_TEXT:
            flag("fail", "fails_aa_body_text", name,
                 f"recomputed {recomputed:.2f}:1 does not clear AA's 4.5:1 for body text, "
                 "despite the file's blanket claim that every palette here does")

    severities = {f["severity"] for f in findings}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")
    return {
        "verdict": verdict,
        "palette_count": len(palettes),
        "findings": findings,
    }


# ───────────────────────────── demo ──────────────────────────────────────────

def demo() -> int:
    print("=" * 72)
    print("DEMO — a clean palette file vs. one with a silently drifted hex")
    print("=" * 72)

    clean_text = """
## Demo Clean

| Role | Hex |
| --- | --- |
| Primary | `#2563EB` |
| Secondary | `#3B82F6` |
| CTA | `#F97316` |
| Background | `#F8FAFC` |
| Text | `#1E293B` |
| Border | `#E2E8F0` |

Text on background: **13.98:1** (WCAG AA needs 4.5:1 for body text, 3:1 for large text)

Trust blue + accent contrast
"""
    clean_result = audit_palettes(parse_palettes(clean_text))
    print(f"\nclean file      -> verdict={clean_result['verdict']}  "
          f"findings={[f['code'] for f in clean_result['findings']]}")

    # Same palette, but Background got hand-edited to a mid-grey (a plausible
    # "just nudging the color" edit) — the printed ratio line was never
    # regenerated, so it now silently lies.
    drifted_text = clean_text.replace("| Background | `#F8FAFC` |", "| Background | `#8A8A8A` |")
    drifted_result = audit_palettes(parse_palettes(drifted_text))
    print(f"drifted file    -> verdict={drifted_result['verdict']}  "
          f"findings={[f['code'] for f in drifted_result['findings']]}")

    # A palette that fails AA outright but still carries a printed ratio
    # claiming otherwise (fabricated/never-recomputed).
    failing_text = """
## Demo Low Contrast

| Role | Hex |
| --- | --- |
| Primary | `#AAAAAA` |
| Secondary | `#BBBBBB` |
| CTA | `#CCCCCC` |
| Background | `#DDDDDD` |
| Text | `#CCCCCC` |
| Border | `#EEEEEE` |

Text on background: **12.00:1** (WCAG AA needs 4.5:1 for body text, 3:1 for large text)

Low-contrast demo block
"""
    failing_result = audit_palettes(parse_palettes(failing_text))
    print(f"low-contrast file -> verdict={failing_result['verdict']}  "
          f"findings={[f['code'] for f in failing_result['findings']]}")

    ok = (
        clean_result["verdict"] == "PASS"
        and drifted_result["verdict"] == "FAIL"
        and any(f["code"] == "ratio_mismatch" for f in drifted_result["findings"])
        and failing_result["verdict"] == "FAIL"
        and any(f["code"] in ("ratio_mismatch", "fails_aa_body_text") for f in failing_result["findings"])
    )
    print()
    print("=" * 72)
    print("demo OK — a silently drifted hex value is caught against the file's own "
          "printed claim" if ok else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Recompute WCAG contrast for references/color_palettes.md and diff against its printed claims")
    ap.add_argument("--palettes", default=str(_DEFAULT_PALETTES_PATH),
                     help=f"path to color_palettes.md (default: {_DEFAULT_PALETTES_PATH})")
    ap.add_argument("--json", help="write machine-readable result here instead of stdout")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    import json

    text = Path(args.palettes).read_text(encoding="utf-8")
    result = audit_palettes(parse_palettes(text))

    out = json.dumps(result, indent=2, default=str)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)
        if result["verdict"] == "FAIL":
            for f in result["findings"]:
                if f["severity"] == "fail":
                    print(f"  FAIL [{f['palette']}] {f['code']}: {f['message']}", file=sys.stderr)

    return 0 if result["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
