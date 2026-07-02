# Arthera Skills

[![test](https://github.com/artherahq/skills/actions/workflows/test.yml/badge.svg)](https://github.com/artherahq/skills/actions/workflows/test.yml)

Reusable [Agent Skills](https://docs.anthropic.com/en/docs/claude-code/skills) for
quantitative finance research, extracted from the Aria toolchain so they can be
installed into any Claude Code project — not just Aria. Maintained by
[`artherahq`](https://github.com/artherahq).

A skill is a folder of instructions, scripts, and references that Claude loads
dynamically when the task matches. This repo follows the same layout as
[`anthropics/skills`](https://github.com/anthropics/skills): a flat `skills/`
catalog, a `spec/` describing the format, a `template/` to start a new skill, and
a `.claude-plugin/marketplace.json` so the whole repo is installable as a plugin
marketplace.

## Skills

| Skill | What it does |
|---|---|
| [`point-in-time-research`](skills/point-in-time-research) | Enforces point-in-time data discipline when backtesting factors or strategies. Catches the three silent leaks (period-end dating, latest-value overwrite, same-session execution), quantifies the distortion with a four-variant A–D information-set comparison, and runs the validation gauntlet. Ships a runnable harness (`scripts/information_set_compare.py --demo`). |
| [`equity-research-report`](skills/equity-research-report) | Produces comprehensive equity reports through an auditable plan, normalized evidence bundle, specialist agents, deterministic fallbacks, critic pass, and executable completion gates. |

## Install

In any Claude Code project:

```
/plugin marketplace add artherahq/skills
/plugin install quant-research-skills@aria-skills
```

Or point at a local checkout during development:

```
/plugin marketplace add /Users/mac/Desktop/aria-skills
```

Aria Code discovers the same catalog through `ARIA_SKILLS_PATH` or a sibling
checkout and registers names as `plugin:skill`, for example:

```text
$quant-research-skills:equity-research-report
$quant-research-skills:point-in-time-research
```

`/skills doctor` verifies catalog integrity and declared permissions.
`/skills trace` shows why a Skill was selected or blocked.

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
├── skills/
│   ├── point-in-time-research/
│   │   ├── SKILL.md         # triggering + workflow
│   │   ├── skill-policy.json
│   │   ├── references/      # methodology, audit checklist
│   │   └── scripts/         # the A–D harness + its tests
│   └── equity-research-report/
│       ├── SKILL.md
│       ├── skill-policy.json
│       ├── references/      # completion and provenance policy
│       └── scripts/         # report-manifest validator + tests
├── spec/                    # the SKILL.md format, briefly
├── scripts/                 # catalog integrity tooling
└── template/                # scaffold for a new skill
```

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
