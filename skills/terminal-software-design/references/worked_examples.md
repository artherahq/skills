# Worked examples — real bugs, not hypotheticals

These are actual defects caught and fixed in a production Electron trading
terminal, kept here as concrete before/after reference rather than abstract
rules. Each maps to a guardrail in `SKILL.md` or another reference file.

## 1. Native window background bleeding at theme boundaries

**Before**: `backgroundColor: '#0A1220'` hardcoded at `BrowserWindow` creation,
app default theme is light.

**Symptom**: a dark line/sliver visible at the top and left edges of the window
in light mode, before/during paint.

**Fix**: default to the app's actual primary theme color, and add an IPC channel
(`theme:sync`) the renderer calls every time it resolves its theme (including on
initial load), so `mainWindow.setBackgroundColor()` always matches reality
instead of a guess frozen at window-creation time. See
`electron_chrome_pitfalls.md`.

## 2. Popover blending into its background and not clearing its trigger

**Before**: an account popup used `background: var(--surface-2)` with a flat
`shadow-2xl` utility, positioned `bottom-7 left-14` relative to its trigger
button.

**Symptom**: the popup blended into the sidebar behind it (both warm-dark, low
contrast), and sat close enough to its trigger that the trigger's own row was
still partially visible peeking out below the popup — reading as two
overlapping, disconnected elements.

**Fix**: bumped to `surface-3` (a full layer lighter), added a real
multi-layer `box-shadow` plus a `border-hover` outline, and repositioned so the
popup's bottom edge fully clears the trigger's actual rendered height instead
of a small fixed offset. See `component_patterns.md` → Popovers.

## 3. Segmented toggle reading as plain text

**Before**: a two-option segmented toggle used `bg-surface-3 text-t1` for the
selected pill and bare `text-t3` (tertiary/dimmest) for the unselected label,
inside a container with a similarly-toned border.

**Symptom**: at a glance the control read as plain text, not an interactive
toggle — selected vs. unselected were both too close in tone to the
container's own border.

**Fix**: added `ring-1 ring-inset ring-border-hover` plus a subtle shadow to
the selected pill, and bumped the unselected label from tertiary to secondary
text color so it's legible before hover, not just after. See
`component_patterns.md` → Segmented toggles.

## 4. Sibling surfaces drifting apart despite "matching" tokens

**Before**: three right-side panels (a task list, a routines list, and an AI
side-panel) used a shared `.glass` utility class built on `color-mix(var(--base)
94%, transparent)` with backdrop blur, while the main left sidebar used a flat
`background: var(--surface-2)` — a *different* base token, not just a different
opacity of the same one.

**Symptom**: the right panels read as a visibly different, slightly-off shade
from the left sidebar despite both being "supposed" to be the same UI layer.

**Fix**: switched the three right-side panels to the same flat `bg-surface-2`
token the sidebar uses, dropping the separate glass/blur treatment entirely
rather than trying to tune the blend to match by eye. See
`component_patterns.md` → Sibling surfaces.
