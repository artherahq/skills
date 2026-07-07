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
└── scripts/           # runnable code the skill tells the agent to execute
```

- **`references/`** — longer material the agent loads on demand. The SKILL.md
  body should link to it rather than inlining everything, so the always-loaded
  surface stays small.
- **`scripts/`** — executable helpers. Prefer instructing the agent to *run* a
  script over describing what it would compute. Make scripts self-testing
  (`--demo` or a no-arg smoke path) and dependency-light.

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
