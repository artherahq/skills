# Factor evaluation — thresholds & interpretation

## IC thresholds (daily cross-sections)

| Reading | Interpretation |
|---|---|
| \|mean IC\| < 0.02 | `no_signal` (fail) — indistinguishable from ranking noise |
| 0.02–0.03 | `weak_signal` (warn) — thin; costs decide |
| 0.03–0.08 | workable — most production equity factors live here |
| > 0.10 sustained | suspicious — check PIT contamination before celebrating |
| IC-IR < 0.30 | `inconsistent_ic` (warn) — mean hides wild swings |

Monthly cross-sections run higher (|IC| 0.05–0.15 workable); scale thresholds
with frequency judgement, and say so when you do.

## Judgement machine

- `invalid` — no_signal fired. Discard or redesign.
- `weak` — signal exists but a fatal instability fired (e.g. `sign_flip`).
- `valid_but_moderate` — signal real, with warnings (thin edge, churny ranks,
  extremes-only quantiles). Usable **with** the warnings attached.
- `valid` — clean pass. Still only a hypothesis until backtest-validation.

Exit code: 0 for valid/valid_but_moderate, 1 otherwise — wire into gates.

## Why rank IC

Pearson IC on raw factor values rewards outliers: one 10-sigma factor value
paired with one lucky return manufactures correlation. Spearman on ranks is
what the portfolio construction actually consumes (you buy the top quintile,
not the z-score).

## Decay × turnover interaction

Decay tells you how long the information lives; rank autocorrelation tells you
how often you must trade to hold the factor. The killer combination is
horizon-1-only IC with autocorrelation < 0.5 (`high_turnover`): the rebalance
frequency needed to capture the edge feeds the cost ladder. Final word belongs
to backtest-validation's cost check — this skill only raises the flag.

## Sub-period sign flip

Half-sample IC signs disagreeing (both above noise) usually means regime
dependence or a data artifact in one half. Either way the factor cannot be
deployed unconditionally — `weak` at best until the flip is explained.

## What this evaluation does NOT cover

- Look-ahead in the panel itself → point-in-time-research.
- Net-of-cost viability, capacity → backtest-validation.
- Factor crowding / correlation with known factor zoo — needs external factor
  returns; note it as a limitation when relevant.
- Non-linear factor-return shapes (quantile table hints at them; modeling them
  is engine work).
