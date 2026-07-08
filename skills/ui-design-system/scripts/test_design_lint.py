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
    "type": {"body": {"size": 15}, "headline": {"size": 17}},
    "spacing": {"base": 4, "steps": {"sm": 8, "lg": 16}},
}


def _allowed(tokens=None):
    return load_allowed(tokens or TOKENS)


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ─────────────────────────── color ──────────────────────────────────────────
def test_in_palette_color_is_clean(tmp_path):
    p = _write(tmp_path, "A.css", "a { color: #2F6BFF; }\n")
    assert lint_file(p, _allowed()) == []


def test_off_palette_hex_flagged(tmp_path):
    p = _write(tmp_path, "A.css", "a { color: #ff0000; }\n")
    v = lint_file(p, _allowed())
    assert any(x["rule"] == "color_off_system" for x in v)


def test_swiftui_rgb_literal_normalized_and_checked(tmp_path):
    p = _write(tmp_path, "V.swift", "Color(red: 0.2, green: 0.6, blue: 0.9)\n")
    v = lint_file(p, _allowed())
    assert any(x["rule"] == "color_off_system" for x in v)


def test_css_rgb_matches_palette(tmp_path):
    p = _write(tmp_path, "A.css", "a { color: rgb(47, 107, 255); }\n")  # == #2f6bff
    assert not any(x["rule"] == "color_off_system" for x in lint_file(p, _allowed()))


def test_color_in_comment_not_flagged(tmp_path):
    p = _write(tmp_path, "A.swift", "// legacy was #ff0000 before the refactor\n")
    assert lint_file(p, _allowed()) == []


def test_color_hex_initializer_without_hash_flagged(tmp_path):
    """Color(hex: "64748B") — the # is omitted, must still be caught."""
    p = _write(tmp_path, "V.swift", 'let c = Color(hex: "64748B")\n')
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "color_off_system"]
    assert v and "#64748b" in v[0]["message"]


def test_color_hex_initializer_in_palette_is_clean(tmp_path):
    p = _write(tmp_path, "V.swift", 'let c = Color(hex: "2f6bff")\n')  # accent, no hash
    assert not any(x["rule"] == "color_off_system" for x in lint_file(p, _allowed()))


def test_chromatic_named_color_flagged_as_warn(tmp_path):
    p = _write(tmp_path, "V.swift", "Circle().fill(Color.green)\n")
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "named_color_off_system"]
    assert v and v[0]["severity"] == "warn" and "green" in v[0]["message"]


def test_neutral_named_colors_not_flagged(tmp_path):
    """white/black/gray/clear are structural — not chromatic brand hues, so not flagged."""
    p = _write(tmp_path, "V.swift", "Color.white.opacity(0.5); Color.black; Color.clear\n")
    assert not any(x["rule"] == "named_color_off_system" for x in lint_file(p, _allowed()))


def test_rounding_equivalent_color_within_tolerance_is_clean(tmp_path):
    p = _write(tmp_path, "V.css", "a { color: #2f6cff; }\n")   # dist 1 from accent
    assert not any(x["rule"] == "color_off_system" for x in lint_file(p, _allowed()))


def test_zero_tolerance_flags_rounding_difference(tmp_path):
    p = _write(tmp_path, "V.css", "a { color: #2f6cff; }\n")
    v = lint_file(p, _allowed(), color_tolerance=0)
    assert any(x["rule"] == "color_off_system" for x in v)


def test_off_system_message_names_nearest_token(tmp_path):
    p = _write(tmp_path, "V.css", "a { color: #3366e6; }\n")
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "color_off_system"]
    assert v and "nearest token: accent" in v[0]["message"]


# ─────────────────────────── radius ─────────────────────────────────────────
def test_radius_off_system_is_warn(tmp_path):
    p = _write(tmp_path, "A.css", ".x { border-radius: 20px; }\n")
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "radius_off_system"]
    assert v and v[0]["severity"] == "warn"


def test_declared_radius_is_clean(tmp_path):
    p = _write(tmp_path, "A.css", ".x { border-radius: 12px; }\n")
    assert not any(x["rule"] == "radius_off_system" for x in lint_file(p, _allowed()))


