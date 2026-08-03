# Density, color, and data — the core disciplines

## 1. The core inversion: density is not the enemy

Marketing-site instinct says "give it room to breathe." In a tool someone operates
daily, that instinct is usually wrong:

- **Default denser, not airier.** A trading terminal, log viewer, or admin table
  should show more real rows/fields per screen, not fewer. Padding that would read
  as "premium" on a pricing page reads as "I can't see anything" in a data grid.
- **Every empty area needs a job.** If a panel has visible dead space, either
  something is missing (a summary strip, a secondary metric, a contextual action)
  or the panel is oversized for its content — shrink it, don't decorate the gap.
  A screen that's 60% blank below an empty-state message is not "clean," it's
  unfinished — the empty state should be *sized to* the space it's centered in,
  not floating in the top third of a much larger area.
- **Scanning beats reading.** Surface the summary before the detail. State should
  be visible in *form*, not just value — a colored dot, a pill, a severity stripe —
  so what needs attention is visible without reading every row.

## 2. Color: semantic is not brand

This is the single most common mistake in dashboard/terminal UI:

- **Semantic color (good/warning/critical, up/down, buy/sell) is a separate system
  from the brand accent color.** Don't let your one accent hue also mean "positive"
  — the moment you need to show a genuinely bad state, you either reuse the accent
  (confusing) or invent a second ad-hoc color (inconsistent).
- **Financial/data convention**: green=up/positive, red=down/negative is near-universal
  and shouldn't be reinvented for novelty — but stay aware of red/green colorblindness;
  pair color with a directional glyph (▲/▼) or sign (+/−), never color alone.
  (If the component is specifically a trading/quote row matching X/TradingView/
  Trading212 conventions, the `trading-ui-patterns` skill's market-convention table
  is the authority on which market uses which direction color — mainland China and
  Taiwan invert it.)
- **Reserve saturated color for state, not decoration.** A dashboard where every card
  has a colored left-border "for style" has no visual hierarchy left when something
  is *actually* wrong — the alert has nothing to stand out against.

## 3. Data: monospace and alignment are not optional

- Any column of numbers that should visually compare (prices, percentages, P&L,
  timestamps) needs `font-variant-numeric: tabular-nums` or a monospace/tabular
  numeral face — proportional digits drift out of alignment and the eye can't
  scan a column.
- Right-align numeric columns, left-align text columns. Don't center either.
- Fixed decimal precision per column (`142.30` not `142.3`) — ragged decimals
  break the same scanning the alignment was trying to preserve.
- Truncate long text with a title/tooltip for the full value, never wrap a table
  cell and reflow the row height — one long symbol name breaking a whole table's
  row rhythm is worse than truncating it.

## 4. Keyboard-first, not keyboard-optional

Software people live in gets keyboard affordances marketing sites don't need:

- Every primary action needs a visible shortcut hint (⌘K, /, Esc) somewhere
  discoverable — a command palette or menu, not hidden knowledge.
- Focus states must be visible and distinct from hover states — in a tool driven
  by keyboard nav as much as mouse, an invisible focus ring is a real usability bug,
  not a nitpick.
- Modal/popover dismissal: Esc must work, and clicking the scrim must work — don't
  make either the only way out.
