"""design_lint tests: off-system detection is driven by the USER's tokens."""

import subprocess
import sys
from pathlib import Path

from design_lint import lint_file, lint_paths, load_allowed, main

FIXTURE_DIR = Path(__file__).parent

TOKENS = {
    "schema_version": "aria.design-tokens.v1", "name": "T", "appearance": "light-dark",
    "conventions": {"emoji_icons": "forbid"},
    "color": {
        "canvas": {"light": "#ffffff", "dark": "#0f1216"},
        "accent": {"light": "#2f6bff", "dark": "#5b86ff"},
    },
    "radius": {"card": 12, "control": 8},
}


def _allowed():
    return load_allowed(TOKENS)


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_in_palette_color_is_clean(tmp_path):
    ah, ar, conv = _allowed()
    # #2f6bff is the accent light value → allowed
    p = _write(tmp_path, "A.css", "a { color: #2F6BFF; }\n")
    assert lint_file(p, ah, ar, conv) == []


def test_off_palette_hex_flagged(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "A.css", "a { color: #ff0000; }\n")
    v = lint_file(p, ah, ar, conv)
    assert any(x["rule"] == "color_off_system" for x in v)


def test_swiftui_rgb_literal_normalized_and_checked(tmp_path):
    ah, ar, conv = _allowed()
    # 0.2/0.6/0.9 → not in palette
    p = _write(tmp_path, "V.swift", "Color(red: 0.2, green: 0.6, blue: 0.9)\n")
    v = lint_file(p, ah, ar, conv)
    assert any(x["rule"] == "color_off_system" for x in v)


def test_css_rgb_matches_palette(tmp_path):
    ah, ar, conv = _allowed()
    # rgb(47,107,255) == #2f6bff (accent) → allowed
    p = _write(tmp_path, "A.css", "a { color: rgb(47, 107, 255); }\n")
    assert lint_file(p, ah, ar, conv) == []


def test_radius_off_system_is_warn(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "A.css", ".x { border-radius: 14px; }\n")
    v = lint_file(p, ah, ar, conv)
    assert v and v[0]["rule"] == "radius_off_system" and v[0]["severity"] == "warn"


def test_declared_radius_is_clean(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "A.css", ".x { border-radius: 12px; }\n")
    assert lint_file(p, ah, ar, conv) == []


def test_emoji_forbidden_by_default(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "A.tsx", "const x = '\U0001F680';\n")
    v = lint_file(p, ah, ar, conv)
    assert any(x["rule"] == "emoji_icon" for x in v)


def test_emoji_allowed_when_convention_permits(tmp_path):
    tokens = dict(TOKENS, conventions={"emoji_icons": "allow"})
    ah, ar, conv = load_allowed(tokens)
    p = _write(tmp_path, "A.tsx", "const x = '\U0001F680';\n")
    assert not any(x["rule"] == "emoji_icon" for x in lint_file(p, ah, ar, conv))


def test_color_in_comment_not_flagged(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "A.swift", "// legacy was #ff0000 before the refactor\n")
    assert lint_file(p, ah, ar, conv) == []


def test_single_appearance_palette(tmp_path):
    tokens = {
        "schema_version": "aria.design-tokens.v1", "name": "S", "appearance": "single",
        "color": {"accent": "#00ff88"}, "radius": {"card": 10},
    }
    ah, ar, conv = load_allowed(tokens)
    assert "#00ff88" in ah
    p = _write(tmp_path, "A.css", "a { color: #00FF88; }\n")   # same, different case
    assert lint_file(p, ah, ar, conv) == []


def test_main_exit_code_1_on_error(tmp_path, capsys):
    import json
    tf = tmp_path / "tokens.json"
    tf.write_text(json.dumps(TOKENS), encoding="utf-8")
    _write(tmp_path, "Bad.css", "a { color: #ff0000; }\n")
    assert main(["--tokens", str(tf), "--paths", str(tmp_path)]) == 1


def test_rounding_equivalent_color_within_tolerance_is_clean(tmp_path):
    """SwiftUI float rounding (#2f6cff, dist 1 from accent #2f6bff) must not misreport."""
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "V.css", "a { color: #2f6cff; }\n")
    assert lint_file(p, ah, ar, conv) == []


def test_zero_tolerance_flags_rounding_difference(tmp_path):
    ah, ar, conv = _allowed()
    p = _write(tmp_path, "V.css", "a { color: #2f6cff; }\n")
    v = lint_file(p, ah, ar, conv, color_tolerance=0)
    assert any(x["rule"] == "color_off_system" for x in v)


def test_off_system_message_names_nearest_token(tmp_path):
    ah, ar, conv = _allowed()
    # a blue-ish off-system color should point at the accent token, not canvas
    p = _write(tmp_path, "V.css", "a { color: #3366e6; }\n")
    v = lint_file(p, ah, ar, conv)
    assert v and "nearest token: accent" in v[0]["message"]


def test_demo_runs_clean():
    result = subprocess.run(
        [sys.executable, str(FIXTURE_DIR / "design_lint.py"), "--demo"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "demo assertions passed" in result.stdout
