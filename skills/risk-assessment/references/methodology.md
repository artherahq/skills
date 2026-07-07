# Risk profile — thresholds & interpretation

## Flag thresholds (and why)

| Flag | Trigger | Rationale |
|---|---|---|
| `single_name_concentration` (high) | top position > 50% of gross | one earnings call decides the book |
| `concentration` (medium) | top position > 30% | institutional single-name limits cluster at 20–30% |
| `low_effective_n` (medium) | effective N < 3 with ≥3 positions | HHI says the diversification is cosmetic |
| `diversification_illusion` (high) | avg pairwise corr > 0.7 | the book moves as one asset in stress |
| `high_volatility` (high) | annualized vol > 35% | single-crypto/levered-equity territory |
| `elevated_volatility` (medium) | vol > 20% | above broad-equity norms |
| `deep_drawdown` (high) | sample maxDD < −30% | realized, not hypothetical |
| `fat_tails` (medium) | excess kurtosis > 3 or skew < −1 | normal-VaR understates the tail |

Risk level: ≥2 high flags → `high`; 1 high → `medium_high`; ≥2 medium →
`medium`; 1 medium → `low_medium`; none → `low`. The level describes the
sample window.

## Metric notes

- **VaR/CVaR** are historical quantiles/tail means of the supplied window —
  they cannot see crises the window lacks. CVaR ≤ VaR by construction.
- **Cornish–Fisher VaR** adjusts the parametric quantile for skew/kurtosis.
  Textbook behavior: with heavy tails it can *narrow* at 95% (extra mass near
  the center too) while *widening* sharply at 99%. When CF-99 diverges from
  historical VaR-99, trust the more conservative one.
- **Effective N** = 1/HHI of absolute weights. 10 equal positions → 10;
  60/25/15 → 2.25.
- **Diversification ratio** = weighted-average asset vol / portfolio vol.
  Near 1 means correlations ate the diversification.
- **Beta shock** = β × market move. Linear floor; crash correlations exceed it.
  Omitted (with reason) when no benchmark or < 60 overlapping observations.

## What this profile does NOT cover

- Liquidity risk (position size vs ADV) — needs volume data.
- Factor/regime decomposition (HMM, DCC-GARCH) — engine-level analyses; hand
  off to the quant engine when the user needs them.
- Forward-looking scenario construction — deliberately out of scope; only the
  labeled linear beta approximation is permitted.
- Options/convexity — linear instruments assumed.
