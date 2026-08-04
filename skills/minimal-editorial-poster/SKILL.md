---
name: minimal-editorial-poster
description: >-
  Compile a minimal editorial/zine-poster prompt for a theme, sentence, mood,
  or brief from ANY domain aria-code touches — a financial story, a real-estate
  listing highlight, a sports recap, a general subject — not tied to
  financial-report styling. Trigger for "做一张极简海报", "zine风格的海报",
  "minimal poster for [subject]", "给这个故事配一张海报", or when the user
  wants a standalone poster-style creative asset rather than a data export.
  Produces a ready-to-use image-generation prompt and, when an image backend
  is configured, actually executes it via aria.report.generate_image_local /
  edit_image_local (self-hosted, no API key) or the OpenAI-backed equivalents
  — falls back to prompt-only + a non-image brief when neither is available.
  Do NOT trigger for styling aria-code's own report/PPTX/Canva exports (use
  `minimal-editorial-exports` for that — this skill is for a standalone
  poster from a theme, not a data-export cover).
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

aria-code can execute the compiled prompt directly when an image backend is
configured (see Execution below) — the compiled prompt is still the primary
artifact, but "compile and hand it off" is now the fallback path, not the
only path.

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

## Execution — turning the compiled prompt into a real image

aria-code has two image backends, both MCP-exposed (`packages/aria_mcp/server.py`),
mirroring the local-vs-cloud choice `local_llm_provider.py`/`openai_image_client.py`
already make for chat:

- **Local, self-hosted** (`local_image_provider.py`, default `stabilityai/sdxl-turbo`
  fp16) — `aria.report.generate_image_local` for a from-scratch anchor,
  `aria.report.edit_image_local` for an anchor that's an existing user photo.
  No API key, no per-call cost. Needs the optional `image_gen` extra
  installed and (once) ~4GB of fp16 weights downloaded — first call is slow,
  later calls fast (confirmed on M1 Pro/MPS: ~10s for a 4-step from-scratch
  generation once weights are cached).
- **OpenAI-backed** (`openai_image_client.py`, `gpt-image-1`) —
  `aria.report.generate_image` / `aria.report.edit_image`. Needs an OpenAI
  key (`/apikey set openai sk-...`); real per-call cost.

**Which tool to call is decided by the Anchor field (step 3):** an anchor
that's the user's own existing photo → the *edit* tool with that file's path;
any other anchor type (illustration, silhouette, block, specimen, type-only)
→ the *generate* tool with no input image.

**`strength` (edit tools only, 0–1) is the one parameter this skill has real
tuned guidance for** — it controls how much the output is allowed to diverge
from the input photo:
- 0.35–0.45: conservative — keeps the original composition/likeness close,
  treatment (duotone, texture) reads as a filter over the real photo
- 0.5–0.6: the default starting point — real restyling while the original
  subject and composition stay recognizable (confirmed on a real portrait:
  duotone + simplified background + texture all came through at 0.55)
- 0.65–0.75: aggressive — the anchor treatment dominates, useful when field 4
  (anchor treatment) calls for something far from a straight photo (e.g.
  full silhouette/line-art)

Steps: 4 is `sdxl-turbo`'s trained regime (`guidance_scale=0.0` to match) —
raising steps on a turbo-distilled model doesn't reliably improve quality,
it just costs more time; only raise it if you switch `model` to a
non-turbo checkpoint that expects real classifier-free guidance.

If neither backend is configured (extra not installed, no OpenAI key), say
so explicitly and fall back to the compiled-prompt-only output below — never
silently skip presenting anything.

## Workflow

1. Gather the theme/sentence/mood/brief from the user — ask if genuinely
   ambiguous, don't invent a subject from nothing.
2. Answer the nine first-principles fields in order for this specific
   subject.
3. Pick variation-axis values driven by what's actually different about
   this subject versus the last one compiled in the same session/batch.
4. Compile into the Output Format below.
5. Run the Quality Gate before presenting it.
6. If an image backend is configured (see Execution), actually call it —
   local first (no cost) unless the user asked for OpenAI specifically —
   using the Anchor field to choose generate vs. edit and, for edit, a
   `strength` from the tuned ranges above. Otherwise present the compiled
   prompt plus the non-image fallback brief and say plainly that no backend
   is configured, rather than silently doing nothing with it.

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

FALLBACK BRIEF (no image-gen backend configured)
A one-paragraph plain-language description of the same composition, for a
human designer or a non-image export path (e.g. handing to
minimal-editorial-exports for a text/chart-only equivalent) to work from.
```

When a backend is configured, the actual tool call follows immediately
after this block — anchor = existing photo → `aria.report.edit_image_local`
(or `_image` for OpenAI) with that file's path and a `strength` from the
tuned ranges above; any other anchor → `aria.report.generate_image_local`
(or `_image`) with the compiled prompt text.

## Quality Gate

- [ ] Exactly one anchor, one saturated color, one texture — none doubled up?
- [ ] Is the anchor color tied to something real about the subject, not
      arbitrary?
- [ ] Does attention geometry genuinely leave 70%+ empty, not just "less
      full than a normal poster"?
- [ ] Would this same compiled prompt work equally well for a completely
      different subject? If yes, it's too generic — revise field 3 (anchor)
      and field 6 (color) to be specific to this brief.
- [ ] If a backend is configured: chose edit vs. generate correctly from the
      Anchor field, and for edit, picked `strength` from the tuned ranges
      rather than defaulting blindly to 0.55 regardless of how far field 4
      (anchor treatment) actually wants to diverge from the source photo?
- [ ] If no backend is configured: said so explicitly and presented the
      fallback brief, not just a prompt nobody can act on?
- [ ] Confirmed this is a standalone poster request, not actually a request
      to style one of aria-code's own report/PPTX/Canva exports (that's
      `minimal-editorial-exports`)?
