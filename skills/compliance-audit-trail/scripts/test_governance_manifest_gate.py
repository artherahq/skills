"""governance_manifest_gate 测试: demo 分离 + 各门禁逐一验证。"""

import copy
from datetime import datetime, timedelta

from governance_manifest_gate import DISCLOSED_MANIFEST, HOLLOW_MANIFEST, demo, validate


def _good():
    return copy.deepcopy(DISCLOSED_MANIFEST)


def test_demo_gate_separates_disclosure_from_hollow_claims():
    assert demo() == 0


def test_disclosed_manifest_passes_or_warns():
    rep = validate(_good())
    assert rep["verdict"] in ("PASS", "WARN")


def test_hollow_manifest_fails():
    rep = validate(copy.deepcopy(HOLLOW_MANIFEST))
    assert rep["verdict"] == "FAIL"
    assert rep["next_step"] == "fix_manifest_or_system"


def test_missing_required_field_fails_fast():
    m = _good()
    del m["audit_trail"]
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "missing_field" in codes
    assert rep["verdict"] == "FAIL"


def test_claim_without_evidence_flags_unverifiable():
    m = _good()
    m["capability_claims"].append({"claim": "we are very good at this", "evidence": ""})
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "unverifiable_claim" in codes
    assert rep["verdict"] == "FAIL"


def test_claim_with_evidence_does_not_flag():
    m = _good()
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "unverifiable_claim" not in codes


def test_production_scope_missing_gate_fails():
    m = _good()
    m["production_scope"].append({"asset": "TSLA", "passed_gates": ["ic_significance"]})
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "production_scope_gate_missing" in codes
    detail = next(f["detail"] for f in rep["flags"] if f["code"] == "production_scope_gate_missing")
    assert "TSLA" in detail


def test_production_scope_all_gates_passed_does_not_flag():
    m = _good()
    m["production_scope"] = [{"asset": "AAPL", "passed_gates": list(m["required_gates"])}]
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "production_scope_gate_missing" not in codes


def test_declared_risk_control_without_verification_fails():
    m = _good()
    m["risk_controls"].append({"name": "kill_switch", "declared_present": True, "verified_triggering": False})
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "unverified_safety_mechanism" in codes
    assert rep["verdict"] == "FAIL"


def test_risk_control_not_declared_present_is_silently_skipped():
    # A control that's honestly marked "not present" isn't a governance gap by
    # itself — the gate isn't in the business of requiring every possible
    # control, only verifying the ones actually claimed.
    m = _good()
    m["risk_controls"].append({"name": "not_built_yet", "declared_present": False})
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "unverified_safety_mechanism" not in codes


def test_verified_control_without_evidence_warns_not_fails():
    m = _good()
    m["risk_controls"] = [
        {"name": "x", "declared_present": True, "verified_triggering": True, "evidence": ""}
    ]
    rep = validate(m)
    flag = next(f for f in rep["flags"] if f["code"] == "safety_evidence_thin")
    assert flag["severity"] == "warn"


def test_no_audit_trail_fails():
    m = _good()
    m["audit_trail"] = {"decision_log_exists": False}
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "no_audit_trail" in codes
    assert rep["verdict"] == "FAIL"


def test_unimplemented_compliance_check_warns_not_fails():
    m = _good()
    m["compliance_checks"] = [{"name": "aml", "implemented": False}]
    rep = validate(m)
    flag = next(f for f in rep["flags"] if f["code"] == "compliance_gap")
    assert flag["severity"] == "warn"
    assert rep["verdict"] == "WARN"  # nothing else in _good() should be flagging here


def test_empty_limitations_warns():
    m = _good()
    m["known_limitations"] = []
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "no_limitations_disclosed" in codes


def test_nonempty_limitations_does_not_flag():
    m = _good()
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "no_limitations_disclosed" not in codes


def test_stale_manifest_warns():
    m = _good()
    m["as_of"] = (datetime.now() - timedelta(days=200)).date().isoformat()
    rep = validate(m, staleness_days=90)
    codes = {f["code"] for f in rep["flags"]}
    assert "stale_manifest" in codes


def test_fresh_manifest_does_not_warn_stale():
    m = _good()
    m["as_of"] = datetime.now().date().isoformat()
    rep = validate(m, staleness_days=90)
    codes = {f["code"] for f in rep["flags"]}
    assert "stale_manifest" not in codes


def test_unparseable_as_of_warns():
    m = _good()
    m["as_of"] = "not-a-date"
    rep = validate(m)
    codes = {f["code"] for f in rep["flags"]}
    assert "unparseable_as_of" in codes


def test_verdict_pass_when_no_flags():
    m = _good()
    m["capability_claims"] = []  # nothing to flag; avoid the AML compliance_gap warning too
    m["compliance_checks"] = [{"name": "risk_limit_check", "implemented": True}]
    rep = validate(m)
    assert rep["verdict"] == "PASS"
    assert rep["flags"] == []
