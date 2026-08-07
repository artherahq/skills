---
name: ui-asset-sourcing
description: >-
  Source the actual assets a website or app needs — icons, imagery, logos,
  avatars, empty-state art — without hallucinating SVG paths, shipping emoji as
  icons, or dropping in stock photos that fight the palette. Trigger for "what
  icons should I use", "给这个网站配图", "add icons to this UI", "generate a hero
  image for this landing page", "这个空状态要放什么插图", "need a logo for this
  brand", or whenever a design direction exists and the remaining gap is the
  visual material to fill it. Names which icon set fits which aesthetic, how to
  fetch real icon and brand SVGs rather than inventing path data, and how to
  generate on-palette imagery with Aria Code's own image tools
  (`aria.report.generate_image_local` free/local, or `aria.report.generate_image`
  paid) when a stock photo would be wrong. Do NOT trigger to choose the design
  direction itself (use `industry-design-direction`) or to compile a single
  editorial poster (`minimal-editorial-poster`). Portable: self-contained prose,
  no script dependency.
---

# UI asset sourcing

A design direction with no assets becomes a wireframe with lorem ipsum and
grey boxes. Filling those boxes is where two specific, very visible failures
happen:

1. **Invented SVG path data.** A model asked for "a Stripe logo" or "a
   calendar icon" will confidently emit a `<path d="M12 2L2 7...">` that
   renders as an unrecognizable blob. Path data cannot be recalled correctly.
2. **Emoji standing in for icons.** 🚀 in a feature card is the single fastest
   tell of generated UI, and it breaks cross-platform (rendering differs per
   OS) and for screen readers.

Both are avoidable by *fetching* rather than *recalling*. That is most of what
this skill is.

## Icons

**Pick one set and stay in it.** Mixing sets is visible immediately — stroke
weights and corner radii will not match, and the interface reads as assembled
rather than designed.

| Set | Fits | Notes |
| --- | --- | --- |
| Lucide | Most product UI; the safe default | ~1500 icons, consistent 24×24 / 2px stroke, MIT |
| Heroicons | Tailwind projects | Outline + solid pairs, by Tailwind's authors, MIT |
| Phosphor | When you need weight variation | 6 weights including duotone, flexible, MIT |
| Tabler | Dense/data UI needing breadth | ~5000 icons, 24×24 / 2px stroke, MIT |
| Material Symbols | Android/Material products | Variable axes (weight, fill, grade), Apache 2.0 |
| Simple Icons | **Brand/company logos only** | Official marks — the correct source when you need a real logo |

**How to get the actual SVG** — never write path data from memory:

- Ask the user to install the package (`lucide-react`, `@heroicons/react`,
  `@phosphor-icons/react`, …) and import icons by name. This is the right
  answer for almost every real project: the names are memorable and correct,
  the path data comes from the package.
