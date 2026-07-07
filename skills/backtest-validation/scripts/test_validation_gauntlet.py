"""validation_gauntlet 测试:demo 分离力 + 各检查的方向性 + 门禁退出码。"""

import math

import numpy as np
import pandas as pd
import pytest

from validation_gauntlet import (
    COST_LADDER_BPS, demo, deflated_sharpe, run_gauntlet, turnover_series,
)


def _genuine(n=1500, seed=42):
    rng = np.random.default_rng(seed)
    return pd.Series(0.0006 + rng.normal(0, 0.008, n))


def test_demo_separates_signal_from_selection_bias():
    assert demo() == 0


def test_genuine_edge_passes_or_warns():
    rep = run_gauntlet(_genuine(), freq="daily", trials=1)
    assert rep["verdict"] in ("PASS", "WARN")
    assert rep["metrics"]["sharpe"] > 0


def test_pure_noise_with_disclosed_trials_fails_dsr():
    rng = np.random.default_rng(0)
    candidates = rng.normal(0.0, 0.01, (200, 1200))
    lucky = candidates[np.argmax(candidates.mean(axis=1))]
    rep = run_gauntlet(pd.Series(lucky), freq="daily", trials=200)
    codes = {f["code"] for f in rep["flags"]}
    assert "selection_bias" in codes or "not_robust" in codes


def test_dsr_monotone_in_trials():
    r = _genuine().to_numpy()
    d1 = deflated_sharpe(r, 252, trials=1)["dsr"]
    d100 = deflated_sharpe(r, 252, trials=100)["dsr"]
    assert d100 <= d1


def test_cost_ladder_monotone_and_flags_fragile_edge():
    n = 800
    rng = np.random.default_rng(3)
    r = pd.Series(0.0002 + rng.normal(0, 0.004, n))          # 细小的毛边收益
    # 每期全换仓的两资产组合:turnover = 1 → 25bps 成本足以杀死毛边
    w = pd.DataFrame({"A": [1.0, 0.0] * (n // 2), "B": [0.0, 1.0] * (n // 2)})
    rep = run_gauntlet(r, weights=w, freq="daily")
    sharpes = [c["sharpe"] for c in rep["cost_ladder"]]
    assert len(sharpes) == len(COST_LADDER_BPS)
    assert all(a >= b or math.isnan(b) for a, b in zip(sharpes, sharpes[1:]))
    assert {f["code"] for f in rep["flags"]} & {"cost_fragile"}


def test_turnover_full_swap_is_one():
    w = pd.DataFrame({"A": [1.0, 0.0, 1.0], "B": [0.0, 1.0, 0.0]})
    tno = turnover_series(w)
    assert tno[0] == pytest.approx(0.5)   # 建仓:0.5 * |Δ| = 0.5
    assert tno[1] == pytest.approx(1.0)   # 全换仓
    assert tno[2] == pytest.approx(1.0)


def test_oos_collapse_flagged():
    rng = np.random.default_rng(9)
    good = 0.002 + rng.normal(0, 0.006, 700)     # 前段强
    dead = rng.normal(-0.0005, 0.006, 300)       # 样本外归零
    rep = run_gauntlet(pd.Series(np.concatenate([good, dead])), freq="daily")
    codes = {f["code"] for f in rep["flags"]}
    assert codes & {"oos_negative", "oos_decay"}


def test_no_weights_degrades_honestly():
    rep = run_gauntlet(_genuine(300), freq="daily")
    assert "no_cost_check" in {f["code"] for f in rep["flags"]}
    assert rep["cost_ladder"] == []


def test_short_history_warns():
    rep = run_gauntlet(_genuine(100), freq="daily")
    assert "short_history" in {f["code"] for f in rep["flags"]}
