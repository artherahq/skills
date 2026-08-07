"""verify_contrast 测试: WCAG 相对亮度公式 + 对比度重算 + 对照
color_palettes.md 打印值的 FAIL/PASS 分支，以及真实参考文件本身过检。"""

from pathlib import Path

from verify_contrast import (
    audit_palettes,
    contrast_ratio,
    demo,
    main,
    parse_palettes,
    relative_luminance,
)


def test_demo_catches_drifted_hex_against_printed_claim():
    assert demo() == 0


# ───────────────────────────── contrast math ───────────────────────────────

def test_black_on_white_is_max_contrast():
    ratio = contrast_ratio("#FFFFFF", "#000000")
    assert 20.9 <= ratio <= 21.1  # textbook WCAG value is 21:1


def test_same_color_has_ratio_one():
    ratio = contrast_ratio("#336699", "#336699")
    assert abs(ratio - 1.0) < 1e-9


def test_relative_luminance_white_is_one():
    assert abs(relative_luminance("#FFFFFF") - 1.0) < 1e-6


def test_relative_luminance_black_is_zero():
    assert abs(relative_luminance("#000000") - 0.0) < 1e-6


# ───────────────────────────── parsing ─────────────────────────────────────

def test_parse_palettes_extracts_roles_and_printed_ratio():
    text = """
## Test Palette

| Role | Hex |
| --- | --- |
| Primary | `#2563EB` |
| Background | `#F8FAFC` |
| Text | `#1E293B` |

Text on background: **13.98:1** (WCAG AA needs 4.5:1 for body text, 3:1 for large text)

Some description
"""
    palettes = parse_palettes(text)
    assert len(palettes) == 1
    assert palettes[0]["name"] == "Test Palette"
    assert palettes[0]["background"] == "#F8FAFC"
    assert palettes[0]["text"] == "#1E293B"
    assert palettes[0]["printed_ratio"] == 13.98


def test_parse_palettes_handles_multiple_blocks():
    text = """
## First

| Role | Hex |
| --- | --- |
| Background | `#FFFFFF` |
| Text | `#000000` |

Text on background: **21.00:1** (WCAG AA needs 4.5:1 for body text, 3:1 for large text)

## Second

| Role | Hex |
| --- | --- |
| Background | `#F8FAFC` |
| Text | `#1E293B` |

Text on background: **13.98:1** (WCAG AA needs 4.5:1 for body text, 3:1 for large text)
"""
    palettes = parse_palettes(text)
    assert [p["name"] for p in palettes] == ["First", "Second"]


def test_parse_palettes_missing_ratio_line_reports_none():
    text = """
## No Ratio Line

| Role | Hex |
| --- | --- |
| Background | `#FFFFFF` |
| Text | `#000000` |
"""
    palettes = parse_palettes(text)
    assert palettes[0]["printed_ratio"] is None


# ───────────────────────────── audit ───────────────────────────────────────

def test_audit_flags_missing_role_hex():
    palettes = [{"name": "Broken", "background": None, "text": "#000000", "printed_ratio": 21.0}]
    result = audit_palettes(palettes)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "missing_role_hex" for f in result["findings"])


def test_audit_flags_missing_printed_ratio():
    palettes = [{"name": "Broken", "background": "#FFFFFF", "text": "#000000", "printed_ratio": None}]
    result = audit_palettes(palettes)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "missing_printed_ratio" for f in result["findings"])


def test_audit_matching_ratio_passes():
    palettes = [{"name": "Good", "background": "#F8FAFC", "text": "#1E293B", "printed_ratio": 13.98}]
    result = audit_palettes(palettes)
    assert result["verdict"] == "PASS"
    assert result["findings"] == []


def test_audit_stale_printed_ratio_fails():
    # correct recomputed ratio for this hex pair is ~13.98, not 21.0
    palettes = [{"name": "Stale", "background": "#F8FAFC", "text": "#1E293B", "printed_ratio": 21.0}]
    result = audit_palettes(palettes)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "ratio_mismatch" for f in result["findings"])


def test_audit_rounding_tolerance_does_not_false_positive():
    # printed value rounded to 2dp should not trip the mismatch check
    exact = contrast_ratio("#F8FAFC", "#1E293B")
    palettes = [{"name": "Rounded", "background": "#F8FAFC", "text": "#1E293B",
                 "printed_ratio": round(exact, 2)}]
    result = audit_palettes(palettes)
    assert not any(f["code"] == "ratio_mismatch" for f in result["findings"])


# ───────────────────────────── real reference file ─────────────────────────

def test_real_color_palettes_file_passes_the_gate():
    path = Path(__file__).resolve().parent.parent / "references" / "color_palettes.md"
    text = path.read_text(encoding="utf-8")
    result = audit_palettes(parse_palettes(text))
    assert result["palette_count"] == 96
    assert result["verdict"] == "PASS", result["findings"]


def test_main_runs_against_default_path(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert '"verdict": "PASS"' in out