- If a raw SVG file is genuinely needed, direct the user to fetch it (the
  set's website, or its GitHub raw file) rather than producing one yourself.
- If you have web access in the current session, fetch it and paste the real
  markup. If you do not, say so and give the import line instead — a stated
  limitation is better than a plausible-looking wrong path.

**Consistency rules that matter more than the set you picked:**

- One nominal size (usually 24×24) with a fixed stroke width across the whole
  UI; scale via the container, not by redrawing at another weight.
- Icons that carry meaning need an accessible name (`aria-label`, or adjacent
  text). Decorative icons get `aria-hidden="true"` so they are not announced.
- An icon alone is rarely enough for a primary action — pair with a label
  unless the metaphor is universally understood (close, search, back).
- Match the icon style to the aesthetic: outline icons for minimal/Swiss,
  filled/duotone for playful/claymorphic, sharp geometric for brutalist. A
  rounded friendly icon set inside a brutalist layout fights the direction.

## Imagery

Decide first **what kind** of imagery the direction calls for — see
`references/imagery_direction.md` for the per-category guidance (photography,
illustration, abstract/gradient, 3D, or deliberately none). The wrong *kind*
is a bigger error than a mediocre execution of the right kind.

**When to generate rather than source stock:**

Generate when the image must sit inside the palette you already chose, when
the subject is specific to this product, or when stock would read as
generic-corporate (the smiling-team-around-a-laptop problem). Aria Code has
two backends, both MCP-exposed:

- `aria.report.generate_image_local` — self-hosted SDXL-Turbo. No API key, no
  per-call cost. Good for texture, abstract backgrounds, and light restyling.
  Weak at aggressive restyling and **cannot render legible text** — do not ask
  it for anything with words in the image.
- `aria.report.generate_image` — OpenAI `gpt-image-1`. Real per-call cost, so
  it requires `confirmed: true`; call `aria.report.estimate_image_cost` first.
  Markedly better at instruction-following, flat/graphic styles, and legible
  text.

Put the palette's hex values in the prompt. An image generated without them
will land near-but-not-on your colors, which reads worse than an obviously
different image.

**Source stock instead** when you need real people, real places, or
photojournalistic credibility — generated humans still fail on hands, teeth,
and crowd scenes, and a generated "customer photo" on a testimonial is a
misrepresentation, not a style choice. Point the user at Unsplash/Pexels
(free, permissive) and have them confirm the licence for commercial use
themselves.

## Logos and brand marks

- Real company logos: **Simple Icons** only. Do not draw them.
- The user's own logo: ask for the file. Do not generate a substitute and
  present it as theirs.
- A new logo for a new brand is a real design engagement, not an asset-fetch
  task — say that plainly rather than generating something disposable.

## Placeholder content

Grey boxes and lorem ipsum hide layout problems until they are expensive to
fix. Use realistic content: plausible names, real-length copy, and images at
the aspect ratio the real ones will use. A card designed against a 3-word
title breaks the moment a 14-word title arrives.

## Workflow

1. Confirm the design direction exists (style, palette, type). If not, stop —
   that is `industry-design-direction`'s job, and assets chosen before a
   direction will not match it.
2. Pick one icon set from the table, matched to the aesthetic, and state the
   install/import method.
3. Decide the imagery *kind* from `references/imagery_direction.md`.
4. For generated imagery: build prompts that carry the palette hex values,
   estimate cost if using the paid backend, and generate.
5. For stock or real logos: point at the correct source; do not fabricate.
6. Run the quality gate — prefer `scripts/asset_lint.py` over eyeballing the
   three mechanically-checkable items (see Automated Checks below).

## Automated Checks

Three of the Quality gate items below are mechanical, not judgment calls, so
`scripts/asset_lint.py` checks them by grepping the actual generated code
instead of relying on the gate being applied by eye:

```bash
python scripts/asset_lint.py path/to/src            # scan real files/dirs
python scripts/asset_lint.py --demo                 # no data needed
```

- `emoji_icon` (error) — an emoji character standing in for an interface icon.
- `invented_svg_path` (warn) — a long inline `<path d="...">` with no nearby
  source citation (an import, a `// source: ...` comment). Can't *prove* the
  path data was hand-recalled rather than fetched, but this is exactly the
  shape that failure takes — a "logo" with no cited source renders as a blob.
- `mixed_icon_set` (warn) — imports from more than one known icon library
  (Lucide, Heroicons, Phosphor, Tabler, react-icons) across the scanned paths.

The remaining Quality gate items (accessible names, palette hex values in
generated-image prompts, no fabricated people/places/brands, realistic
placeholder length) stay judgment calls this script doesn't attempt —
automating those would launder a guess as a verified fact, which is worse
than leaving them as prose. Note this script is intentionally separate from
`ui-design-system`'s `design_lint.py`: that one enforces code against the
*user's own declared design-tokens.json*, a different, tokens-shaped concern
from universal icon/asset hygiene, which applies whether or not a design
system has been frozen yet.

## Quality gate

- [ ] Zero emoji used as interface icons?
- [ ] Zero hand-written SVG path data — every icon and logo either imported by
      name, fetched from a real source, or explicitly flagged as needing the
      user to fetch it?
- [ ] One icon set throughout, at one nominal size and stroke width?
- [ ] Meaningful icons have accessible names; decorative ones are
      `aria-hidden`?
- [ ] Generated imagery carries the actual palette hex values in its prompt?
- [ ] Nothing generated that misrepresents a real person, place, or company —
      no synthetic "customer photos", no drawn-from-memory brand marks?
- [ ] Placeholder text at realistic length, not lorem ipsum at convenient
      length?

## References

- `references/imagery_direction.md` — which kind of imagery suits which design
  direction, prompt patterns that keep generated images on-palette, and the
  cases where generating is the wrong call
