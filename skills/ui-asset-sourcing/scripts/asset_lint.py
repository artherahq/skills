#!/usr/bin/env python3
"""asset_lint.py — greps generated UI code for the mechanically-checkable
items on SKILL.md's Quality gate: emoji standing in for interface icons,
long inline SVG path data with no cited source (the "invented brand logo
renders as a blob" failure), and more than one icon library imported in the
same codebase.

Deliberately narrow: `ui-design-system`'s `design_lint.py` enforces code
against the *user's own declared tokens* (colors, radii, sizes, spacing) —
a different, tokens.json-shaped concern. This script needs no tokens file;
it checks universal icon/asset hygiene that applies whether or not a design
system has been frozen yet.

Not everything on the Quality gate is checkable here — "generated imagery
carries the actual palette hex values in its prompt" and "nothing generated
misrepresents a real person/place/company" require judgment this script
doesn't have. Three items genuinely are mechanical:
  emoji_icon         error  emoji character in UI-facing string/view code
  invented_svg_path   warn  long inline <path d="..."> with no nearby source
                            comment/import — can't prove it's hand-recalled,
                            but it's exactly the shape that failure takes
  mixed_icon_set      warn  imports from more than one known icon library
                            across the scanned paths

Try it with no data:  python asset_lint.py --demo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF\U00002700-\U000027BF"
    "]"
)

# `d="M12 2L2 7..."` — matches the attribute regardless of quote style; the
# path-data length (not the tag) is what decides if it's "long".
_SVG_PATH_RE = re.compile(r'd\s*=\s*["\']([^"\']{1,4000})["\']')
_MIN_SUSPECT_PATH_LEN = 60

# import-statement source -> normalized icon-library name. Not exhaustive —
# add here as new libraries come up; false negatives (an unrecognized
# library) are silent, not an error, by design.
_ICON_LIBRARY_MARKERS = {
    "lucide-react": "lucide", "lucide-svelte": "lucide", "lucide-vue-next": "lucide",
    "@heroicons/react": "heroicons", "@heroicons/vue": "heroicons",
    "@phosphor-icons/react": "phosphor", "phosphor-react": "phosphor",
    "@tabler/icons-react": "tabler", "@tabler/icons": "tabler",
    "react-icons": "react-icons",
    "simple-icons": "simple-icons",
}
_SOURCE_HINT_RE = re.compile(
    r"(lucide|heroicons|phosphor|tabler|simple.?icons|react-icons|figma|"
    r"verified|from:|source:)", re.IGNORECASE,
)


def _v(path: Path, lineno: int, rule: str, severity: str, snippet: str, message: str) -> dict:
    return {"file": str(path), "line": lineno, "rule": rule,
            "severity": severity, "snippet": snippet.strip(), "message": message}


def lint_file(path: Path) -> List[dict]:
    out: List[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return out

    lines = text.splitlines()
    for lineno, raw in enumerate(lines, start=1):
        if _EMOJI_RE.search(raw):
            out.append(_v(path, lineno, "emoji_icon", "error", raw,
                          "emoji character — use a real icon from a named set, not an emoji glyph"))

        for m in _SVG_PATH_RE.finditer(raw):
            path_data = m.group(1)
            if len(path_data) < _MIN_SUSPECT_PATH_LEN:
                continue
            # look at this line plus one line of context above for a source citation
            context = raw + (lines[lineno - 2] if lineno >= 2 else "")
            if _SOURCE_HINT_RE.search(context):
                continue
            out.append(_v(path, lineno, "invented_svg_path", "warn", raw,
                          f"inline SVG path data ({len(path_data)} chars) with no nearby source "
                          "citation — verify this came from a real icon/logo asset rather than "
                          "being hand-recalled, which renders as a blob"))

    return out


def lint_paths(paths: List[str]) -> dict:
    violations: List[dict] = []
    icon_libraries_seen: dict[str, List[str]] = {}

    for raw_path in paths:
        p = Path(raw_path)
        files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file())
        for f in files:
            violations.extend(lint_file(f))
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for marker, library in _ICON_LIBRARY_MARKERS.items():
                if marker in text:
                    icon_libraries_seen.setdefault(library, []).append(str(f))

    if len(icon_libraries_seen) > 1:
        libs = sorted(icon_libraries_seen)
        violations.append({
            "file": "(multiple)", "line": 0, "rule": "mixed_icon_set", "severity": "warn",
            "snippet": "", "message": (
                f"{len(libs)} icon libraries imported across the scanned paths ({', '.join(libs)}) "
                "— pick one icon set throughout, not a mix"
            ),
        })

    severities = {v["severity"] for v in violations}
    verdict = "FAIL" if "error" in severities else ("WARN" if "warn" in severities else "PASS")
    return {"verdict": verdict, "violations": violations, "icon_libraries_seen": icon_libraries_seen}


# ───────────────────────────── demo ──────────────────────────────────────────

def demo() -> int:
    import tempfile

    print("=" * 72)
    print("DEMO — clean icon usage vs. emoji/invented-path/mixed-set violations")
    print("=" * 72)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "Good.tsx").write_text(
            'import { ArrowRight } from "lucide-react";\n'
            "export const Cta = () => <button><ArrowRight size={16} /></button>;\n",
            encoding="utf-8",
        )
        (tmp / "Bad.tsx").write_text(
            'import { Home } from "lucide-react";\n'
            'import { Bell } from "@heroicons/react/24/outline";\n'
            'const rocket = "\U0001F680";\n'
            'const logo = <svg><path d="M83.4 12.1c-5.2-3.1-11.9-3.1-17.1 0-14.2 8.5-22.9 24.1-22.9 40.9v55c0 16.8 8.7 32.4 22.9 40.9 5.2 3.1 11.9 3.1 17.1 0" /></svg>;\n',
            encoding="utf-8",
        )
        result = lint_paths([str(tmp)])
        rules_seen = {v["rule"] for v in result["violations"]}
        print(f"\nverdict={result['verdict']}  rules={sorted(rules_seen)}")
        for v in result["violations"]:
            print(f"  [{v['severity']}] {Path(v['file']).name}:{v['line']} {v['rule']} — {v['message'][:80]}")

        ok = (
            result["verdict"] == "FAIL"  # emoji is an error-severity rule
            and "emoji_icon" in rules_seen
            and "invented_svg_path" in rules_seen
            and "mixed_icon_set" in rules_seen
            and not any(v["file"].endswith("Good.tsx") for v in result["violations"])
        )

    print()
    print("=" * 72)
    print("demo OK — clean file has no violations, the bad file trips all three "
          "checkable rules" if ok else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Lint generated UI code for emoji-as-icon, invented SVG paths, and mixed icon sets")
    ap.add_argument("paths", nargs="*", help="files/directories to scan")
    ap.add_argument("--json", help="write machine-readable result here instead of stdout")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    if not args.paths:
        ap.error("--demo, or one or more paths to scan, is required")
        return 2

    result = lint_paths(args.paths)
    out = json.dumps(result, indent=2, default=str)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)

    return 0 if result["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
