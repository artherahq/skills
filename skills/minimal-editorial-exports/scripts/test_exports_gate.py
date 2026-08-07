"""exports_gate 测试: 封面/首页 spec 的 compile 输出 + Checklist 的
FAIL/WARN/PASS 分支。"""

import pytest

from exports_gate import audit_export_spec, compile_brief, demo


def test_demo_separates_dense_cover_from_minimal_editorial_compile():
    assert demo() == 0


def _base_good_spec():
    return {
        "surface": "cover",
        "export_format": "html_pdf",
        "quiet_pct": 80,
        "focal_point": "headline return: +4.2%",
        "focal_point_type": "number",
        "accent_color": {"name": "signal green", "hex": "#1F8A4C",
                          "source": "this report's real positive return"},
        "typography": "Georgia headline, monospace caption",
        "texture": "subtle paper grain",
        "chrome_notes": "",
    }


def test_compile_brief_renders_all_fields():
    out = compile_brief(_base_good_spec())
    assert "Surface: cover (html_pdf)" in out
    assert "Quiet space: 80%" in out
    assert "signal green" in out
    assert "Georgia headline" in out
    assert "subtle paper grain" in out


def test_quiet_pct_below_70_fails():
    spec = _base_good_spec()
    spec["quiet_pct"] = 30
    result = audit_export_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "insufficient_quiet_space" for f in result["findings"])


def test_quiet_pct_70_to_75_warns_not_fails():
    spec = _base_good_spec()
    spec["quiet_pct"] = 72
    result = audit_export_spec(spec)
    assert any(f["code"] == "borderline_quiet_space" for f in result["findings"])
    assert not any(f["severity"] == "fail" for f in result["findings"])


def test_report_body_surface_fails():
    spec = _base_good_spec()
    spec["surface"] = "report_body"
    result = audit_export_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "wrong_surface_for_style" for f in result["findings"])


def test_missing_accent_color_fails():
    spec = _base_good_spec()
    del spec["accent_color"]
    result = audit_export_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "missing_accent_color" for f in result["findings"])


def test_ungrounded_accent_warns():
    spec = _base_good_spec()
    spec["accent_color"]["source"] = ""
    result = audit_export_spec(spec)
    assert any(f["code"] == "accent_not_grounded" for f in result["findings"])


def test_generic_sans_without_restraint_warns():
    spec = _base_good_spec()
    spec["typography"] = "Inter, system-ui"
    result = audit_export_spec(spec)
    assert any(f["code"] == "typography_reads_as_dashboard_default" for f in result["findings"])


def test_generic_sans_with_restraint_hint_does_not_warn():
    spec = _base_good_spec()
    spec["typography"] = "Inter for body, serif headline"
    result = audit_export_spec(spec)
    assert not any(f["code"] == "typography_reads_as_dashboard_default" for f in result["findings"])


def test_texture_on_pptx_fails():
    spec = _base_good_spec()
    spec["export_format"] = "pptx"
    result = audit_export_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "texture_unsupported_by_format" for f in result["findings"])


def test_texture_on_html_pdf_is_fine():
    spec = _base_good_spec()
    spec["export_format"] = "html_pdf"
    result = audit_export_spec(spec)
    assert not any(f["code"] == "texture_unsupported_by_format" for f in result["findings"])


@pytest.mark.parametrize("field,term", [
    ("focal_point", "sidebar navigation"),
    ("chrome_notes", "multi-panel grid"),
])
def test_borrowed_chrome_detected_per_field(field, term):
    spec = _base_good_spec()
    spec[field] = term
    result = audit_export_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "borrowed_dashboard_chrome" for f in result["findings"])


def test_batch_without_variation_warns():
    spec = _base_good_spec()
    spec["is_batch"] = True
    result = audit_export_spec(spec)
    assert any(f["code"] == "no_batch_variation_declared" for f in result["findings"])


def test_batch_with_variation_does_not_warn():
    spec = _base_good_spec()
    spec["is_batch"] = True
    spec["variation_axis"] = "focal_point_type"
    spec["variation_reason"] = "this symbol's story is a chart, not a number"
    result = audit_export_spec(spec)
    assert not any(f["code"] == "no_batch_variation_declared" for f in result["findings"])


def test_well_formed_spec_passes():
    result = audit_export_spec(_base_good_spec())
    assert result["verdict"] == "PASS"
    assert result["findings"] == []
