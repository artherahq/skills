"""risk_profile 测试:demo 分离力 + 各统计方向性 + 诚实降级。"""

import numpy as np
import pandas as pd
import pytest

from risk_profile import (
    assess, concentration, cornish_fisher_var, demo, var_cvar, portfolio_returns,
)


def _rets(n=400, seed=5, cols=("A", "B", "C")):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=n)
    return pd.DataFrame({c: rng.normal(0.0003, 0.01, n) for c in cols}, index=idx)


def test_demo_separates_concentrated_from_diversified():
    assert demo() == 0


def test_var_ordering_and_cvar_beyond_var():
    r = np.random.default_rng(1).normal(0, 0.01, 2000)
    v95, c95 = var_cvar(r, 0.95)
    v99, _ = var_cvar(r, 0.99)
    assert v99 < v95 < 0          # 99% 分位更深
    assert c95 <= v95             # 尾内均值不浅于分位点


def test_cornish_fisher_widens_fat_tail_at_99():
    # CF 修正的教科书行为:超额峰度在 95% 分位可能收窄(t 分布中心质量也更多),
    # 在 99% 深尾必须显著加宽——用 99% 断言方向性。
    rng = np.random.default_rng(2)
    normal = rng.normal(0, 0.01, 5000)
    fat = rng.standard_t(3, 5000) * 0.01 / np.sqrt(3)   # 同方差量级的厚尾
    assert cornish_fisher_var(fat, 0.99) < cornish_fisher_var(normal, 0.99)


def test_concentration_effective_n():
    conc = concentration(pd.Series({"X": 0.5, "Y": 0.5}))
    assert conc["effective_n"] == pytest.approx(2.0)
    conc1 = concentration(pd.Series({"X": 1.0}))
    assert conc1["effective_n"] == pytest.approx(1.0)
    assert conc1["top_position"]["share"] == pytest.approx(1.0)


def test_single_name_concentration_flagged_high():
    rets = _rets()
    rep = assess(rets, pd.Series({"A": 0.7, "B": 0.2, "C": 0.1}))
    assert "single_name_concentration" in {f["code"] for f in rep["flags"]}


def test_correlated_book_flags_diversification_illusion():
    rng = np.random.default_rng(7)
    n = 400
    common = rng.normal(0.0003, 0.012, n)
    idx = pd.bdate_range("2024-01-02", periods=n)
    rets = pd.DataFrame({c: common + rng.normal(0, 0.002, n) for c in ("A", "B", "C", "D")},
                        index=idx)
    rep = assess(rets, pd.Series({"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25}))
    assert "diversification_illusion" in {f["code"] for f in rep["flags"]}


def test_no_benchmark_skips_shock_honestly():
    rep = assess(_rets(), pd.Series({"A": 0.4, "B": 0.3, "C": 0.3}))
    assert rep["stress"]["skipped"] is True
    assert "not fabricated" in rep["stress"]["reason"]


def test_gross_renormalization_disclosed():
    rets = _rets()
    port, notes = portfolio_returns(rets, pd.Series({"A": 1.0, "B": 1.0}))  # gross=2
    assert notes["weights_renormalized_from_gross"] == pytest.approx(2.0)
    assert len(port) == len(rets)


def test_disclosure_always_present():
    rep = assess(_rets(), pd.Series({"A": 0.5, "B": 0.5}))
    assert any("not individualized investment advice" in d for d in rep["disclosure"])


def test_too_short_history_errors():
    rep = assess(_rets(20), pd.Series({"A": 1.0}))
    assert rep["risk_level"] == "unknown" and "error" in rep
