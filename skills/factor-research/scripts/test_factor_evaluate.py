"""factor_evaluate 测试:demo 分离力 + IC/分位/稳定性检查的方向性。"""

import numpy as np
import pandas as pd

from factor_evaluate import demo, evaluate, rank_autocorr, spearman


def _universe(n_dates=200, n_sym=30, seed=3):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=n_dates)
    symbols = [f"S{i:02d}" for i in range(n_sym)]
    return rng, idx, symbols


def _to_long(mat, idx, symbols):
    df = pd.DataFrame(mat, index=idx, columns=symbols)
    return df.stack().rename("value").rename_axis(["date", "symbol"]).reset_index()


def test_demo_separates_prediction_from_noise():
    assert demo() == 0


def test_spearman_perfect_and_inverse():
    a = np.arange(10, dtype=float)
    assert spearman(a, a) == 1.0
    assert spearman(a, -a) == -1.0


def test_persistent_predictive_factor_is_valid_with_high_ic():
    # 静态横截面分数(rank 自相关=1,无换手 flag)+ 收益持续由它驱动 → 干净的 valid
    rng, idx, symbols = _universe()
    scores = rng.normal(0, 1, len(symbols))
    signal = np.tile(scores, (len(idx), 1))
    rets = pd.DataFrame(
        0.01 * signal + rng.normal(0, 0.002, (len(idx), len(symbols))),
        index=idx, columns=symbols)
    rep = evaluate(_to_long(signal, idx, symbols), rets)
    assert rep["judgement"] == "valid"
    assert rep["ic"]["mean"] > 0.5
    assert rep["quantiles"]["monotone_share"] == 1.0
    assert rep["next_step"] == "backtest-validation"


def test_churny_predictive_factor_downgraded_by_turnover():
    # 每期独立重排的强预测因子:信号真,但换手极高 → 必须带 high_turnover 降档,
    # 由 backtest-validation 的成本阶梯做最终裁决(两个 skill 的接力关系)。
    rng, idx, symbols = _universe(seed=17)
    signal = rng.normal(0, 1, (len(idx), len(symbols)))
    rets = pd.DataFrame(
        0.01 * np.vstack([np.zeros((1, len(symbols))), signal[:-1]])
        + rng.normal(0, 0.002, (len(idx), len(symbols))),
        index=idx, columns=symbols)
    rep = evaluate(_to_long(signal, idx, symbols), rets)
    assert rep["judgement"] == "valid_but_moderate"
    assert "high_turnover" in {f["code"] for f in rep["flags"]}


def test_noise_factor_invalid():
    rng, idx, symbols = _universe(seed=9)
    rets = pd.DataFrame(rng.normal(0, 0.02, (len(idx), len(symbols))), index=idx, columns=symbols)
    noise = rng.normal(0, 1, (len(idx), len(symbols)))
    rep = evaluate(_to_long(noise, idx, symbols), rets)
    assert rep["judgement"] == "invalid"
    assert "no_signal" in {f["code"] for f in rep["flags"]}
    assert rep["next_step"] == "discard_or_redesign"


def test_sign_flip_flagged():
    rng, idx, symbols = _universe(n_dates=240, seed=11)
    n = len(idx)
    signal = rng.normal(0, 1, (n, len(symbols)))
    lagged = np.vstack([np.zeros((1, len(symbols))), signal[:-1]])
    flip = np.where(np.arange(n)[:, None] < n // 2, 1.0, -1.0)  # 后半反号
    rets = pd.DataFrame(0.01 * lagged * flip + rng.normal(0, 0.002, (n, len(symbols))),
                        index=idx, columns=symbols)
    rep = evaluate(_to_long(signal, idx, symbols), rets)
    assert "sign_flip" in {f["code"] for f in rep["flags"]}
    assert rep["judgement"] in ("weak", "invalid")


def test_static_factor_rank_autocorr_is_one():
    import pytest
    _, idx, symbols = _universe(n_dates=50)
    static = np.tile(np.arange(len(symbols), dtype=float), (len(idx), 1))
    fwide = pd.DataFrame(static, index=idx, columns=symbols)
    assert rank_autocorr(fwide) == pytest.approx(1.0)


def test_insufficient_panel_rejected():
    _, idx, symbols = _universe(n_dates=10)
    rng = np.random.default_rng(0)
    rets = pd.DataFrame(rng.normal(0, 0.01, (len(idx), len(symbols))), index=idx, columns=symbols)
    rep = evaluate(_to_long(rng.normal(0, 1, (len(idx), len(symbols))), idx, symbols), rets)
    assert rep["judgement"] == "invalid"
    assert "insufficient_panel" in {f["code"] for f in rep["flags"]}
