# GEX gate — methodology & interpretation

## Gamma, per strike

Black-Scholes gamma is identical for a call and a put at the same
`(S, K, T, sigma)`, so there's exactly one formula:

```
d1 = (ln(S/K) + (r + 0.5*sigma^2)*T) / (sigma*sqrt(T))
Gamma(K) = phi(d1) / (S * sigma * sqrt(T))
```

where `phi` is the standard normal PDF. Gamma peaks at-the-money and falls
off in both directions — that shape is the reason near-the-money strikes
dominate GEX totals even when they don't have the largest open interest.

`T` is calendar days to expiry divided by 365, floored at 1 day so a
same-day expiration doesn't divide by zero or blow up numerically. `r`
defaults to 0.05 (a placeholder risk-free rate) — pass the real one if
precision at very long-dated expirations matters; gamma is not very
sensitive to `r` in practice.

## Normalization: why `× S² × 0.01`

Raw Black-Scholes gamma is "delta change per $1 move in the underlying, per
option." Multiplying by open interest and the contract multiplier (100
shares/contract, standard for US equity options) gives total delta
exposure change per $1 move — useful, but not the number every public GEX
calculator reports.

The `× S² × 0.01` convention converts that into "notional dollar exposure
per 1% move in the underlying" — SqueezeMetrics and the calculators that
followed report GEX in this unit because it's comparable across tickers at
wildly different price levels (a $50 stock and a $2,000 stock aren't
comparable in raw dollars-per-$1-move terms). This is not a law of
physics — it's a reporting convention. Keep it if reproducing/comparing
against a standard GEX chart; state it explicitly if using something else.

## Sign convention — the part that's an assumption, not a formula

```
call_gex(K) = +Gamma(K) * call_OI(K) * multiplier * S^2 * 0.01
put_gex(K)  = -Gamma(K) * put_OI(K)  * multiplier * S^2 * 0.01
net_gex(K)  = call_gex(K) + put_gex(K)
```

The `+`/`-` split rests entirely on: *customers are net buyers of options,
dealers are the counterparty (net sellers), and dealers delta-hedge their
book.* Under that assumption:

- Rising price + positive dealer gamma → dealers buy the underlying to
  stay delta-neutral → hedging flow dampens the move (positive regime,
  vol-suppressing).
- Rising price + negative dealer gamma → dealers sell to stay
  delta-neutral → hedging flow amplifies the move (negative regime,
  vol-amplifying).

No public dataset confirms dealers are actually net short customer flow at
any given moment — it's the standard assumption because it's usually
approximately true for retail-heavy names, not because it's measured. A
market-maker who is already long gamma from a prior trade, or a name with
unusually two-sided institutional flow, can violate it. State the
assumption; don't state the conclusion as fact.

**The one-line version of the entire failure mode this skill exists to
catch:** flip the `put_gex` sign to `+` instead of `-` (a plausible typo —
"OI is OI, why would sign matter" is an easy trap) and the code still
executes, still returns a number, still charts cleanly. It just describes
the opposite hedging regime. `scripts/gex_gate.py --demo` reproduces this:
identical chain, `net_gex_total` goes from -1.08M (correct) to +2.63M
(buggy), regime flips negative → positive.

## Zero-gamma flip

Sort strikes ascending, cumulatively sum `net_gex(K)`, and find where the
running sum crosses zero. Linearly interpolate between the two bracketing
strikes rather than snapping to the nearer one — on a chain with $5 or $10
strike spacing, "nearest strike" can be off by half a strike-width, which
matters when the flip point itself is the thing being reported as a level.
No crossing in the chain's range → `zero_gamma_flip = None`; don't
extrapolate outside the data you have.

## Gamma walls

The top-N strikes by `abs(net_gex(K))` — the strikes where dealer hedging
flow is largest in either direction, often read informally as
support/resistance-like levels because large hedging flow at a strike can
slow a move through it. `audit_gex_report` verifies the reported walls are
actually the top-N by magnitude in the accompanying strike table, not an
arbitrary or stale selection.

## The audit gate's checks

| Check | Severity | What it catches |
|---|---|---|
| `missing_dealer_assumption_disclosure` | FAIL | Report doesn't state the customers-net-buyers assumption anywhere |
| `missing_coverage_limitation` | FAIL | Report doesn't state what this snapshot doesn't cover |
| `gex_sum_mismatch` | FAIL | Reported total doesn't match the sum of the per-strike detail — stale or hand-edited summary |
| `regime_sign_mismatch` | FAIL | Reported regime label doesn't match the sign of the reported total — the exact shape of the sign-convention bug |
| `flip_point_out_of_range` | FAIL | Reported zero-gamma flip falls outside the chain's own strike range |
| `gamma_walls_mismatch` | FAIL | Reported walls aren't actually the top-N strikes by magnitude |
| `sparse_chain` | WARN | Fewer than 5 strikes with OI — flip/wall picks have limited resolution, disclose it |
| `no_strike_detail` | WARN | Only a summary was supplied, nothing to audit the summary against |

`audit_gex_report` cannot catch a fabricated *input* (invented OI/IV
numbers feeding a self-consistent computation) — it audits internal
consistency and disclosure, not ground truth. Pull OI/IV from a real chain.

## Verdict semantics

- **PASS** — no flags. Disclosures present, numbers internally consistent.
- **WARN** — usable, but disclose the caveat (sparse chain, or a
  summary-only report that couldn't be cross-checked).
- **FAIL** — missing required disclosure, or the numbers disagree with
  each other. Fix before sharing; a FAIL is not something to caveat around
  in prose while keeping the broken number.

Exit code enforces the gate: 0 for PASS/WARN, 1 for FAIL.

## What this skill does NOT cover

- Risk of options positions the user actually holds → `risk-assessment`.
- Whether a GEX-based trading rule is profitable → `backtest-validation`
  (GEX is a hedging-flow *description*, not a validated signal on its
  own).
- Position sizing or execution off a GEX read → `execution-position`.
- Multiple-expiration or portfolio-level dealer gamma — this gate operates
  on one expiration's chain at a time, by design (see
  `coverage_limitation`); summing across expirations changes the "what
  does this cover" disclosure and isn't done automatically.
