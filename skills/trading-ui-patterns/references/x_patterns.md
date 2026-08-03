# X (Twitter) patterns

X's density and restraint are the two things generic "social feed" UI
usually gets wrong: too much whitespace makes a timeline feel sparse and
slow to scan; too much decoration (filled icons at rest, gradient avatars,
emoji reactions) makes it feel like a toy rather than a place people spend
hours reading.

## `x_timeline_post`

A post is one row in an infinitely scrolling list, not a card floating in
space. No drop shadow, no rounded-card background distinct from the feed —
the separator is a hairline divider or simple padding, not a container.

- **Avatar** — circular, fixed size (40–48pt typical), tap target extends
  slightly beyond the visible circle.
- **Header line** — display name (bold) + handle (secondary color, `@handle`)
  + timestamp, all on one line, truncating the name before the handle if
  space is tight. Timestamp is *relative* ("3h", "2d", then a date once it's
  old enough) — an absolute timestamp here reads as foreign to the pattern.
- **Body text** — full width under the header, no left-indent past the
  avatar's column. Line-wraps naturally; links/mentions/hashtags get the
  brand accent color, not underline.
- **Media/chart embed** (optional) — rounded corners, fixed aspect ratio,
  never lets the image dictate the row's height unpredictably.
- **Action bar** — see `x_action_bar` below, always present, always at the
  bottom of the post.

Retweet/repost context ("X reposted") appears as a small icon + line *above*
the post header, in muted secondary color — not styled as if it were part of
the post's own content.

## `x_action_bar`

Four icons in a row: reply, repost, like, share (view count sometimes a
fifth, non-interactive). This is the pattern most naive rebuilds get
subtly wrong:

- **Outline by default, filled only once activated.** A like that's already
  filled-red before the user has ever tapped it is a broken affordance — it
  either lies about state or looks like every post is already liked.
- **Counts appear once there's a real count**, not as "0" placeholder text
  competing for attention with actual activity elsewhere in the feed.
  Whether to hide zero-counts entirely or show a bare icon with no number is
  a taste call; showing the literal digit "0" next to every icon on every
  post is the anti-pattern.
- **Even spacing, not edge-anchored.** The four/five actions distribute
  across the row's width rather than clustering left with a large gap to a
  lone share icon on the right.
- **44pt minimum tap target** per action even though the visual icon is much
  smaller — the hit area extends past the glyph, not just the glyph itself.
- **One icon family.** Mixing a filled Material icon for "like" with an
  outlined SF Symbol for "reply" reads as assembled from different kits, even
  if each icon individually looks fine.

## What breaks the pattern's identity

- A card-style container around each post (shadow, distinct background,
  visible corner radius) — that's a different pattern (closer to a forum
  post or a notification card), not X's timeline.
- Absolute timestamps in the main feed.
- Any action icon rendered as an emoji rather than a real icon glyph — emoji
  render inconsistently across platforms, can't be recolored/filled to show
  state, and carry no accessibility label.
