"""position_gate 测试:demo 分离 + 各闸门逐一验证 + paper 封顶。"""

import copy

import pytest

from position_gate import GOOD, KELLY_CAP, demo, run_gate, size_kelly, size_vol_target


def _good():
    return copy.deepcopy(GOOD)


def test_demo_gate_separates_discipline_from_yolo():
    assert demo() == 0


def test_good_spec_emits_paper_intent():
    rep = run_gate(_good())
    assert rep["verdict"] in ("PASS", "WARN")
    assert rep["intent"]["paper_only"] is True
    assert rep["intent"]["delta_weight"] > 0


def test_live_execution_refused():
    s = _good()
    s["order"]["execution"] = "live"
    rep = run_gate(s)
    assert rep["verdict"] == "FAIL"
    assert "live_execution_refused" in {f["code"] for f in rep["flags"]}
    assert rep["intent"] is None


def test_vol_target_math():
    # 2% 风险预算 / 28% 年化波动 ≈ 7.1% 权重
    assert size_vol_target(0.02, 0.28) == pytest.approx(0.0714, abs=1e-3)


def test_kelly_requires_declared_edge():
    s = _good()
    s["order"]["sizing"] = {"method": "kelly"}
    rep = run_gate(s)
    assert "kelly_without_declared_edge" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_kelly_fraction_capped():
    w_full = size_kelly(0.60, 2.0, fraction=1.0)
    w_kelly = 0.60 - 0.40 / 2.0  # f* = 0.4
    assert w_full == pytest.approx(w_kelly * KELLY_CAP)


def test_position_limit_blocks():
    s = _good()
    s["portfolio"]["positions"]["AAPL"] = 0.19   # 已接近上限
    s["order"]["sizing"] = {"method": "fixed_weight", "weight": 0.10}
    rep = run_gate(s)
    assert "position_limit" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_gross_exposure_blocks():
    s = _good()
    s["portfolio"]["positions"] = {"MSFT": 0.5, "NVDA": 0.45}
    s["order"]["sizing"] = {"method": "fixed_weight", "weight": 0.15}
    rep = run_gate(s)
    assert "gross_exposure_limit" in {f["code"] for f in rep["flags"]}


def test_insufficient_cash_blocks():
    s = _good()
    s["portfolio"]["cash"] = 1_000
    rep = run_gate(s)
    assert "insufficient_cash" in {f["code"] for f in rep["flags"]}


def test_noise_stop_warned():
    s = _good()
    s["order"]["stop_price"] = 229.9   # 0.04% 距离 << 日 sigma
    rep = run_gate(s)
    assert "noise_stop" in {f["code"] for f in rep["flags"]}


def test_liquidity_gate():
    s = _good()
    s["market"]["adv_shares"] = 100    # 极小 ADV
    rep = run_gate(s)
    assert "liquidity_limit" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_liquidity_skipped_honestly_without_adv():
    s = _good()
    del s["market"]["adv_shares"]
    rep = run_gate(s)
    assert rep["liquidity"]["skipped"] is True


def test_no_vol_refuses_to_guess():
    s = _good()
    del s["market"]["ann_vol"]
    rep = run_gate(s)
    assert "no_volatility" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"