# ─────────────────────────── font size ──────────────────────────────────────
def test_off_system_font_size_flagged(tmp_path):
    p = _write(tmp_path, "V.swift", ".font(.system(size: 14))\n")
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "font_size_off_system"]
    assert v and v[0]["severity"] == "warn"
    assert "nearest:" in v[0]["message"]


def test_declared_font_size_is_clean(tmp_path):
    p = _write(tmp_path, "V.swift", ".font(.system(size: 17))\n")  # headline
    assert not any(x["rule"] == "font_size_off_system" for x in lint_file(p, _allowed()))


def test_css_font_size_checked(tmp_path):
    p = _write(tmp_path, "A.css", "p { font-size: 14px; }\n")
    assert any(x["rule"] == "font_size_off_system" for x in lint_file(p, _allowed()))


def test_font_size_not_linted_when_type_absent(tmp_path):
    tokens = dict(TOKENS)
    tokens = {k: v for k, v in TOKENS.items() if k != "type"}
    p = _write(tmp_path, "V.swift", ".font(.system(size: 99))\n")
    assert not any(x["rule"] == "font_size_off_system" for x in lint_file(p, _allowed(tokens)))


# ─────────────────────────── spacing ────────────────────────────────────────
def test_off_system_padding_flagged(tmp_path):
    p = _write(tmp_path, "V.swift", ".padding(15)\n")
    v = [x for x in lint_file(p, _allowed()) if x["rule"] == "spacing_off_system"]
    assert v and v[0]["severity"] == "warn"
    assert "nearest: lg 16" in v[0]["message"]


def test_declared_padding_is_clean(tmp_path):
    p = _write(tmp_path, "V.swift", ".padding(16)\n")   # lg
    assert not any(x["rule"] == "spacing_off_system" for x in lint_file(p, _allowed()))


def test_padding_with_edge_argument_checked(tmp_path):
    p = _write(tmp_path, "V.swift", ".padding(.horizontal, 15)\n")
    assert any(x["rule"] == "spacing_off_system" for x in lint_file(p, _allowed()))


def test_css_gap_checked(tmp_path):
    p = _write(tmp_path, "A.css", ".row { gap: 8px; }\n")   # sm → clean
    assert not any(x["rule"] == "spacing_off_system" for x in lint_file(p, _allowed()))


# ─────────────────────────── emoji ──────────────────────────────────────────
def test_emoji_forbidden_by_default(tmp_path):
    p = _write(tmp_path, "A.tsx", "const x = '\U0001F680';\n")
    assert any(x["rule"] == "emoji_icon" for x in lint_file(p, _allowed()))


def test_emoji_allowed_when_convention_permits(tmp_path):
    tokens = dict(TOKENS, conventions={"emoji_icons": "allow"})
    p = _write(tmp_path, "A.tsx", "const x = '\U0001F680';\n")
    assert not any(x["rule"] == "emoji_icon" for x in lint_file(p, _allowed(tokens)))


# ─────────────────────────── single appearance / plumbing ───────────────────
def test_single_appearance_palette(tmp_path):
    tokens = {
        "schema_version": "aria.design-tokens.v1", "name": "S", "appearance": "single",
        "color": {"accent": "#00ff88"}, "radius": {"card": 10},
    }
    allowed = load_allowed(tokens)
    assert "#00ff88" in allowed.colors
    p = _write(tmp_path, "A.css", "a { color: #00FF88; }\n")   # same, different case
    assert lint_file(p, allowed) == []


def test_main_exit_code_1_on_error(tmp_path):
    import json
    tf = tmp_path / "tokens.json"
    tf.write_text(json.dumps(TOKENS), encoding="utf-8")
    _write(tmp_path, "Bad.css", "a { color: #ff0000; }\n")
    assert main(["--tokens", str(tf), "--paths", str(tmp_path)]) == 1


def test_main_exit_code_0_when_only_warnings(tmp_path):
    import json
    tf = tmp_path / "tokens.json"
    tf.write_text(json.dumps(TOKENS), encoding="utf-8")
    _write(tmp_path, "Bad.swift", ".padding(15)\n.cornerRadius(14)\n")  # only warns
    assert main(["--tokens", str(tf), "--paths", str(tmp_path)]) == 0


def test_demo_runs_clean():
    result = subprocess.run(
        [sys.executable, str(FIXTURE_DIR / "design_lint.py"), "--demo"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "demo assertions passed" in result.stdout
