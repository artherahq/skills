"""poster_gate 测试: 九字段 compile 输出格式 + Quality Gate 的
FAIL/WARN/PASS 分支 + strength 推荐区间。"""

import pytest

from poster_gate import (
    audit_poster_spec,
    compile_prompt,
    demo,
    recommend_strength,
)


def test_demo_separates_commercial_prompt_from_minimal_editorial_compile():
    assert demo() == 0


def _base_good_spec():
    return {
        "subject": "test subject",
        "subject_keywords": ["lighthouse", "coast"],
        "canvas": "2:3 tall poster, aged matte paper ground",
        "negative_space_pct": 80,
        "anchor": "a solitary lighthouse silhouette",
        "anchor_is_photo": False,
        "anchor_treatment": "high-contrast silhouette",
        "typography": "serif, single word",
        "colors": [
            {"role": "anchor", "name": "rust red", "hex": "#A6472B",
             "source": "the lighthouse's real rust-streaked paint, per the brief"},
            {"role": "ground", "name": "fog grey", "hex": "#D8D5CE", "source": ""},
        ],
        "texture": "letterpress impression",
        "temperature": "quiet",
        "avoids": ["cinematic lighting", "commercial layout"],
    }


# ───────────────────────────── compile_prompt ─────────────────────────────

def test_compile_prompt_renders_all_nine_fields():
    out = compile_prompt(_base_good_spec())
    assert "Canvas:" in out
    assert "Attention geometry: 80%" in out
    assert "Anchor: a solitary lighthouse silhouette" in out
    assert "Typography:" in out
    assert "rust red" in out and "fog grey" in out
    assert "Texture: letterpress impression" in out
    assert "Temperature: quiet" in out
    assert "cinematic lighting" in out  # in the Avoid line, not leaked elsewhere


# ───────────────────────────── audit: negative space ──────────────────────

def test_negative_space_below_70_fails():
    spec = _base_good_spec()
    spec["negative_space_pct"] = 40
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "insufficient_negative_space" for f in result["findings"])


def test_negative_space_70_to_75_warns_not_fails():
    spec = _base_good_spec()
    spec["negative_space_pct"] = 72
    result = audit_poster_spec(spec)
    assert any(f["code"] == "borderline_negative_space" for f in result["findings"])
    assert not any(f["severity"] == "fail" for f in result["findings"])


def test_missing_negative_space_fails():
    spec = _base_good_spec()
    del spec["negative_space_pct"]
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "missing_negative_space_pct" for f in result["findings"])


# ───────────────────────────── audit: anchor ───────────────────────────────

def test_multiple_subjects_in_anchor_warns():
    spec = _base_good_spec()
    spec["anchor"] = "a lighthouse and a fishing boat and a gull"
    result = audit_poster_spec(spec)
    assert any(f["code"] == "possible_multiple_subjects" for f in result["findings"])


def test_missing_anchor_fails():
    spec = _base_good_spec()
    spec["anchor"] = ""
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "missing_anchor" for f in result["findings"])


# ───────────────────────────── audit: color ────────────────────────────────

def test_two_anchor_colors_fails():
    spec = _base_good_spec()
    spec["colors"].append({"role": "anchor", "name": "teal", "hex": "#116666", "source": "x"})
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "multiple_saturated_colors" for f in result["findings"])


def test_no_anchor_color_fails():
    spec = _base_good_spec()
    spec["colors"] = [{"role": "ground", "name": "fog grey"}]
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "no_anchor_color" for f in result["findings"])


def test_ungrounded_anchor_color_warns():
    spec = _base_good_spec()
    spec["colors"][0]["source"] = ""
    result = audit_poster_spec(spec)
    assert any(f["code"] == "anchor_color_not_grounded" for f in result["findings"])


# ───────────────────────────── audit: forbidden terms ──────────────────────

@pytest.mark.parametrize("field,term", [
    ("anchor_treatment", "cinematic lighting"),
    ("typography", "commercial"),
    ("texture", "glossy 3d"),
    ("temperature", "dramatic"),
])
def test_forbidden_term_leak_detected_per_field(field, term):
    spec = _base_good_spec()
    spec[field] = term
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "forbidden_term_leak" and term in f["message"] for f in result["findings"])


# ───────────────────────────── audit: genericness ──────────────────────────

def test_generic_anchor_not_tied_to_subject_fails():
    spec = _base_good_spec()
    spec["anchor"] = "a generic building silhouette"  # doesn't mention lighthouse/coast
    result = audit_poster_spec(spec)
    assert result["verdict"] == "FAIL"
    assert any(f["code"] == "generic_anchor" for f in result["findings"])


def test_no_subject_keywords_warns_and_skips_genericness_check():
    spec = _base_good_spec()
    spec["subject_keywords"] = []
    result = audit_poster_spec(spec)
    assert any(f["code"] == "no_subject_keywords" for f in result["findings"])
    assert not any(f["code"] == "generic_anchor" for f in result["findings"])


# ───────────────────────────── audit: clean spec ───────────────────────────

def test_well_formed_spec_passes():
    result = audit_poster_spec(_base_good_spec())
    assert result["verdict"] == "PASS"
    assert result["findings"] == []


# ───────────────────────────── strength recommendation ─────────────────────

def test_strength_recommendation_only_for_photo_anchor():
    spec = _base_good_spec()
    spec["anchor_is_photo"] = False
    result = audit_poster_spec(spec)
    assert "strength_recommendation" not in result

    spec["anchor_is_photo"] = True
    result = audit_poster_spec(spec)
    assert "strength_recommendation" in result


@pytest.mark.parametrize("treatment,expected_range", [
    ("full silhouette, line art only", (0.65, 0.75)),
    ("keeps the original composition close, conservative", (0.35, 0.45)),
    ("duotone, simplified background", (0.50, 0.60)),
])
def test_recommend_strength_keyword_routing(treatment, expected_range):
    result = recommend_strength(treatment)
    assert tuple(result["range"]) == expected_range
