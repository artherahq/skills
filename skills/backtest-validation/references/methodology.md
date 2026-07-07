# Validation gauntlet — methodology & interpretation

## Honest metric set

Computed one way, no alternatives to cherry-pick: total return, CAGR,
annualized volatility, Sharpe, Sortino, max drawdown, Calmar, win rate, profit
factor, average one-way turnover (when weights are supplied). Annualization
uses 252/52/12 periods for daily/weekly/monthly.

## Check 1 — cost ladder

Net returns = gross − turnover × cost, at 0/5/10/25/50 bps per unit of one-way
turnover (`0.5 · Σ|w_t − w_{t−1}|`). Interpretation:

| Observation | Reading |
|---|---|
| Sharpe stable across the ladder | edge is capacity-real at retail scale |
| dies between 10–25 bps | viable only with cheap execution; flag it |
| dies at ≤10 bps (`cost_fragile`, FAIL) | microstructure noise, not an edge |

50 bps approximates A-share stamp duty + slippage for small caps; 5–10 bps is
liquid US large-cap reality.

## Check 2 — split stability

Chronological split (default 70/30) — never shuffled, since autocorrelation is
the point. `oos_negative` (FAIL): in-sample Sharpe > 0.5 but out-of-sample ≤ 0.
`oos_decay` (WARN): decay > 50%. A strategy with in-sample Sharpe below 0.5 is
not asked to prove stability — there is nothing worth stabilizing.

For long series (> 5y daily), prefer full walk-forward (rolling re-fit) over a
single split; the single split is the *minimum* bar, not the gold standard.

## Check 3 — stationary block bootstrap

Politis–Romano stationary bootstrap (mean block 20 periods, 2000 draws)
preserves short-range autocorrelation while resampling. Outputs a 95% CI for
the annualized Sharpe and `p(Sharpe ≤ 0)`:

- p > 10% → `not_robust` (FAIL): indistinguishable from zero.
- 5–10% → `weak_robustness` (WARN).

## Check 4 — Deflated Sharpe Ratio (selection bias)

Bailey & López de Prado (2014). Given N disclosed trials, the expected maximum
Sharpe of N pure-noise strategies is

`SR₀ = √(1/T) · [(1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e))]`, γ = Euler–Mascheroni.

DSR = probability the observed Sharpe exceeds SR₀, adjusting for skew/kurtosis
of the return distribution. DSR < 0.95 with N > 1 → `selection_bias`
(WARN ≥ 0.5, FAIL < 0.5).

The number of trials is an **honesty input**: it cannot be computed from the
returns. Ask. Common answers that all count as trials: parameter grid points,
discarded variants, different universes tried, different date ranges tried.

## Verdict semantics

- **PASS** — no flags. The claim "survived the gauntlet on the disclosed
  information set" is permitted.
- **WARN** — survivable defects (short history, skipped cost check, moderate
  decay). Report as *conditionally validated*, enumerate warnings.
- **FAIL** — at least one fatal flag. The deliverable is the rejection: which
  check failed, why it matters, what would change the outcome.

Exit code enforces the gate: 0 for PASS/WARN, 1 for FAIL. Wire it into CI or
agent completion gates so "validated" cannot be claimed rhetorically.

## What this gauntlet does NOT cover

- Look-ahead / revision leakage in the inputs → `point-in-time-research`.
- Regime dependence beyond the single split (bull-only samples pass splits
  inside one regime) — check the sample spans at least one drawdown episode.
- Capacity/impact beyond linear per-turnover costs.
- Live execution slippage asymmetry.
