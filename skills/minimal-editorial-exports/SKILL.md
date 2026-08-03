---
name: minimal-editorial-exports
description: >-
  An alternate visual style for aria-code's own generated exports — report
  covers, PPTX title slides, single-chart share images, Canva one-pagers —
  built on heavy negative space, one accent color, and restrained
  serif/monospace type, instead of the default dense institutional/dashboard
  look. Trigger for "极简", "杂志风", "editorial", "zine", "less corporate",
  "make the cover page quieter", "one number, lots of white space", or when
  the user wants a report/deck/chart export that reads as considered rather
  than templated-dashboard. Do NOT trigger for the default financial report
  body (tables, indicators, full analysis) — this governs cover pages, title
  slides, and single-focal-point exports only, never dense data views (use
  `terminal-software-design` or the existing institutional/bloomberg themes
  for those). Do NOT trigger to invent a generic aesthetic from nothing — use
  `ui-ux-pro-max` for open-ended exploration instead.
---

# Minimal Editorial Exports

Financial report tooling defaults to density — dark tables, corporate blue,
every indicator visible at once — because that's what the *body* of a report
needs. But aria-code also produces things that aren't report bodies: a cover
page, a PPTX title slide, a single chart meant to stand alone, a Canva
one-pager. Applying the dense-dashboard default to those is a mismatch: a
cover page crammed with the same density as the analysis behind it reads as
unfinished, not thorough. The fix is a second, deliberately restrained style
for exactly these single-focal-point surfaces — heavy negative space, one
accent color, one number or one chart doing the work, quiet typography
carrying the rest. Silence read as confidence in print design long before
software existed; the same logic applies here.

## When this matters

- A report's cover page or first slide, before the dense analysis begins
- A PPTX title slide (`aria.report.pptx` / `report_exporters.py`)
- A single chart meant to be shared standalone, not embedded in a full report
- A Canva brand-template autofill for a one-pager or social export
- Never the report *body* — tables, multi-indicator panels, and the
  institutional/bloomberg themes stay dense on purpose; this style is for the
  one surface per document that's allowed to be quiet

## Design rules

1. **70%+ quiet space.** The cover/title surface should be mostly negative
   space around one focal point — one number (e.g. the headline return), one
   chart, or one signal — not a summary of everything the document contains.
2. **One accent color, tied to real meaning.** If there's a directional
   signal, the accent is that signal's real color (gain/loss, buy/sell) —
   never a decorative color chosen for mood. If there's no signal, pick one
   restrained anchor color and don't reach for a second.
3. **Restrained type, not the safe default.** Serif or monospace over the
   generic sans-serif dashboard default; one size doing the heavy lifting
   (the headline number or title), everything else quiet caption-weight.
4. **Texture only where the format supports it.** An HTML/PDF cover
   (`report_generator.py`'s `export_pdf` path) can carry a subtle
   paper-grain or noise background; PPTX/DOCX covers (`report_exporters.py`)
   can't render texture the same way — for those, let space and type do the
   work instead of trying to fake grain.
5. **No borrowed dashboard chrome on the cover.** No sidebar, no nav, no
   multi-panel grid — a cover that reuses the report body's chrome isn't
   restrained, it's just a smaller dashboard.

## Applying this in aria-code

- **`report_generator.py`** — `generate_price_chart`'s `mpf.make_marketcolors(...)`
  call sets the chart palette; for a standalone/cover chart, drop it to a
  single accent + neutral rather than the full up/down + volume palette used
  in the report body.
- **`pdf_report.py`** — `THEMES` (`institutional`, `bloomberg`) are both
  dense-body themes; this style is for the *cover page* those themes render
  before the body starts, not a competing third dense theme.
- **`report_exporters.py`** — `markdown_to_pptx`'s title slide (the first
  slide, before per-heading slides start) is the one slide this style
  governs; keep it to one line of restrained type and real negative space,
  not a bullet list. Same for `markdown_to_docx`'s cover heading.
- **`canva_client.py`** — when building the brand template this style
  targets, keep the template itself minimal (one text field, one optional
  image/chart field); `autofill_design`'s `data` argument should carry one
  headline value, not a dense field set.

## Checklist

- [ ] Is at least 70% of the cover/title surface genuinely quiet, not just
      slightly less dense than the body?
- [ ] Is the one accent color tied to something real (a signal), or at least
      chosen once and not fought by a second color?
- [ ] Is the type restrained and specific, not the default dashboard sans?
- [ ] Did texture only get used where the export format can actually render
      it (HTML/PDF), not faked on PPTX/DOCX?
- [ ] Does the cover avoid reusing the report body's chrome (sidebar, nav,
      multi-panel grid)?
- [ ] Is this being applied to a cover/title/single-focal surface, not the
      dense report body itself?
