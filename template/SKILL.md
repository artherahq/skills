---
name: your-skill-name
description: >-
  Replace this with one or two sentences that say exactly when to trigger the
  skill, in the words a user would actually use. Name the concrete situations.
  Add a "Do NOT trigger for …" clause if the skill is easy to over-fire. This
  field is the only thing the model sees when deciding whether to load the skill.
---

# Your Skill Name

One paragraph: what discipline or capability this skill enforces, and why a
naive attempt at the task gets it wrong.

## When this matters

The situations that should fire this skill — including the phrasings a user is
likely to use instead of the precise technical term.

## Workflow — order matters

1. First step.
2. Second step.
3. ...

Write these as instructions to an agent, not prose for a human.

## Bundled resources

- `scripts/your_script.py` — what it does and how to run it (give the exact
  command; prefer a self-testing `--demo` path).
- `references/your_reference.md` — when to read it.
