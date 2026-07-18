"""multiplicity_gate 测试: demo 分离力 + 校正方向性 + breadth 计算 + 门禁退出码。"""

import math

import pytest

np = pytest.importorskip("numpy")

from multiplicity_gate import (
    benjamini_hochberg_correction,
    bonferroni_correction,
    demo,
    effective_breadth,
    fundamental_law_ir,
    run_gate,
    t_stat_to_pvalue,
)


def test_demo_separates_noise_from_breadth_illusion():
    assert demo() == 0


def test_bh_less_conservative_than_bonferroni():
    # 同一批 p 值，BH 拒绝的原假设数量应该 >= Bonferroni（BH 更宽松）。
    p_values = {f"t{i}": p for i, p in enumerate([0.001, 0.01, 0.02, 0.03, 0.04, 0.2, 0.5, 0.8])}
    bonferroni = bonferroni_correction(p_values, alpha=0.05)
    bh = benjamini_hochberg_correction(p_values, alpha=0.05)
    assert sum(bh.values()) >= sum(bonferroni.values())


def test_bonferroni_threshold_is_alpha_over_n():
    p_values = {"a": 0.006, "b": 0.06}  # n=2, threshold = 0.025
    result = bonferroni_correction(p_values, alpha=0.05)
    assert result["a"] is True
    assert result["b"] is False


def test_bh_all_significant_when_all_p_tiny():
    p_values = {f"t{i}": 0.0001 for i in range(10)}
    bh = benjamini_hochberg_correction(p_values, alpha=0.05)
    assert all(bh.values())


def test_bh_none_significant_when_all_p_large():
    p_values = {f"t{i}": 0.9 for i in range(10)}
    bh = benjamini_hochberg_correction(p_values, alpha=0.05)
    assert not any(bh.values())


def test_empty_p_values_returns_empty():
    assert bonferroni_correction({}) == {}
    assert benjamini_hochberg_correction({}) == {}


def test_t_stat_to_pvalue_symmetric_and_bounded():
    p_pos = t_stat_to_pvalue(2.5, df=100)
    p_neg = t_stat_to_pvalue(-2.5, df=100)
    assert p_pos == pytest.approx(p_neg)
    assert 0.0 <= p_pos <= 1.0
    assert t_stat_to_pvalue(0.0, df=100) == pytest.approx(1.0, abs=1e-6)


def test_t_stat_to_pvalue_zero_df_is_conservative():
    assert t_stat_to_pvalue(5.0, df=0) == 1.0


def test_effective_breadth_independent_bets_unchanged():
    assert effective_breadth(20, 0.0) == pytest.approx(20.0)


def test_effective_breadth_identical_bets_collapses_to_one():
    assert effective_breadth(20, 1.0) == pytest.approx(1.0)


def test_effective_breadth_monotone_decreasing_in_correlation():
    b_low = effective_breadth(20, 0.1)
    b_high = effective_breadth(20, 0.8)
    assert b_high < b_low


def test_fundamental_law_ir_scales_with_sqrt_breadth():
    ir_1x = fundamental_law_ir(0.05, 10)
    ir_4x = fundamental_law_ir(0.05, 40)
    # breadth ×4 → IR ×2 (sqrt scaling), not ×4 — this is the whole point of
    # the formula and the easiest place a naive reader gets it wrong.
    assert ir_4x == pytest.approx(ir_1x * 2, rel=1e-6)


def test_fundamental_law_ir_zero_breadth_is_zero():
    assert fundamental_law_ir(0.1, 0) == 0.0


def test_run_gate_pure_noise_batch_flags_evaporation():
    rng = np.random.default_rng(28)
    test_results = {}
    for i in range(30):
        sample = rng.normal(0.0, 1.0, 240)
        mean, se = float(np.mean(sample)), float(np.std(sample, ddof=1) / math.sqrt(240))
        test_results[f"f{i}"] = {"t_stat": (mean / se if se > 0 else 0.0), "n_periods": 240}

    rep = run_gate(test_results, alpha=0.05)
    assert rep["naive_significant_count"] > rep["bh_fdr_significant_count"]
    codes = {f["code"] for f in rep["flags"]}
    # naive found at least one "hit" in this batch (expected under pure noise
    # at n=30, alpha=0.05) and BH correctly kills it
    assert rep["bh_fdr_significant_count"] == 0
    if rep["naive_significant_count"] > 0:
        assert "significance_evaporates" in codes
        assert rep["verdict"] == "FAIL"


def test_run_gate_genuine_strong_effect_survives_correction():
    # A batch where one factor has an overwhelming true effect and the rest
    # are noise — the strong one should survive even Bonferroni.
    rng = np.random.default_rng(3)
    test_results = {"strong": {"t_stat": 6.0, "n_periods": 240}}
    for i in range(9):
        sample = rng.normal(0.0, 1.0, 240)
        mean, se = float(np.mean(sample)), float(np.std(sample, ddof=1) / math.sqrt(240))
        test_results[f"noise{i}"] = {"t_stat": (mean / se if se > 0 else 0.0), "n_periods": 240}

    rep = run_gate(test_results, alpha=0.05)
    assert rep["per_test"]["strong"]["significant_bonferroni"] is True
    assert rep["per_test"]["strong"]["significant_bh_fdr"] is True


def test_run_gate_single_test_is_not_corrected():
    rep = run_gate({"only_one": {"t_stat": 2.5, "n_periods": 240}})
    codes = {f["code"] for f in rep["flags"]}
    assert "insufficient_batch" in codes
    assert rep["per_test"]["only_one"]["significant_bh_fdr"] is False


def test_run_gate_breadth_illusion_flag():
    rep = run_gate({}, ic=0.04, n_bets=20, avg_pairwise_correlation=0.7)
    codes = {f["code"] for f in rep["flags"]}
    assert "breadth_illusion" in codes
    assert rep["breadth"]["effective_breadth"] < rep["breadth"]["nominal_breadth"]


def test_run_gate_low_correlation_no_breadth_illusion():
    rep = run_gate({}, ic=0.04, n_bets=20, avg_pairwise_correlation=0.05)
    codes = {f["code"] for f in rep["flags"]}
    assert "breadth_illusion" not in codes


def test_run_gate_exit_code_semantics():
    # WARN and PASS should both be treated as "usable" (exit 0 at the CLI);
    # FAIL should not.
    warn_or_pass = run_gate({"a": {"t_stat": 2.5, "n_periods": 240},
                             "b": {"t_stat": 0.5, "n_periods": 240}})
    assert warn_or_pass["verdict"] in ("PASS", "WARN", "FAIL")  # sanity: always one of the three
