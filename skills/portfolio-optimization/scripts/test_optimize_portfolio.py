"""optimize_portfolio 测试:各引擎数学性质 + 结构感知 + 诚实披露。"""

import numpy as np
import pandas as pd
import pytest

from optimize_portfolio import (
    apply_cap, demo, optimize, shrunk_cov, w_erc, w_hrp, w_minvar, _project_simplex,
)


def _cov(seed=1, n=5, t=400):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, 0.01, (t, n)) @ np.diag(np.linspace(0.8, 1.5, n))
    return np.cov(r, rowvar=False, ddof=1), r


def test_demo_structure_awareness():
    assert demo() == 0


def test_simplex_projection_properties():
    w = _project_simplex(np.array([0.9, -0.3, 0.5]))
    assert w.min() >= 0 and w.sum() == pytest.approx(1.0)


def test_all_engines_long_only_sum_one():
    cov, _ = _cov()
    for fn in (w_minvar, w_erc, w_hrp):
        w = fn(cov)
        assert w.min() >= -1e-9
        assert w.sum() == pytest.approx(1.0, abs=1e-6)


def test_minvar_not_worse_than_equal_in_sample():
    cov, _ = _cov(seed=7)
    n = cov.shape[0]
    ew = np.full(n, 1 / n)
    wm = w_minvar(cov)
    assert wm @ cov @ wm <= ew @ cov @ ew + 1e-10


def test_erc_equalizes_risk_contributions():
    cov, _ = _cov(seed=3)
    w = w_erc(cov)
    rc = w * (cov @ w)
    rc = rc / rc.sum()
    assert rc.max() - rc.min() < 0.02


def test_hrp_allocates_across_clusters():
    # 4 只强相关 + 1 只独立:HRP 给独立资产的权重应远高于 1/5 的平均摊派
    rng = np.random.default_rng(9)
    n = 500
    common = rng.normal(0, 0.012, n)
    rets = np.column_stack([common + rng.normal(0, 0.003, n) for _ in range(4)]
                           + [rng.normal(0, 0.012, n)])
    cov = np.cov(rets, rowvar=False, ddof=1)
    w = w_hrp(cov)
    assert w[4] > 0.3


def test_shrinkage_intensity_grows_when_panel_short():
    rng = np.random.default_rng(2)
    _, i_long = shrunk_cov(rng.normal(0, 0.01, (1000, 5)))
    _, i_short = shrunk_cov(rng.normal(0, 0.01, (40, 20)))
    assert i_short > i_long


def test_weight_cap_enforced():
    cov, _ = _cov(seed=5)
    w = apply_cap(w_minvar(cov), 0.30)
    assert w.max() <= 0.30 + 1e-9 and w.sum() == pytest.approx(1.0)


def test_short_wide_panel_gets_estimation_note():
    rng = np.random.default_rng(4)
    idx = pd.bdate_range("2024-01-02", periods=50)
    rets = pd.DataFrame(rng.normal(0, 0.01, (50, 30)),
                        index=idx, columns=[f"S{i}" for i in range(30)])
    rep = optimize(rets, method="hrp")
    assert any("wide error bars" in n for n in rep["notes"])


def test_compare_mode_reports_oos_table():
    rng = np.random.default_rng(6)
    idx = pd.bdate_range("2022-01-03", periods=600)
    rets = pd.DataFrame(rng.normal(0.0003, 0.01, (600, 4)),
                        index=idx, columns=list("ABCD"))
    rep = optimize(rets, method="compare")
    wf = rep["walk_forward"]
    assert not wf["skipped"]
    assert set(wf["oos_table"]) == {"equal", "invvol", "minvar", "erc", "hrp"}


def test_disclosure_present_on_weights():
    cov_df = pd.DataFrame(
        np.random.default_rng(8).normal(0, 0.01, (200, 3)),
        index=pd.bdate_range("2024-01-02", periods=200), columns=list("XYZ"))
    rep = optimize(cov_df, method="erc")
    assert any("not individualized investment advice" in d for d in rep["disclosure"])
