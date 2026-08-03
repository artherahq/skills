# Agent Skill format

A skill is a directory whose entry point is a `SKILL.md` file. Aria reads the
frontmatter of every available skill at all times, but only loads the body when a
task matches the `description`. Keep the frontmatter tight and the body focused.

## Minimum

```
my-skill/
└── SKILL.md
```

```markdown
---
name: my-skill                 # kebab-case, unique, matches the folder name
description: >-                 # the single most important field — it is the
  One or two sentences that     # ONLY thing the agent sees when deciding whether
  say exactly when to trigger   # to load the skill. Name concrete triggers and,
  this skill, in the user's     # if useful, when NOT to trigger.
  own words.
---

# My Skill

The workflow. Write it as instructions to an agent, not prose for a human.
```

## With resources

```
my-skill/
├── SKILL.md
├── references/        # docs the skill points to ("read references/x.md when …")
├── scripts/           # runnable code the skill tells the agent to execute
└── agents/            # per-runtime interface descriptors (display name, prompt)
```

- **`references/`** — longer material the agent loads on demand. The SKILL.md
  body should link to it rather than inlining everything, so the always-loaded
  surface stays small.
- **`scripts/`** — executable helpers. Prefer instructing the agent to *run* a
  script over describing what it would compute. Make scripts self-testing
  (`--demo` or a no-arg smoke path) and dependency-light.
- **`agents/`** — how the skill presents itself in runtimes that need a
  human-facing entry point rather than an auto-fired description. Each file is
  named for its target runtime (`openai.yaml` today). The `description` in
  `SKILL.md` is written for a *classifier* deciding whether to load the skill;
  these fields are written for a *person* picking one off a list, which is why
  they are separate:

  ```yaml
  interface:
    display_name: "Risk Assessment"
    short_description: "Decompose portfolio risk from actual history"
    default_prompt: "Use $risk-assessment to decompose this portfolio's risk."
  ```

  `default_prompt` must reference the skill as `$<name>` so the invocation is
  copy-pasteable. Every skill in this catalog carries one — a skill without an
  interface descriptor is invisible in any runtime that lists skills for a
  human to choose from.

## `skill-policy.json`

Declares what the skill is allowed to reach for. A runtime that enforces
permissions reads this before activating anything; a runtime that doesn't can
ignore it. Unknown keys are ignored, so adding a field is backward-compatible.

```json
{
  "schema_version": "aria.skill-policy.v1",
  "allowed_tools": ["get_market_data", "web_search"],
  "agents": ["fundamental", "technical", "risk"],
  "permissions": ["network", "workspace-write"],
  "scripts": { "execution": "approval", "network": false, "workspace_write": false }
}
```

- **`allowed_tools`** — tool names the skill may call.
- **`agents`** — specialist agents the skill orchestrates, by registry name.
  Advisory: the loader never imports an agent registry, so a skill declaring
  agents still loads in runtimes that have none. Declare an agent only if the
  skill actually directs work to it — an aspirational list is worse than an
  empty one, because nothing fails when the agent is absent; the skill just
  quietly does less than its policy claims.
- **`permissions`** — `read-only`, `network`, `workspace-write`, broker levels.
- **`scripts`** — execution posture for anything under `scripts/`. Use
  `"execution": "none"` for reference-only skills that bundle no code.

Reference-only skills still need this file; omit it and the skill loads with
the most restrictive defaults, which is safe but silently wrong if the skill
actually needed a tool.

## Description guidance

The `description` is a triggering classifier, not marketing copy. Good
descriptions:

- name the concrete situations that should fire the skill, in the words a user
  would actually use;
- include near-miss phrasings the user might say instead of the technical term;
- state an explicit exclusion when the skill is easy to over-trigger.

## Conventions in this repo

- One concept per skill; split rather than overload.
- Bundled scripts must run from a clean checkout and skip (not fail) when an
  optional dependency is missing.
- Reference docs must stay consistent with the scripts they describe — when the
  code changes, update the reference in the same commit.
