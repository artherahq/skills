---
name: backtest-validation
description: >-
  Validate whether a backtest result is trustworthy before drawing any
  conclusion from it. Trigger for "回测这个策略", "这个策略过拟合吗",
  "夏普这么高可信吗", "加上手续费还赚钱吗", "样本外表现", "validate this
  backtest", "is this strategy overfit", or whenever the user (1) presents or
  produces backtest results and wants a judgement, (2) asks whether an edge is
  real, (3) compares strategy variants and picks the best one, or (4) is about
  to deploy/paper-trade a strategy based on historical performance. Fire even
  when the user only asks for the metrics ("just show me the Sharpe") — the
  metrics are not a conclusion until the gauntlet passes. Pair with
  point-in-time-research: that skill guards the data going in; this one guards
  the claim coming out. Do NOT trigger for pure data fetching or for live
  trading questions with no historical simulation involved.
---

# Backtest Validation

A backtest is a claim, not a result. In-sample performance is the *cheapest*
number in quant research: it rises with every parameter you tune and every
variant you discard. This skill converts "the backtest looks great" into a
defensible verdict — or an honest rejection.

## The four ways a backtest lies

1. **Selection bias.** You tried N variants and reported the best. The maximum
   of N noise strategies has a positive expected Sharpe that grows with N.
   Ask the user how many variants were tried; disclose that number to the
   Deflated Sharpe Ratio. Undisclosed trials are the most common lie by omission.
2. **Cost blindness.** Gross returns ignore what turnover costs. An edge that
   dies at 10 bps per unit of turnover was never an edge — it was a liquidity
   donation you had not made yet.
3. **In-sample memorization.** Parameters fitted on the full history describe
   the past, not the future. A chronological in-sample / out-of-sample split is
   the minimum; walk-forward is better when the series is long enough.
4. **Fragility.** One draw of history is one draw. If a stationary block
   bootstrap says p(Sharpe ≤ 0) is 10%, the "edge" is statistically
   indistinguishable from luck regardless of how the equity curve looks.

Look-ahead and revision leakage are the *fifth* way — that is
`point-in-time-research`'s jurisdiction. When the input data has not passed PIT
discipline, run that skill first; a gauntlet on contaminated data validates
nothing.

## Workflow

1. Establish what is being validated: returns series (frequency, gross or net),
   portfolio weights if available, benchmark, and — critically — **how many
   variants were tried** before this one. Record the answers.
2. If the returns come from a simulation the user or you just built, confirm
   the data joins are point-in-time clean (hand off to `point-in-time-research`
   if in doubt). Do not proceed on contaminated inputs.
3. Run the gauntlet:
   `python scripts/validation_gauntlet.py --returns returns.csv [--weights weights.csv] --freq daily --trials N --json report.json`
   With no data at hand, show the mechanics with `--demo`.
4. Read the verdict, not the equity curve. Report the honest metric set, the
   cost ladder, the IS/OOS split, the bootstrap CI, and the DSR together —
   never the Sharpe alone.
5. Translate flags into plain language for the user: what failed, why it
   matters, what would fix it (longer history, cost model, fewer variants,
   walk-forward). See `references/methodology.md` for the interpretation table.
6. Completion gate: claim the strategy "validated" **only** when the gauntlet
   exits 0 (PASS or WARN). On FAIL, the deliverable is the rejection and its
   reasons — that is a valid, useful research result. Label WARN verdicts as
   "conditionally validated" and enumerate the warnings.
7. Never extrapolate a validated backtest into a forward guarantee. The
   strongest permitted claim is: "survived the validation gauntlet on the
   disclosed information set".

## Guardrails

- No conclusion from gross returns when turnover is knowable — run the ladder.
- No "best of N" reporting without disclosing N to the DSR.
- No deployment/paper-trading recommendation on a FAIL verdict.
- Missing inputs degrade honestly: the gauntlet emits `no_cost_check` /
  `no_split_check` warnings instead of silently skipping — surface them.
- Guaranteed-return language is prohibited regardless of verdict.
