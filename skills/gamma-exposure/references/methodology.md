# GEX gate — methodology & interpretation

## Primary source

This gate's methodology is checked directly against SqueezeMetrics' original
whitepaper, *Gamma Exposure (GEX): Quantifying hedge rebalancing in SPX
options* (March 2016, revised December 2017, freely redistributable,
sqzme.co) — not against secondary summaries. Where this gate's scope narrows
or extends what that paper describes, it says so explicitly below rather than
presenting an extension as if it were the original methodology.

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

SqueezeMetrics' original formula is simpler than most public calculators
reproduce: `GEX = Γ · OI · 100` per contract, in **shares** — no `S²` term at
all. Their own footnote: *"When computing for SPX, we denominate GEX in
dollars"* — i.e. their dollar conversion is a share-count times spot price,
not the `S² × 0.01` convention this skill (and most public retail GEX
calculators) uses.

`× S² × 0.01` is a later popularization: it converts raw gamma into "notional
dollar exposure per 1% move in the underlying," which is comparable across
tickers at wildly different price levels (a $50 stock and a $2,000 stock
aren't comparable in raw dollars-per-$1-move terms). Useful, standard among
public GEX charting tools — but attribute it as the charting-tool convention,
not SqueezeMetrics' original per-contract share formula. Not a law of
physics either way — a reporting convention, state which one you're using.

## Sign convention — the part that's an assumption, not a formula

```
call_gex(K) = +Gamma(K) * call_OI(K) * multiplier * S^2 * 0.01
put_gex(K)  = -Gamma(K) * put_OI(K)  * multiplier * S^2 * 0.01
net_gex(K)  = call_gex(K) + put_gex(K)
```

The `+`/`-` split is NOT a blanket "customers buy, dealers sell" rule — the
original whitepaper gives call and put a *different* behavioral story (its
"Four Assumptions" section), because it's easier to defend than one uniform
claim:

- **Calls**: investors are assumed net *sellers* (covered-call writing,
  collar overwriting against existing stock) — dealers are the net *buyers*,
  so dealers are net **long** call gamma (`+`).
- **Puts**: investors are assumed net *buyers* (protective puts against
  existing exposure) — dealers are the net *sellers*, so dealers are net
  **short** put gamma (`-`).
- A fourth, easy-to-miss assumption in the same section: dealers hedge
  *precisely* to the option's delta. Real market-makers use hedging bands to
  balance transaction cost against delta risk, so this is an additional
  simplification layered on top of the positioning assumption — not
  something unique to this implementation.

Under these assumptions:

- Rising price + positive dealer gamma → dealers buy the underlying to
  stay delta-neutral → hedging flow dampens the move (positive regime,
  vol-suppressing).
- Rising price + negative dealer gamma → dealers sell to stay
  delta-neutral → hedging flow amplifies the move (negative regime,
  vol-amplifying).

No public dataset confirms dealers are actually positioned this way at any
given moment — it's the standard assumption because it's usually
approximately true for retail-heavy names with visible call-overwriting and
protective-put flow, not because it's measured. A market-maker who is
already long gamma from a prior trade, or a name with unusually two-sided
institutional flow, can violate it either leg. State the assumption; don't
state the conclusion as fact.

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

This per-strike flip level is a popularized extension from public GEX
charting services, not part of the original whitepaper — SqueezeMetrics'
own methodology computes a single aggregate GEX number for the whole
underlying (summed across every strike *and* every expiration) and validates
it against subsequent realized volatility, without locating a specific
strike-price "flip point." Both are legitimate; don't present the strike-
level flip as if it were the original paper's own construct.

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
