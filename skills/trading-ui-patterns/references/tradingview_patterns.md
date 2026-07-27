# TradingView patterns

TradingView's identity is density-with-legibility: a terminal that shows a
lot of numeric information per screen without becoming unreadable, using
tabular figures, muted chrome, and color reserved almost entirely for
direction (never decoration).

## `tradingview_watchlist_row`

- **Symbol** — bold, left-aligned, often with a small exchange/market tag
  beside it in a muted pill.
- **Price** — right-aligned (or a fixed column), **tabular/monospaced-digit
  figures** so the row doesn't visually jitter as the last digit updates
  every second. This matters more than it sounds: proportional digits
  ("1" narrower than "8") make a live-updating price column shimmer
  distractingly even when the actual value barely moved.
- **Change value + change percent** — both shown, not one or the other; the
  percent is what most users scan for, the value gives magnitude context.
- **Direction color** — see the market-convention note below. This is the
  *only* semantic use of red/green in the row; nothing else in the row
  should borrow that color pair for an unrelated purpose (a chip color, a
  membership badge) because it dilutes the one signal red/green is supposed
  to carry.
- **Sparkline** (recommended, not required) — a real intraday line from
  actual price history, not a decorative icon. A static up/down arrow glyph
  in its place is the anti-pattern this checklist flags
  (`decorative_icon_in_place_of_real_sparkline`): it looks like data but
  carries none.
- **44pt minimum row height** for the tap target, independent of how compact
  the visual row looks — TradingView's watchlist rows read as dense but are
  still built on a real touch-target grid underneath.

### Direction color is not a fixed constant — it is market-dependent

| Market convention | Up | Down |
|---|---|---|
| US, UK, HK, EU, most of the world (`red_down_green_up`) | green | red |
| Mainland China, Taiwan (`red_up_green_down`) | red | green |

Red is an auspicious color in Chinese culture and is associated with rising
prices; the "Western" mapping is reversed. A component that hardcodes one
convention and gets pointed at the other market's feed renders every quote
backwards with no crash and no visibly "wrong" screenshot to someone who
doesn't already know the correct mapping for that market. See
`references/methodology.md` for how `pattern_audit.py`'s
`market_aware_fields` check catches exactly this.

## `tradingview_technical_rating_gauge`

The half-circle "Strong Sell → Strong Buy" gauge is an aggregated *vote*,
not a single computed number — that distinction should be visible in the UI,
not just in a tooltip:

- **Needle position** maps a normalized score in `[-1, 1]` to the gauge arc
  (180° for strong sell, 0° for strong buy is the TradingView convention;
  what matters structurally is that the needle position and the label
  agree).
- **Rating label** beneath the needle in large text (Strong Sell / Sell /
  Neutral / Buy / Strong Buy) — the needle alone is not legible enough to
  carry the result on its own.
- **Vote breakdown** (buy/sell/neutral counts) shown below the gauge, small
  but present — this is what makes the aggregate auditable rather than a
  black box; a user who distrusts the headline rating can see it's built
  from real underlying votes, not vibes.
- **Data-sufficiency floor.** A rating computed from a thin data window
  (under ~30 bars) is statistically weak; disclose that or suppress the
  gauge rather than show a confident needle position built on little data.
  Showing *no* rating when the data is insufficient is more honest than
  showing a neutral one — a "neutral" reading and "not enough data to say"
  are different claims and should not be visually identical.

## What breaks the pattern's identity

- Any chrome color beyond a narrow monochrome/blue-accent palette — a
  watchlist or chart screen that introduces unrelated bright colors for
  non-directional UI reads as off-brand for this pattern immediately.
- A gauge or rating shown with an empty or synthetic vote breakdown just to
  fill the space under it.
- Proportional (non-tabular) digits in any price/volume column that updates
  live.
