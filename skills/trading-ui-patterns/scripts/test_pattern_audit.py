"""pattern_audit tests: required/recommended/forbidden field checks, numeric
and equality rules, the market-aware convention check (the core "silent
wrong color" failure mode this skill exists to catch), and the demo harness."""

import pytest

from pattern_audit import audit_manifest, demo, load_patterns


@pytest.fixture(scope="module")
def patterns():
    return load_patterns()


def test_demo_reproduces_the_market_convention_bug_and_the_fix():
    assert demo() == 0


# ───────────────────────────── unknown pattern ────────────────────────────

def test_unknown_pattern_fails_closed(patterns):
    report = audit_manifest({"pattern": "not_a_real_pattern", "fields": {}}, patterns)
    assert report["verdict"] == "FAIL"
    assert report["findings"][0]["code"] == "unknown_pattern"


# ───────────────────────────── required / recommended / forbidden ────────

def test_missing_required_field_is_a_fail(patterns):
    manifest = {
        "pattern": "x_timeline_post",
        "fields": {
            "avatar": True, "display_name": True, "handle": True,
            "timestamp": True, "body_text": True,
            # action_bar omitted
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "FAIL"
    codes = [f["code"] for f in report["findings"]]
    assert "missing_required_field" in codes


def test_all_required_present_with_no_recommended_is_warn_not_fail(patterns):
    manifest = {
        "pattern": "x_timeline_post",
        "fields": {
            "avatar": True, "display_name": True, "handle": True,
            "timestamp": True, "body_text": True, "action_bar": True,
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "WARN"
    assert all(f["severity"] == "warn" for f in report["findings"])


def test_fully_populated_component_passes_clean(patterns):
    manifest = {
        "pattern": "x_timeline_post",
        "fields": {
            "avatar": True, "display_name": True, "handle": True,
            "timestamp": True, "body_text": True, "action_bar": True,
            "media_embed": True, "reply_context": True,
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "PASS"
    assert report["findings"] == []


def test_forbidden_condition_present_is_a_fail(patterns):
    manifest = {
        "pattern": "x_action_bar",
        "fields": {
            "reply_action": True, "repost_action": True,
            "like_action": True, "share_action": True,
            "filled_icon_before_activation": True,
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "FAIL"
    assert any(f["code"] == "forbidden_condition_present" for f in report["findings"])


# ───────────────────────────── numeric / equality rules ───────────────────

def test_tap_target_below_minimum_fails(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "US",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_down_green_up",
            "tap_target_pt": 32,  # below the 44pt rule
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "FAIL"
    rule_findings = [f for f in report["findings"] if f["code"] == "rule_violation" and f["field"] == "tap_target_pt"]
    assert len(rule_findings) == 1


def test_rule_is_only_enforced_when_manifest_declares_the_field(patterns):
    # tap_target_pt omitted entirely -> no rule_violation finding for it,
    # since the audit only checks fields the manifest actually claims.
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "US",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_down_green_up",
        },
    }
    report = audit_manifest(manifest, patterns)
    assert not any(f["field"] == "tap_target_pt" for f in report["findings"])


# ───────────────────────────── market-aware convention check ─────────────

def test_us_convention_on_us_market_is_fine(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "US",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_down_green_up",
        },
    }
    report = audit_manifest(manifest, patterns)
    assert not any(f["code"] == "market_convention_mismatch" for f in report["findings"])


def test_us_convention_copied_onto_cn_market_is_flagged(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "CN",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_down_green_up",
        },
    }
    report = audit_manifest(manifest, patterns)
    assert report["verdict"] == "FAIL"
    mismatch = [f for f in report["findings"] if f["code"] == "market_convention_mismatch"]
    assert len(mismatch) == 1
    assert mismatch[0]["expected"] == "red_up_green_down"


def test_correct_convention_on_cn_market_is_not_flagged(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "CN",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_up_green_down",
        },
    }
    report = audit_manifest(manifest, patterns)
    assert not any(f["code"] == "market_convention_mismatch" for f in report["findings"])


def test_unspecified_market_falls_back_to_default_convention(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True, "direction_color": "red_down_green_up",
        },
    }
    report = audit_manifest(manifest, patterns)
    assert not any(f["code"] == "market_convention_mismatch" for f in report["findings"])


def test_market_aware_field_only_checked_when_manifest_declares_it(patterns):
    manifest = {
        "pattern": "tradingview_watchlist_row",
        "market": "CN",
        "fields": {
            "symbol": True, "price": True, "change_value": True,
            "change_percent": True,
            # direction_color omitted -> that's a missing_required_field,
            # not a market_convention_mismatch
        },
    }
    report = audit_manifest(manifest, patterns)
    assert not any(f["code"] == "market_convention_mismatch" for f in report["findings"])
    assert any(f["code"] == "missing_required_field" and f["field"] == "direction_color" for f in report["findings"])
