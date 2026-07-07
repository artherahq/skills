---
name: portfolio-optimization
description: >-
  Produce defensible portfolio weights from return history, and check whether
  the optimizer earns its complexity. Trigger for "帮我优化组合权重",
  "风险平价配置", "怎么配这几只资产", "降低组合波动怎么调仓", "optimize my
  portfolio", "risk parity allocation", "rebalance weights", or whenever the
  user (1) holds several assets and asks how much of each, (2) wants lower
  volatility/drawdown via allocation, (3) asks equal weight vs something
  smarter, or (4) receives strategy signals that need converting into weights.
  Do NOT trigger for single-asset position sizing (execution question) or for
  judging portfolio risk after the fact (risk-assessment).
---

# Portfolio Optimization

Optimizers amplify the noise in their inputs, and the noisiest input in
finance is the expected return. This skill therefore optimizes **risk
structure only** — and always asks the question most optimizers dodge: did the
clever method beat equal weight out-of-sample?

## Principles

1. **No expected-return inputs.** Sample means are noise; MVO on sample means
   is noise squared. The methods here (inverse vol, min variance, ERC risk
   parity, HRP) need only the covariance structure. If the user brings views,
   the honest framing is scenario analysis, not a mean-variance frontier.
2. **Equal weight is the benchmark, not the strawman.** The `compare` mode
   walk-forwards every method against EW; `optimizer_no_edge` is a first-class
   finding, common in practice, and worth telling the user plainly.
3. **Estimation error is disclosed, not hidden.** Covariance is shrunk toward
   an identity target when the panel is short relative to breadth, and the
   report states the intensity. T < 2N earns a wide-error-bars note.
4. **Weights describe risk, not conviction.** The disclosure lines say so and
   must be surfaced.

## Workflow

1. Assemble the return matrix (shared dates, per-asset periodic returns) and
   any constraints (max weight per asset). Confirm the frequency.
2. Start with the comparison, not a single method:
   `python scripts/optimize_portfolio.py --returns returns.csv --method compare`
   — walk-forward OOS vol/Sharpe/maxDD per method vs equal weight.
3. Pick the method the comparison actually supports. Defaults when the
   comparison is inconclusive: `hrp` for structured books (clusters visible),
   `erc` when the user wants balanced risk, `equal` when nothing beats it.
4. Produce weights: `--method hrp --max-weight 0.25 --json weights.json`.
   Report weights, portfolio vol, effective N, and per-asset risk
   contributions together — a weight table without risk contributions hides
   exactly what the user needs to see.
5. Hand the resulting book to `risk-assessment` for the full profile
   (concentration, tails, stress) before anyone acts on it.
6. Rebalancing advice must state turnover implications — weights that change
   10% a month feed the cost ladder in backtest-validation.

## Guardrails

- No mean-variance frontiers from sample means; no implied return forecasts.
- `optimizer_no_edge` findings are reported, not suppressed.
- Shrinkage intensity and estimation-error notes are part of the deliverable.
- Weights are research output, not individualized investment advice — the
  disclosure lines ship with every result.
- Live execution is out of scope; the strongest recommendation is a paper
  rebalance reviewed by the user.
