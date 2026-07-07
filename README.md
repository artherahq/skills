# Arthera Skills

[![test](https://github.com/artherahq/skills/actions/workflows/test.yml/badge.svg)](https://github.com/artherahq/skills/actions/workflows/test.yml)

The skill catalog for **Aria Code** — Arthera's AI quant terminal. Each skill
packages one piece of research discipline (point-in-time data hygiene, backtest
trust gates, risk decomposition, strategy spec gates…) as instructions plus
runnable verification scripts that Aria loads dynamically when a task matches.
Maintained by [`artherahq`](https://github.com/artherahq).

The catalog uses the open Agent Skills layout — a flat `skills/` directory, a
`spec/` describing the format, a `template/` for new skills, and a plugin
`marketplace.json` — so the same skills also run in any Agent-Skills-compatible
runtime. Aria Code is the first-class consumer: its portable skill loader
verifies the catalog against `skills.lock.json` before anything executes.

## Skills

| Skill | What it does |
|---|---|
| [`point-in-time-research`](skills/point-in-time-research) | Enforces point-in-time data discipline when backtesting factors or strategies. Catches the three silent leaks (period-end dating, latest-value overwrite, same-session execution), quantifies the distortion with a four-variant A–D information-set comparison, and runs the validation gauntlet. Ships a runnable harness (`scripts/information_set_compare.py --demo`). |
| [`backtest-validation`](skills/backtest-validation) | Validates whether a backtest is trustworthy before any conclusion: honest metric set, turnover cost ladder, chronological IS/OOS split, stationary-bootstrap Sharpe CI, and the Deflated Sharpe Ratio against disclosed trials. Verdict gates (PASS/WARN/FAIL) with a runnable harness (`scripts/validation_gauntlet.py --demo`). |
| [`risk-assessment`](skills/risk-assessment) | Decomposes portfolio/strategy risk from its actual history: VaR/CVaR with Cornish–Fisher tail adjustment, drawdown, concentration (effective N), diversification illusion via pairwise correlation, historical worst windows, and labeled linear beta shocks. Flags → risk level with mandatory disclosures; runnable harness (`scripts/risk_profile.py --demo`). |
| [`factor-research`](skills/factor-research) | Judges whether a cross-sectional factor genuinely predicts returns: per-period rank IC/IR/t-stat, decay across horizons, quantile monotonicity, sub-period sign-flip detection, and turnover via rank autocorrelation. Verdict routes survivors to backtest-validation; runnable harness (`scripts/factor_evaluate.py --demo`). |
| [`strategy-generation`](skills/strategy-generation) | Turns trading ideas into disciplined specs and implementations through a six-stage pipeline with three executable gates: a spec validator (hard risk controls, cost assumption, overfit preflight, forbidden-claim scan, honesty ledger for tried variants), then backtest-validation, then risk-assessment. Deploy advice caps at paper trading (`scripts/validate_strategy_spec.py --demo`). |
| [`portfolio-optimization`](skills/portfolio-optimization) | Estimation-robust weights with no expected-return inputs: inverse vol, long-only min variance, ERC risk parity, and inline HRP — plus a walk-forward `compare` mode that reports honestly when the optimizer fails to beat equal weight out-of-sample. Disclosed covariance shrinkage; weights ship with risk contributions (`scripts/optimize_portfolio.py --demo`). |
| [`execution-position`](skills/execution-position) | The pre-trade gate: sizes a signal (vol-target, or fractional Kelly only from a declared edge, hard-capped at 0.25), checks position/gross/cash/liquidity limits and stop-distance sanity, estimates costs, and emits paper-only order intents — live execution fails mechanically (`scripts/position_gate.py --demo`). |
| [`equity-research-report`](skills/equity-research-report) | Produces comprehensive equity reports through an auditable plan, normalized evidence bundle, specialist agents, deterministic fallbacks, critic pass, and executable completion gates. |

## Install

Aria Code discovers the catalog through `ARIA_SKILLS_PATH` or a sibling
checkout and registers each skill as `plugin:skill`:

```bash
git clone https://github.com/artherahq/skills aria-skills
export ARIA_SKILLS_PATH=/path/to/aria-skills   # or keep it next to aria-code
```

```text
$quant-research-skills:point-in-time-research
$quant-research-skills:factor-research
$quant-research-skills:backtest-validation
$quant-research-skills:risk-assessment
$quant-research-skills:strategy-generation
$quant-research-skills:portfolio-optimization
$quant-research-skills:execution-position
$quant-research-skills:equity-research-report
```

Inside Aria Code:

- `/skills doctor` verifies catalog integrity and declared permissions.
- `/skills trace` shows why a skill was selected or blocked.

The repo doubles as a standard plugin marketplace (`artherahq/skills`), so any
Agent-Skills-compatible runtime can install the same catalog.

## Integrity And Permissions

- `.claude-plugin/skills.lock.json` pins each Skill tree to a SHA-256 digest.
- `skill-policy.json` declares tools, runtime permissions, and script policy.
- Bundled scripts are never pre-authorized; Aria's normal command approval still applies.
- Regenerate and verify the lock after changing a Skill:

```bash
python scripts/build_skill_lock.py
python scripts/build_skill_lock.py --check
```

## Layout

```
aria-skills/
├── .claude-plugin/
│   ├── marketplace.json     # installable marketplace metadata
│   └── skills.lock.json     # versioned content-integrity lock
├── skills/                  # every skill follows the same shape:
│   └── <skill-name>/
│       ├── SKILL.md         # triggering + workflow + guardrails
│       ├── skill-policy.json# declared tools / permissions / script policy
│       ├── references/      # methodology, thresholds, schemas
│       └── scripts/         # runnable harness or gate + its pytest suite
├── spec/                    # the SKILL.md format, briefly
├── scripts/                 # catalog integrity tooling (skills.lock builder)
└── template/                # scaffold for a new skill
```

Every skill ships an executable verifier with a `--demo` mode — the discipline
is enforced by scripts and exit codes, not by prose.

## Run the bundled harness

The point-in-time skill ships a self-contained comparison harness. Verify it
with no data:

```bash
cd skills/point-in-time-research/scripts
python information_set_compare.py --demo
```

It embeds a deliberate look-ahead edge and shows the earnings factor's alpha
collapse from ~72% (naive, period-end-dated, revised values) to ~0% under strict
point-in-time alignment.

Tests (pandas/numpy required; they skip cleanly where absent):

```bash
pytest skills/point-in-time-research/scripts/test_information_set_compare.py
```

## License

Apache-2.0. See [LICENSE](LICENSE).
