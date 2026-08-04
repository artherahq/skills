---
name: minimal-editorial-poster
description: >-
  Compile a minimal editorial/zine-poster prompt for a theme, sentence, mood,
  or brief from ANY domain aria-code touches — a financial story, a real-estate
  listing highlight, a sports recap, a general subject — not tied to
  financial-report styling. Trigger for "做一张极简海报", "zine风格的海报",
  "minimal poster for [subject]", "给这个故事配一张海报", or when the user
  wants a standalone poster-style creative asset rather than a data export.
  Produces a ready-to-use image-generation prompt (for whichever image tool
  the runtime has) plus a non-image fallback brief, since aria-code has no
  image-generation tool built in today. Do NOT trigger for styling aria-code's
  own report/PPTX/Canva exports (use `minimal-editorial-exports` for that —
  this skill is for a standalone poster from a theme, not a data-export cover).
---

# Minimal Editorial Poster

A minimal zine poster says one thing, quietly, with almost the whole frame
left empty around it. That works the same way regardless of which of
aria-code's domains the subject comes from — `FINANCIAL_SCHEME`'s "AAPL beat
on margins", `REALTY_SCHEME`'s "this listing's cash flow is genuine", a
sports recap, or a subject with no domain scheme at all. This skill is the
domain-agnostic prompt compiler: it turns a theme into a disciplined image
prompt, the same way a magazine art director turns a headline into a cover
brief — one attention geometry, one anchor, one color, real restraint.

aria-code has no image-generation tool wired in today, so this skill's real
output is the **compiled prompt text** (and a non-image fallback brief) —
handing that prompt to whatever image-generation capability the runtime has
is the caller's job, not this skill's.

## When this matters

- A standalone poster-style asset for a theme, headline, or brief — from
  any domain, not just finance
- The user explicitly asks for "minimal", "zine", "editorial", or "poster"
  styling for a piece of content, distinct from a data export
- Never for styling aria-code's own report covers/PPTX/Canva exports — that
  is `minimal-editorial-exports`'s job, and the two skills should not both
  fire for the same request

## First-principles compiler — answer these in order

Answering out of order produces a prompt that looks assembled rather than
composed — each answer constrains the next.

1. **Canvas** — aspect ratio and surface (tall poster, square card, wide
   banner) and ground material (aged paper, plain matte, raw canvas).
2. **Attention geometry** — what fraction of the frame is empty (70-90% is
   the zine default) and where the one occupied region sits.
3. **Anchor** — the single subject that fills that occupied region: a
   photo-like image, a cut-paper silhouette, a solid color block, a small
   illustration, a specimen-style object, a short line of type standing
   alone. Pick ONE — never a scene with multiple competing subjects.
4. **Anchor treatment** — how that one anchor is rendered: full color,
   duotone, line art, halftone, high-contrast silhouette.
5. **Typography** — serif, typewriter, or monospace; how much of the frame
   type occupies (usually very little — a title and maybe one line, never a
   paragraph).
6. **Color logic** — one high-saturation anchor color against a
   desaturated/neutral ground. See Color Engine below.
7. **Texture** — the print-defect layer: xerox grain, risograph
   misregistration, halftone dots, letterpress impression, scanner noise.
   Pick one, applied subtly — texture is atmosphere, not the subject.
8. **Emotional temperature** — quiet, wistful, plain, deadpan, tender. Not
   loud, not commercial, not dramatic — this is an editorial/indie register,
   not an ad.
9. **Hard avoids** — see Negative Constraints; name explicitly in the
   compiled prompt what this is NOT, since image models default toward the
   commercial-poster look this style rejects.

## Color Engine

- Exactly one saturated anchor color. Everything else is paper-neutral,
  aged-white, muted grey, or ink-black.
- The anchor color should come from something real about the subject when
  one exists (a domain signal's real color, a detail mentioned in the
  brief) — not an arbitrary pretty color, the same principle
  `minimal-editorial-exports` applies to report covers.
- Never two saturated colors fighting for attention.

## Variation axes — don't compile the same poster every time

Running this compiler repeatedly for a batch (a week of stories, a set of
listings) with one fixed recipe becomes its own template. Vary, driven by
the actual subject each time, not at random:

- **Attention geometry** — center-fragment, lower-third float, upper
  corner block, dual-panel split, type-led (no image anchor at all)
- **Anchor type** — photo/illustration/silhouette/block/specimen/type-only
- **Texture** — rotate across xerox/riso/halftone/letterpress/scan-noise
- **Temperature** — quiet vs. plain vs. wistful vs. deadpan

## Workflow

1. Gather the theme/sentence/mood/brief from the user — ask if genuinely
   ambiguous, don't invent a subject from nothing.
2. Answer the nine first-principles fields in order for this specific
   subject.
3. Pick variation-axis values driven by what's actually different about
   this subject versus the last one compiled in the same session/batch.
4. Compile into the Output Format below.
5. Run the Quality Gate before presenting it.
6. Present the compiled prompt — and if the runtime has no image-generation
   tool available, say so explicitly and offer the non-image fallback brief
   instead of silently doing nothing with it.

## Negative Constraints

Never: full-bleed busy scenes, commercial/advertising headline layouts,
product-ad composition, logos or brand marks, glossy 3D renders, cinematic
lighting, neon, cartoon style, dense scrapbook collage, long text blocks,
stock-photo realism, multiple competing focal subjects.

## Output Format

```
POSTER PROMPT
Canvas: <aspect ratio + surface>
Attention geometry: <negative-space % + occupied region position>
Anchor: <the one subject> — <treatment>
Typography: <face + how little of the frame it uses>
Color: <one anchor color> on <neutral ground>
Texture: <one texture, applied subtly>
Temperature: <one register>
Avoid: <hard avoids relevant to this brief>

FALLBACK BRIEF (no image-gen tool available)
A one-paragraph plain-language description of the same composition, for a
human designer or a non-image export path (e.g. handing to
minimal-editorial-exports for a text/chart-only equivalent) to work from.
```

## Quality Gate

- [ ] Exactly one anchor, one saturated color, one texture — none doubled up?
- [ ] Is the anchor color tied to something real about the subject, not
      arbitrary?
- [ ] Does attention geometry genuinely leave 70%+ empty, not just "less
      full than a normal poster"?
- [ ] Would this same compiled prompt work equally well for a completely
      different subject? If yes, it's too generic — revise field 3 (anchor)
      and field 6 (color) to be specific to this brief.
- [ ] Named the fallback brief for runtimes without image-generation, not
      just silently produced a prompt nobody can use?
- [ ] Confirmed this is a standalone poster request, not actually a request
      to style one of aria-code's own report/PPTX/Canva exports (that's
      `minimal-editorial-exports`)?
