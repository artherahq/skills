# Trading212 patterns

Trading212's identity is the opposite instinct from TradingView's: hide
complexity a retail investor doesn't need at the moment of action, and never
let the primary action (place an order) be reachable before the input that
determines its consequences is valid.

## `trading212_order_ticket`

The buy/sell sheet is deliberately simpler than a professional order ticket
— no order-type picker, no time-in-force, no advanced routing options
visible by default:

- **Side toggle** (buy/sell) — a two-state segmented control, not a
  dropdown; the current side's color (buy=green-leaning, sell=red-leaning in
  most builds) tints the confirm button so the two states are visually
  distinct at a glance, not just by the toggle's own label.
- **Quantity-vs-value toggle** — the single most distinctive Trading212
  pattern: the user can enter either "how many shares" or "how much money",
  toggled with one tap, and the app converts between them live. A ticket
  that only accepts share count (forcing mental math for "I want to invest
  $500") is missing this pattern's core idea, not just a minor omission.
- **Estimated total** — must recompute live as quantity/value changes.
  Showing a number computed from the *previous* input state right up until
  submit is the specific failure this checklist flags
  (`estimated_total_updates_live`): the user is looking at the number to
  decide whether to confirm, so it has to be current.
- **Confirm action** — single, primary, and disabled/inert until the input
  is valid (nonzero quantity/value, within available cash for a buy). A
  confirm button that's tappable before that point invites an accidental or
  meaningless submission. Because this is a high-consequence, hard-to-fully-
  reverse action, its tap target should exceed the generic 44pt minimum
  (48pt+), not just meet it.
- **Fee disclosure** (recommended) — shown on the ticket itself before
  commit, not revealed only in a post-trade receipt. Hiding a real fee until
  after the user has already confirmed is the specific anti-pattern flagged
  here (`hidden_fee_disclosed_only_after_confirm`) — even a "no commission"
  claim should be visible pre-commit, not implied by its absence.

## `trading212_holding_row`

- **Logo or mark** — real brand mark for the instrument, not a generic
  placeholder glyph, so a portfolio list is scannable by logo the way a real
  brokerage app is.
- **Name** — full instrument name, not just ticker, since retail users
  recognize company names faster than tickers for anything outside their
  most-watched symbols.
- **Current value** — the position's present market value, not cost basis,
  as the primary number.
- **P/L value + P/L percent** — both shown together; a percent alone with no
  currency value forces the user to do their own multiplication to know if a
  move actually matters in absolute terms (the specific anti-pattern here is
  `pl_percent_without_pl_value`). Color follows the sign of the P/L, not an
  arbitrary per-row color scheme — a green P/L on a losing position because
  of a decorative color choice unrelated to the actual gain/loss
  (`pl_color_independent_of_sign`) is a correctness bug dressed as styling.
- **Quantity / average cost** (recommended) — usually revealed on tap or in
  a secondary line rather than cluttering the primary row, but present
  somewhere in the component.

## What breaks the pattern's identity

- An order ticket that exposes order-type/time-in-force/routing controls by
  default — that's a professional ticket (closer to the TradingView/
  institutional pattern), not Trading212's simplified one.
- A confirm button that is always tappable regardless of input validity.
- A holdings row whose color for gain/loss doesn't track the actual sign of
  the P/L.
