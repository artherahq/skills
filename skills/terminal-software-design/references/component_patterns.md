# Component patterns specific to terminal/software UI

### Sidebar / primary navigation
- If a sidebar has an empty/zero-state (no items yet), center the empty-state
  message in the *actual available space*, not pinned near the top with a long
  stretch of nothing below it — either the empty state should own the full
  available height (flex-centered), or the panel shouldn't reserve that much
  height until there's content to fill it.
- A collapsed/narrow-width state should hide or icon-only the sidebar, not let it
  fill 100% of a narrowed window while the main content area silently disappears —
  losing the actual working view because the sidebar took the whole viewport is a
  broken responsive floor, not a graceful degradation.

### Popovers, menus, floating panels
- A floating panel's background **must be visually distinct from what's behind
  it** — a real shadow plus a border a shade lighter/darker than the panel's own
  surface, not just a same-toned surface token with a `shadow-2xl` utility class
  that renders as effectively flat against a similarly-toned parent.
- A popover triggered from a button **must fully cover or clear that trigger** —
  a gap between the popover's edge and the trigger it opened from reads as two
  overlapping, disconnected UI elements, not one coherent menu. Compute the
  popover's offset from the trigger's actual height, don't guess a fixed pixel
  value that happens to work for one trigger size.

### Segmented toggles / mode switches
- The selected segment needs *more* than a background-color change if the
  unselected background and the container's own border are close in tone —
  add a ring/inset border or shadow on the selected pill so the segmented
  control still reads as a control, not decorative text, at a glance.
- Unselected labels should be legible at rest (not just on hover) — dimming them
  to near-invisible until hover means a first-time user can't tell the control
  has multiple options without moving the mouse over it.

### Sibling surfaces must share tokens
- If two panels sit side by side (e.g. a left sidebar and a right detail panel),
  and both are meant to read as "the same UI layer," they must use the literal
  same background token — not two different tokens that happen to render close
  in one theme. A `color-mix()` blend of a *different* base token than the
  sibling's flat token will drift visibly apart the moment blur, opacity, or a
  theme switch is involved, even if they looked close in a screenshot. (If the
  project has a `design-tokens.json` from the `ui-design-system` skill, this is
  a mechanical check: both surfaces should resolve to the same token name.)

### Empty states in a *working* tool
- Different from a marketing empty state ("no results, try X") — in a tool
  someone actively uses, the empty state should describe the next concrete
  action in the tool's own vocabulary ("Start a conversation to create your
  first strategy session"), not a generic "nothing here yet."
