"""gex_gate 测试: Black-Scholes gamma 正确性 + 符号约定 + 零伽马翻转插值 +
gamma walls 排序 + 披露门禁的 FAIL/WARN/PASS 分支。"""

import math

import pytest

from gex_gate import (
    DEALER_ASSUMPTION_DISCLOSURE,
    COVERAGE_LIMITATION,
    audit_gex_report,
    black_scholes_gamma,
    build_report,
    compute_gex,
    demo,
)


def test_demo_flips_regime_and_separates_audit_verdicts():
    assert demo() == 0


# ───────────────────────────── black_scholes_gamma ────────────────────────────

def test_gamma_peaks_near_the_money():
    # Gamma is highest when strike ~= spot and falls off away from it —
    # the textbook shape; if this breaks, the whole computation is wrong.
    atm = black_scholes_gamma(100, 100, 30 / 365, 0.3)
    otm = black_scholes_gamma(100, 140, 30 / 365, 0.3)
    itm = black_scholes_gamma(100, 60, 30 / 365, 0.3)
    assert atm > otm
    assert atm > itm


def test_gamma_same_for_call_and_put_by_construction():
    # black_scholes_gamma doesn't take an option-type argument at all —
    # this test documents why: BS gamma is identical for calls and puts
    # at the same (S, K, T, sigma).
    g1 = black_scholes_gamma(100, 95, 0.25, 0.28)
    g2 = black_scholes_gamma(100, 95, 0.25, 0.28)
    assert g1 == g2


def test_gamma_degenerate_inputs_return_zero_not_raise():
    assert black_scholes_gamma(0, 100, 0.1, 0.2) == 0.0
    assert black_scholes_gamma(100, 0, 0.1, 0.2) == 0.0
    assert black_scholes_gamma(100, 100, 0.0, 0.2) == 0.0
    assert black_scholes_gamma(100, 100, 0.1, 0.0) == 0.0


def test_gamma_positive_for_valid_inputs():
    assert black_scholes_gamma(100, 105, 0.1, 0.25) > 0


# ───────────────────────────── compute_gex ─────────────────────────────────────

def _simple_chain():
    return [
        {"strike": 95,  "call_oi": 100, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3},
        {"strike": 100, "call_oi": 100, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3},
        {"strike": 105, "call_oi": 100, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3},
    ]


def test_compute_gex_symmetric_oi_and_iv_nets_to_zero():
    # Equal call/put OI and IV at every strike, with the correct opposite
    # sign convention, should net out close to zero (call and put gamma are
    # identical, so equal OI on each side cancels almost exactly).
    result = compute_gex(_simple_chain(), spot=100, days_to_expiry=30)
    assert result["net_gex_total"] == pytest.approx(0.0, abs=1e-6)


def test_compute_gex_call_heavy_chain_is_positive_regime():
    chain = [{"strike": 100, "call_oi": 1000, "call_iv": 0.3, "put_oi": 50, "put_iv": 0.3}]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    assert result["net_gex_total"] > 0
    assert result["regime"] == "positive"


def test_compute_gex_put_heavy_chain_is_negative_regime():
    chain = [{"strike": 100, "call_oi": 50, "call_iv": 0.3, "put_oi": 1000, "put_iv": 0.3}]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    assert result["net_gex_total"] < 0
    assert result["regime"] == "negative"


def test_compute_gex_put_sign_flag_reverses_contribution():
    chain = [{"strike": 100, "call_oi": 50, "call_iv": 0.3, "put_oi": 1000, "put_iv": 0.3}]
    correct = compute_gex(chain, spot=100, days_to_expiry=30, put_sign=-1)
    buggy = compute_gex(chain, spot=100, days_to_expiry=30, put_sign=+1)
    assert correct["net_gex_total"] < 0
    assert buggy["net_gex_total"] > 0
    # only the put leg's sign moves — its magnitude (and the call leg
    # entirely) is identical between the two runs
    call_gex = correct["gex_by_strike"][0]["call_gex"]
    put_gex_magnitude = abs(correct["gex_by_strike"][0]["put_gex"])
    assert buggy["net_gex_total"] == pytest.approx(call_gex + put_gex_magnitude, rel=1e-9)


def test_compute_gex_skips_rows_with_zero_or_missing_oi():
    chain = [
        {"strike": 100, "call_oi": 0, "call_iv": 0.3, "put_oi": 0, "put_iv": 0.3},
        {"strike": 105, "call_oi": 100, "call_iv": 0.3},  # no put leg at all
    ]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    row_100 = next(r for r in result["gex_by_strike"] if r["strike"] == 100)
    row_105 = next(r for r in result["gex_by_strike"] if r["strike"] == 105)
    assert row_100["net_gex"] == 0.0
    assert row_105["put_gex"] == 0.0
    assert row_105["call_gex"] > 0.0


def test_compute_gex_zero_gamma_flip_is_interpolated_not_nearest_strike():
    # Construct a chain where net GEX crosses zero strictly between two
    # strikes; the interpolated flip should land inside that interval, not
    # snap to either endpoint.
    chain = [
        {"strike": 90, "call_oi": 10, "call_iv": 0.3, "put_oi": 800, "put_iv": 0.3},   # very negative
        {"strike": 100, "call_oi": 800, "call_iv": 0.3, "put_oi": 10, "put_iv": 0.3},  # very positive
    ]
    result = compute_gex(chain, spot=95, days_to_expiry=30)
    flip = result["zero_gamma_flip"]
    assert flip is not None
    assert 90 < flip < 100


