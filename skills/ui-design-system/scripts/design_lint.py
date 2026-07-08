#!/usr/bin/env python3
"""Enforce generated UI code against the USER'S own design-tokens.json.

Nothing here is Arthera-specific: the set of allowed colors/radii comes
entirely from the tokens file passed in. A color or radius literal in code
that is not one of the user's declared tokens is "off-system".

Checks:
  color_off_system    error   a hex / Color(r:g:b:) / rgb() literal whose value
                              is not within tolerance of any token color; the
                              message names the nearest token so the fix is a
                              route, not a guess
  radius_off_system   warn    a numeric cornerRadius/border-radius/borderRadius
                              not equal to one of the user's radius tiers
  emoji_icon          error   emoji character, when the tokens file declares
                              conventions.emoji_icons == "forbid" (the default)

Color matching uses a small RGB-distance tolerance (default 3.0) so that
floating-point rounding — e.g. SwiftUI Color(red: 0.184, ...) vs the token's
#2f6bff — is not misreported as off-system. Genuinely different colors sit far
outside the tolerance.

Usage:
    python design_lint.py --tokens design-tokens.json --paths src/ View.swift --json report.json
    python design_lint.py --tokens design-tokens.json --paths src/ --color-tolerance 0
    python design_lint.py --demo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_COLOR_TOLERANCE = 3.0  # RGB euclidean distance treated as a rounding match

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF\U00002700-\U000027BF"
    "]"
)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")
_SWIFT_RGB_RE = re.compile(r"Color\(\s*red:\s*([\d.]+),\s*green:\s*([\d.]+),\s*blue:\s*([\d.]+)")
_CSS_RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
_RADIUS_RE = re.compile(r"(?:cornerRadius|border-?[Rr]adius)\s*:?\s*\(?\s*(\d+(?:\.\d+)?)")


def _norm_hex(h: str) -> str:
    return "#" + h.lstrip("#").lower()


def _rgb01_to_hex(r: str, g: str, b: str) -> str:
    return "#" + "".join(f"{round(float(c) * 255):02x}" for c in (r, g, b))


def _rgb255_to_hex(r: str, g: str, b: str) -> str:
    return "#" + "".join(f"{max(0, min(255, int(c))):02x}" for c in (r, g, b))


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _color_distance(h1: str, h2: str) -> float:
    a, b = _hex_to_rgb(h1), _hex_to_rgb(h2)
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def _nearest_token(hx: str, allowed: dict[str, str]) -> tuple[str | None, str | None, float]:
    """-> (token name, token hex, distance) of the closest palette color."""
    best_name: str | None = None
    best_hex: str | None = None
    best_dist = float("inf")
    for ahex, name in allowed.items():
        d = _color_distance(hx, ahex)
        if d < best_dist:
            best_name, best_hex, best_dist = name, ahex, d
    return best_name, best_hex, best_dist


def load_allowed(tokens: dict) -> tuple[dict[str, str], set[float], str]:
    """-> ({normalized hex: token name}, allowed radius set, emoji convention)."""
    appearance = tokens.get("appearance", "light-dark")
    hexes: dict[str, str] = {}
    for name, spec in tokens.get("color", {}).items():
        if appearance == "single" and isinstance(spec, str):
            vals = [spec]
        elif isinstance(spec, dict):
            vals = [v for v in (spec.get("light"), spec.get("dark")) if isinstance(v, str)]
        else:
            vals = []
        for v in vals:
            hexes.setdefault(_norm_hex(v), name)
    radii = {float(v) for v in tokens.get("radius", {}).values()
             if isinstance(v, (int, float))}
    convention = (tokens.get("conventions", {}) or {}).get("emoji_icons", "forbid")
    return hexes, radii, convention


def _strip_comment(line: str) -> str:
    for marker in ("//", "/*"):
        idx = line.find(marker)
        if idx != -1:
            line = line[:idx]
    return line


def lint_file(path: Path, allowed_colors: dict[str, str], allowed_radius: set[float],
              emoji_convention: str, color_tolerance: float = DEFAULT_COLOR_TOLERANCE) -> list[dict]:
    out: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return out

    for lineno, raw in enumerate(text.splitlines(), start=1):
        if emoji_convention == "forbid" and _EMOJI_RE.search(raw):
            out.append(_v(path, lineno, "emoji_icon", "error", raw.strip(),
                          "emoji character — tokens declare emoji_icons=forbid; use a real icon"))
        code = _strip_comment(raw)

        found_hex: set[str] = set()
        for m in _HEX_RE.finditer(code):
            found_hex.add(_norm_hex(m.group(0)))
        for m in _SWIFT_RGB_RE.finditer(code):
            found_hex.add(_rgb01_to_hex(*m.groups()))
        for m in _CSS_RGB_RE.finditer(code):
            found_hex.add(_rgb255_to_hex(*m.groups()))
        for hx in sorted(found_hex):
            if hx in allowed_colors:
                continue
            name, ahex, dist = _nearest_token(hx, allowed_colors)
            if dist <= color_tolerance:
                continue  # within rounding tolerance of a token — treat as that token
            msg = f"color {hx} is not in the token palette"
            if name:
                msg += f" (nearest token: {name} {ahex})"
            out.append(_v(path, lineno, "color_off_system", "error", code.strip(), msg))

        for m in _RADIUS_RE.finditer(code):
            val = float(m.group(1))
            if allowed_radius and val not in allowed_radius:
                out.append(_v(path, lineno, "radius_off_system", "warn", code.strip(),
                              f"radius {m.group(1)} is not a declared token tier"))
    return out


def _v(path, lineno, rule, severity, snippet, message) -> dict:
    return {"file": str(path), "line": lineno, "rule": rule,
            "severity": severity, "snippet": snippet, "message": message}


def lint_paths(paths: list[str], allowed_colors, allowed_radius, emoji_convention,
               color_tolerance: float = DEFAULT_COLOR_TOLERANCE) -> list[dict]:
    out: list[dict] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files = sorted(f for f in path.rglob("*")
                           if f.suffix in {".swift", ".css", ".scss", ".tsx", ".jsx",
                                           ".ts", ".js", ".dart", ".vue", ".html"})
        else:
            files = [path]
        for f in files:
            out.extend(lint_file(f, allowed_colors, allowed_radius, emoji_convention, color_tolerance))
    return out


def _report(violations: list[dict]) -> dict:
    by_rule: dict[str, int] = {}
    for v in violations:
        by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1
    errors = [v for v in violations if v["severity"] == "error"]
    return {"violations": violations, "by_rule": by_rule,
            "n_violations": len(violations), "n_errors": len(errors),
            "compliant": not errors}


def _print_human(report: dict) -> None:
    if not report["violations"]:
        print("  no violations — consistent with the token system")
        return
    for v in report["violations"]:
        print(f"  {v['file']}:{v['line']}  {v['rule']} [{v['severity']}]")
        print(f"    → {v['message']}")
    print(f"\n  {report['n_violations']} violation(s), {report['n_errors']} error(s)")


def _demo() -> int:
    tokens = {
        "schema_version": "aria.design-tokens.v1", "name": "Demo",
        "appearance": "light-dark",
        "conventions": {"emoji_icons": "forbid"},
        "color": {
            "canvas": {"light": "#ffffff", "dark": "#0f1216"},
            "accent": {"light": "#2f6bff", "dark": "#5b86ff"},
        },
        "radius": {"card": 12, "control": 8},
    }
    allowed_colors, allowed_radius, convention = load_allowed(tokens)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "Good.swift").write_text(
            'let c = Color("accent")\n'
            "let d = Color(red: 0.184, green: 0.42, blue: 1.0)  // ~ #2f6bff within tolerance\n"
            ".cornerRadius(12)\n", encoding="utf-8")
        (tmp / "Bad.swift").write_text(
            "Text(\"\U0001F680\")\n"                       # emoji
            "let c = Color(red: 0.2, green: 0.4, blue: 0.9)\n"  # #3366e6, off-system but near accent
            ".cornerRadius(14)\n",                          # off-system radius
            encoding="utf-8")
        violations = lint_paths([str(tmp)], allowed_colors, allowed_radius, convention)
        report = _report(violations)
        print("=== demo: Good.swift (clean, incl. a rounding-equivalent color) "
              "+ Bad.swift (3 violations) ===\n")
        _print_human(report)
        good = [v for v in violations if v["file"].endswith("Good.swift")]
        bad = [v for v in violations if v["file"].endswith("Bad.swift")]
        bad_rules = {v["rule"] for v in bad}
        assert good == [], f"clean file (incl. tolerance color) should have no violations: {good}"
        assert bad_rules == {"emoji_icon", "color_off_system", "radius_off_system"}
        assert any("nearest token: accent" in v["message"] for v in bad), "should suggest nearest token"
        print("\n  demo assertions passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint UI code against the user's design tokens")
    ap.add_argument("--tokens", help="path to the user's design-tokens.json")
    ap.add_argument("--paths", nargs="+", help="files or dirs to scan")
    ap.add_argument("--color-tolerance", type=float, default=DEFAULT_COLOR_TOLERANCE,
                    help="RGB distance treated as a rounding match (0 = exact)")
    ap.add_argument("--json", help="write machine-readable report here")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return _demo()
    if not args.tokens or not args.paths:
        print("need --tokens design-tokens.json --paths <file_or_dir> ... (or --demo)")
        return 1

    try:
        tokens = json.loads(Path(args.tokens).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"  cannot read tokens: {e}")
        return 1

    allowed_colors, allowed_radius, convention = load_allowed(tokens)
    violations = lint_paths(args.paths, allowed_colors, allowed_radius, convention, args.color_tolerance)
    report = _report(violations)
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n  UI Design System Lint — tokens '{tokens.get('name', '?')}', "
          f"{len(allowed_colors)} colors / {len(allowed_radius)} radii")
    _print_human(report)
    return 0 if report["compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
