"""design_tokens validator tests: contrast math, scale checks, schema shape."""

import json

from design_tokens import TEMPLATE, contrast_ratio, extract, main, validate


def test_template_is_valid():
    assert validate(TEMPLATE)["valid"]


def test_contrast_black_on_white_is_maximal():
    # WCAG max ratio is 21:1
    assert round(contrast_ratio("#000000", "#FFFFFF")) == 21


def test_contrast_is_symmetric():
    assert contrast_ratio("#123456", "#abcdef") == contrast_ratio("#abcdef", "#123456")


def test_low_contrast_body_text_flagged():
    t = json.loads(json.dumps(TEMPLATE))
    t["color"]["textSecondary"] = {"light": "#CCCCCC", "dark": "#AAAAAA"}  # too light on white
    rep = validate(t)
    assert not rep["valid"]
    assert any("contrast" in e for e in rep["errors"])


def test_colliding_radius_tiers_flagged():
    t = json.loads(json.dumps(TEMPLATE))
    t["radius"]["control"] = t["radius"]["chip"]  # duplicate value
    rep = validate(t)
    assert any("radius" in e for e in rep["errors"])


def test_spacing_non_multiple_flagged():
    t = json.loads(json.dumps(TEMPLATE))
    t["spacing"]["steps"]["weird"] = 5  # base is 8
    rep = validate(t)
    assert any("multiple" in e for e in rep["errors"])


def test_single_appearance_accepts_string_colors():
    t = {
        "schema_version": "aria.design-tokens.v1", "name": "S", "appearance": "single",
        "color": {"canvas": "#FFFFFF", "textPrimary": "#000000"},
        "contrast_pairs": [{"text": "textPrimary", "on": "canvas", "min": 4.5}],
    }
    rep = validate(t)
    assert rep["valid"], rep["errors"]
    assert rep["contrast"] and rep["contrast"][0]["pass"]


def test_light_dark_requires_both_modes():
    t = {
        "schema_version": "aria.design-tokens.v1", "name": "S", "appearance": "light-dark",
        "color": {"canvas": "#FFFFFF"},  # string, but mode is light-dark
    }
    rep = validate(t)
    assert not rep["valid"]
    assert any("light-dark" in e for e in rep["errors"])


def test_missing_required_field_flagged():
    rep = validate({"appearance": "single", "color": {}})
    assert any("name" in e for e in rep["errors"])


def test_cli_validate_exit_codes(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(TEMPLATE), encoding="utf-8")
    assert main(["--validate", str(good)]) == 0

    bad = json.loads(json.dumps(TEMPLATE))
    bad["spacing"]["steps"]["weird"] = 5
    badf = tmp_path / "bad.json"
    badf.write_text(json.dumps(bad), encoding="utf-8")
    assert main(["--validate", str(badf)]) == 1


def test_template_cli_prints_json(capsys):
    assert main(["--template"]) == 0
    out = capsys.readouterr().out
    assert json.loads(out)["schema_version"] == "aria.design-tokens.v1"


# ─────────────────────────── extract ────────────────────────────────────────
def test_extract_clusters_near_duplicate_colors(tmp_path):
    (tmp_path / "a.css").write_text(
        "a { color: #2F6BFF; }\n.b { color: #2f6cff; }\n", encoding="utf-8")  # dist 1 → one token
    draft = extract([str(tmp_path)])
    assert len(draft["color"]) == 1


def test_extract_keeps_distinct_colors_separate(tmp_path):
    (tmp_path / "a.css").write_text(
        "a { color: #2f6bff; }\nb { color: #1db954; }\n", encoding="utf-8")  # far apart
    draft = extract([str(tmp_path)])
    assert len(draft["color"]) == 2


def test_extract_normalizes_swift_and_css_rgb(tmp_path):
    (tmp_path / "v.swift").write_text(
        "Color(red: 0.184, green: 0.42, blue: 1.0)\n", encoding="utf-8")   # ~#2f6bff
    (tmp_path / "a.css").write_text("a { color: rgb(47,107,255); }\n", encoding="utf-8")  # #2f6bff
    draft = extract([str(tmp_path)])
    # the swift-rounded blue and the css blue fold into the same cluster
    assert len(draft["color"]) == 1


def test_extract_orders_radii_by_frequency(tmp_path):
    (tmp_path / "a.css").write_text(
        ".x { border-radius: 12px; }\n.y { border-radius: 12px; }\n.z { border-radius: 8px; }\n",
        encoding="utf-8")
    draft = extract([str(tmp_path)])
    assert draft["radius"]["radius_1"] == 12  # most frequent first


def test_extract_draft_validates_once_named(tmp_path):
    (tmp_path / "a.css").write_text("a { color: #2f6bff; }\n", encoding="utf-8")
    draft = extract([str(tmp_path)])
    draft["name"] = "Named"
    assert validate(draft)["valid"]


def test_extract_cli(tmp_path, capsys):
    (tmp_path / "a.css").write_text("a { color: #2f6bff; }\n", encoding="utf-8")
    assert main(["--extract", str(tmp_path)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["appearance"] == "single"
    assert "#2f6bff" in out["color"].values()
