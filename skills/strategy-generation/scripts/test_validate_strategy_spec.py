"""validate_strategy_spec 测试:demo 分离 + 各门禁逐一验证。"""

import copy

from validate_strategy_spec import GOOD_SPEC, demo, validate


def _good():
    return copy.deepcopy(GOOD_SPEC)


def test_demo_gate_separates_spec_from_mood():
    assert demo() == 0


def test_good_spec_passes_clean():
    rep = validate(_good())
    assert rep["verdict"] == "PASS" and rep["flags"] == []
    assert rep["next_step"] == "implement_then_backtest-validation"


def test_missing_risk_control_fails():
    s = _good()
    s["risk_control"] = {"note": "trust me"}
    rep = validate(s)
    assert rep["verdict"] == "FAIL"
    assert "no_hard_risk_control" in {f["code"] for f in rep["flags"]}


def test_gross_only_costs_fail():
    s = _good()
    s["costs_bps"] = 0
    assert "gross_only" in {f["code"] for f in validate(s)["flags"]}


def test_forbidden_language_fails_anywhere():
    s = _good()
    s["signal"]["entry_logic"] += " — this setup is basically risk-free"
    rep = validate(s)
    assert rep["verdict"] == "FAIL"
    assert "forbidden_claim" in {f["code"] for f in rep["flags"]}


def test_forbidden_language_chinese():
    s = _good()
    s["strategy_name"] = "稳赚动量策略"
    assert "forbidden_claim" in {f["code"] for f in validate(s)["flags"]}


def test_overfit_preflight_param_budget():
    s = _good()
    s["signal"]["parameters"] = {f"p{i}": i for i in range(1, 40)}  # 39 参数
    s["data_requirements"]["history_periods"] = 40
    s["universe"] = ["BTC-USD"]                                     # 40 obs / 39 params
    rep = validate(s)
    assert "overfit_preflight" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_pit_pending_warns_not_fails():
    s = _good()
    s["data_requirements"]["pit_reviewed"] = False
    rep = validate(s)
    assert rep["verdict"] == "WARN"
    assert "pit_pending" in {f["code"] for f in rep["flags"]}


def test_trials_zero_fails():
    s = _good()
    s["variants_tried"] = 0
    assert "trials_undisclosed" in {f["code"] for f in validate(s)["flags"]}


def test_missing_field_reported():
    s = _good()
    del s["costs_bps"]
    rep = validate(s)
    assert rep["verdict"] == "FAIL"
    assert "missing_field" in {f["code"] for f in rep["flags"]}
