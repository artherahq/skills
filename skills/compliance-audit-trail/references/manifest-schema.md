# Governance manifest contract

Every field below is required unless marked optional. The validator
(`scripts/governance_manifest_gate.py`) enforces this mechanically.

| Field | Type | Notes |
|---|---|---|
| `system_name` | str | |
| `as_of` | str | ISO date; drives the `stale_manifest` staleness check |
| `capability_claims` | list of `{claim, evidence}` | every claim needs a non-empty evidence pointer — a code path, test name, or metric. Empty evidence fails the whole manifest |
| `required_gates` | list of str | the gate names a strategy/model must clear to count as "production scope" — e.g. `["ic_significance", "backtest_gate", "hac_test"]`. Defined once, checked against every entry below |
| `production_scope` | list of `{asset, passed_gates}` | `passed_gates` must be a superset of `required_gates` for every entry, or that entry fails the gate. "Has a model file" is not "passed the pipeline" — this field is where that distinction gets checked mechanically instead of asserted in prose |
| `risk_controls` | list of `{name, declared_present, verified_triggering, evidence}` | a control with `declared_present: true` and `verified_triggering: false`/absent fails — code existing and code running under test are different claims. `verified_triggering: true` without `evidence` warns |
| `audit_trail` | `{decision_log_exists, evidence}` | `decision_log_exists: false` fails — "reconstructible if asked" does not count as a persisted trail |
| `compliance_checks` | list of `{name, implemented}` | any `implemented: false` entry warns (not fails) — an honestly-scoped rule set that says what it doesn't cover is not itself a governance gap |
| `known_limitations` | list of str | an **empty** list warns. Every real system has boundaries; an empty list more often signals omission than a genuinely limitation-free system |

## Why an empty `known_limitations` is a flag, not a pass

This is the one rule in this gate that inverts the usual "empty = fine"
instinct on purpose. A capability-claims section with zero claims is
uninformative but not dishonest. A limitations section with zero entries,
for any system that has actually been run against real data, is usually
either an incomplete review or a marketing document wearing a due-diligence
document's clothes. The gate treats it as a WARN, not a FAIL, because it is
possible (if unusual) for a narrowly-scoped system to genuinely have none —
but it should never pass silently.

## Staleness

`as_of` older than `--staleness-days` (default 90) warns
(`stale_manifest`) — a governance document that never gets re-verified
against the current state of the system it describes eventually describes a
system that no longer exists. An unparseable `as_of` warns too
(`unparseable_as_of`) rather than silently skipping the check.

## What this gate does NOT do

- It cannot verify that `evidence` pointers are *true* — only that they
  exist. Evidence that turns out to be wrong or fabricated is a separate,
  worse problem this structural gate cannot catch; someone still has to
  actually check the pointer.
- It is not a regulatory rule engine. `compliance_checks` is whatever list
  the manifest author declares; the gate does not know what a complete
  regulatory rule set for any given jurisdiction looks like. An honest,
  short list that says what it does *not* cover (per the guardrail above)
  is the correct output of this skill, not a failure to be complete.
- It does not run the risk controls or gates themselves — `verified_triggering`
  and `passed_gates` are inputs the manifest author asserts, which is why the
  companion skills (`backtest-validation`, `risk-assessment`,
  `multiple-testing-correction`) exist to actually produce those results
  before they go into a manifest.
