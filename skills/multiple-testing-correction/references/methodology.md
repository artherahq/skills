# Multiplicity gate — methodology & interpretation

## Check 1 — multiple-testing correction

Each test's t-statistic converts to a two-sided p-value via the t-distribution
(`df = n_periods - 1`; falls back to a normal approximation if scipy is
unavailable, which converges to the same answer once `n_periods` is not tiny).

**Bonferroni** — reject at `p <= alpha / n`. Controls the family-wise error
rate: `P(at least one false positive across the whole batch) <= alpha`. The
conservative choice — use it when a single false positive is expensive (e.g.
before capital deployment).

**Benjamini-Hochberg (BH/FDR)** — sort p-values ascending, find the largest
`k` where `p_(k) <= (k/n) * alpha`, reject the null for the `k` smallest.
Controls the *expected proportion* of false positives among what gets called
significant, not the probability of any false positive at all. Less
conservative than Bonferroni and the more common choice in modern quant
research — the same "batch size shouldn't buy false confidence" logic behind
Bailey & López de Prado's Deflated Sharpe Ratio, which `backtest-validation`
already uses for the narrower case of "best strategy variant out of N
backtested." This skill is the general form: any batch of hypothesis tests
(factor screens, parameter sweeps, sub-period splits), not just
strategy-selection.

| Naive count > 0, BH count == 0 | `significance_evaporates` (FAIL) — the batch's apparent significance is consistent with pure noise at this size |
| Naive count > BH count > 0 | `correction_reduced_significant_set` (WARN) — report only the BH survivors |
| Naive count == BH count | no flag — correction didn't change the conclusion (small batch, or genuinely strong effects) |

A batch of exactly 1 test cannot be corrected against itself
(`insufficient_batch`, WARN) — that is not a bug in the gate, it is the
correct behavior for `n=1`.

## Check 2 — breadth illusion (Fundamental Law of Active Management)

Grinold (1989): `IR ≈ IC × √Breadth`, where Breadth is the number of
*independent* bets made per year. The formula's entire content is in the
word "independent" — it is trivial to inflate Breadth by counting correlated
bets as separate ones.

Effective breadth from `N` nominal bets sharing average pairwise correlation
`rho`:

```
N_eff = N / (1 + (N - 1) * rho)
```

`rho = 0` → `N_eff = N` (truly independent, no correction needed).
`rho = 1` → `N_eff = 1` (they are the same bet wearing `N` costumes,
regardless of how the nominal count is reported). This is the identical
diversification-ratio shape `risk-assessment`'s effective-N concentration
metric uses — that skill applies it to **portfolio weight** (how much capital
is really concentrated); this one applies it to **bet count** (how much
research "breadth" is really independent). Same formula, different unit,
worth cross-checking both when a strategy claims diversification *and* a high
IR from the same set of correlated sub-strategies.

`breadth_illusion` (WARN) fires when effective breadth drops below 50% of
nominal — report the *effective*-breadth IR ceiling, not the nominal one, in
any forward-looking claim from that point on.

## Where the correlation number comes from

The gate does not estimate `rho` itself — it is a required input, same as
`backtest-validation`'s disclosed trial count. A defensible source: the
realized pairwise correlation of the *signals themselves* (not their
underlying assets) over the same history used to compute IC. An assumed or
guessed `rho` should be labeled as an assumption in the writeup, not presented
as measured.

## Verdict semantics

- **PASS** — no flags. Either the batch is small enough that correction
  didn't move the conclusion, or breadth checks out.
- **WARN** — correction shrank the significant set (report the survivors), a
  single-test batch (nothing to correct), or a breadth illusion detected
  (report the corrected IR).
- **FAIL** — the batch's apparent significance is indistinguishable from pure
  noise once corrected. The deliverable is the rejection, not a retry with a
  looser threshold.

Exit code enforces the gate: 0 for PASS/WARN, 1 for FAIL.

## What this gate does NOT cover

- Look-ahead / revision leakage in the data feeding the t-statistics →
  `point-in-time-research` (garbage in, corrected-garbage out).
- Selection bias in a single best-of-N *strategy* comparison (as opposed to a
  batch of *hypothesis tests*) → `backtest-validation`'s Deflated Sharpe
  Ratio is the right tool for that narrower case.
- Portfolio-level concentration/diversification of capital →
  `risk-assessment`'s effective-N and pairwise-correlation checks.
- Estimating the correlation or trial count inputs themselves — both must
  come from the user or the actual data, not be assumed by this skill.