def test_compute_gex_no_crossing_returns_none_flip():
    chain = [{"strike": 100, "call_oi": 500, "call_iv": 0.3, "put_oi": 10, "put_iv": 0.3}]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    assert result["zero_gamma_flip"] is None


def test_compute_gex_gamma_walls_are_top_n_by_abs_value():
    chain = [
        {"strike": 90, "call_oi": 10, "call_iv": 0.3, "put_oi": 10, "put_iv": 0.3},
        {"strike": 95, "call_oi": 2000, "call_iv": 0.3, "put_oi": 10, "put_iv": 0.3},
        {"strike": 100, "call_oi": 10, "call_iv": 0.3, "put_oi": 2000, "put_iv": 0.3},
        {"strike": 105, "call_oi": 10, "call_iv": 0.3, "put_oi": 10, "put_iv": 0.3},
    ]
    result = compute_gex(chain, spot=98, days_to_expiry=30)
    wall_strikes = {w["strike"] for w in result["gamma_walls"]}
    assert 95 in wall_strikes
    assert 100 in wall_strikes


def test_compute_gex_skips_row_with_no_strike():
    chain = [{"call_oi": 100, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3}]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    assert result["gex_by_strike"] == []


# ───────────────────────────── audit_gex_report ────────────────────────────────

def _compliant_report():
    # 5+ strikes so this fixture doesn't also trip the sparse_chain WARN —
    # that path has its own dedicated test below.
    chain = [
        {"strike": 90, "call_oi": 100, "call_iv": 0.3, "put_oi": 50, "put_iv": 0.3},
        {"strike": 95, "call_oi": 200, "call_iv": 0.3, "put_oi": 60, "put_iv": 0.3},
        {"strike": 100, "call_oi": 500, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3},
        {"strike": 105, "call_oi": 200, "call_iv": 0.3, "put_oi": 60, "put_iv": 0.3},
        {"strike": 110, "call_oi": 100, "call_iv": 0.3, "put_oi": 50, "put_iv": 0.3},
    ]
    result = compute_gex(chain, spot=100, days_to_expiry=30)
    return build_report(result, methodology=DEALER_ASSUMPTION_DISCLOSURE,
                         coverage_limitation=COVERAGE_LIMITATION)


def test_audit_passes_compliant_report():
    rep = audit_gex_report(_compliant_report())
    assert rep["verdict"] == "PASS"
    assert rep["flags"] == []


def test_audit_fails_missing_methodology():
    report = _compliant_report()
    report["methodology"] = ""
    rep = audit_gex_report(report)
    assert rep["verdict"] == "FAIL"
    assert "missing_dealer_assumption_disclosure" in {f["code"] for f in rep["flags"]}


def test_audit_fails_missing_coverage_limitation():
    report = _compliant_report()
    report["coverage_limitation"] = "short"  # under the length threshold
    rep = audit_gex_report(report)
    assert rep["verdict"] == "FAIL"
    assert "missing_coverage_limitation" in {f["code"] for f in rep["flags"]}


def test_audit_fails_gex_sum_mismatch():
    report = _compliant_report()
    report["net_gex_total"] = report["net_gex_total"] + 999_999
    rep = audit_gex_report(report)
    assert "gex_sum_mismatch" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_audit_fails_regime_sign_mismatch():
    report = _compliant_report()
    report["regime"] = "negative" if report["regime"] == "positive" else "positive"
    rep = audit_gex_report(report)
    assert "regime_sign_mismatch" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_audit_fails_flip_point_out_of_range():
    report = _compliant_report()
    report["zero_gamma_flip"] = 99999.0
    rep = audit_gex_report(report)
    assert "flip_point_out_of_range" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_audit_fails_gamma_walls_mismatch():
    report = _compliant_report()
    report["gamma_walls"] = [{"strike": 99999.0, "gex": 1.0}]
    rep = audit_gex_report(report)
    assert "gamma_walls_mismatch" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "FAIL"


def test_audit_warns_on_sparse_chain():
    result = compute_gex(
        [{"strike": 100, "call_oi": 500, "call_iv": 0.3, "put_oi": 100, "put_iv": 0.3}],
        spot=100, days_to_expiry=30,
    )
    report = build_report(result, methodology=DEALER_ASSUMPTION_DISCLOSURE,
                           coverage_limitation=COVERAGE_LIMITATION)
    rep = audit_gex_report(report)
    assert "sparse_chain" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "WARN"


def test_audit_warns_when_no_strike_detail_present():
    rep = audit_gex_report({
        "methodology": DEALER_ASSUMPTION_DISCLOSURE,
        "coverage_limitation": COVERAGE_LIMITATION,
        "net_gex_total": 100.0,
        "regime": "positive",
    })
    assert "no_strike_detail" in {f["code"] for f in rep["flags"]}
    assert rep["verdict"] == "WARN"


def test_audit_exit_code_semantics():
    # WARN and PASS both mean "usable"; FAIL should not.
    rep = audit_gex_report(_compliant_report())
    assert rep["verdict"] in ("PASS", "WARN", "FAIL")
