#!/usr/bin/env python3
"""poster_gate.py — compiles a minimal-editorial-poster spec into the skill's
Output Format prompt block, then runs the SKILL.md Quality Gate as code
instead of a checklist a human has to remember to apply.

The failure mode this exists to catch isn't a crash — it's a poster that
*reads* fine in isolation but quietly breaks the discipline: two saturated
colors competing, a "hard avoid" term (cinematic lighting, commercial
headline layout, glossy 3D) leaking into the very fields meant to avoid it,
negative space that's "less full than usual" instead of genuinely 70%+, or
a compiled prompt so generic it would paste unchanged onto a completely
different subject. Each of these looks like a reasonable poster brief right
up until you compare it against the skill's own stated rules — exactly the
class of error a deterministic gate catches and a first read-through misses.

`demo()` reproduces a real instance: the commercial travel-poster prompt
this skill's own author sent to an image tool for a London skyline photo
before this gate existed, side by side with the corrected minimal-editorial
compile for the same subject — one FAILs, one PASSes, same source photo.

Try it with no data:  python poster_gate.py --demo
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

# Terms straight out of SKILL.md's own Negative Constraints — if any of these
# leak into a field meant to describe what the poster actually looks like,
# the compiled prompt is fighting itself.
FORBIDDEN_TERMS = [
    "cinematic lighting", "cinematic", "commercial", "advertising",
    "product-ad", "product ad", "glossy 3d", "3d render", "neon",
    "cartoon", "scrapbook collage", "stock photo", "stock-photo",
    "dramatic", "loud", "logo", "brand mark",
]

_ALLOWED_TEMPERATURES = {"quiet", "wistful", "plain", "deadpan", "tender"}

# Anchor-treatment keyword -> img2img strength range, straight out of the
# skill's tuned guidance (confirmed 0.55 on a real portrait for the
# duotone+simplify case).
_STRENGTH_AGGRESSIVE = (0.65, 0.75)
_STRENGTH_DEFAULT = (0.50, 0.60)
_STRENGTH_CONSERVATIVE = (0.35, 0.45)


def recommend_strength(anchor_treatment: str) -> Dict[str, Any]:
    """Only meaningful when anchor_is_photo is true (edit_image, not
    generate_image) — the generate path has no source image to diverge from."""
    t = (anchor_treatment or "").lower()
    aggressive_kw = ["silhouette", "line art", "line-art"]
    conservative_kw = ["close to original", "keeps the original", "filter over the real photo", "conservative"]
    if any(kw in t for kw in aggressive_kw):
        lo, hi = _STRENGTH_AGGRESSIVE
        rationale = "anchor treatment calls for a rendering far from a straight photo"
    elif any(kw in t for kw in conservative_kw):
        lo, hi = _STRENGTH_CONSERVATIVE
        rationale = "anchor treatment wants the original composition/likeness kept close"
    else:
        lo, hi = _STRENGTH_DEFAULT
        rationale = "default starting point — real restyling while subject stays recognizable"
    return {"range": [lo, hi], "rationale": rationale}


def compile_prompt(spec: Dict[str, Any]) -> str:
    """Renders SKILL.md's Output Format POSTER PROMPT block from a spec dict.
    Does not validate — call audit_poster_spec for that. Kept separate so a
    caller can see what got compiled even from a spec that fails the gate."""
    colors = spec.get("colors") or []
    anchor_colors = [c for c in colors if c.get("role") == "anchor"]
    ground_colors = [c for c in colors if c.get("role") != "anchor"]
    color_line = (
        f"{', '.join(c.get('name', '?') for c in anchor_colors) or '?'} on "
        f"{', '.join(c.get('name', '?') for c in ground_colors) or 'neutral ground'}"
    )
    lines = [
        "POSTER PROMPT",
        f"Canvas: {spec.get('canvas', '?')}",
        f"Attention geometry: {spec.get('negative_space_pct', '?')}% empty — {spec.get('anchor_position', 'anchor region')}",
        f"Anchor: {spec.get('anchor', '?')} — {spec.get('anchor_treatment', '?')}",
        f"Typography: {spec.get('typography', '?')}",
        f"Color: {color_line}",
        f"Texture: {spec.get('texture', '?')}",
        f"Temperature: {spec.get('temperature', '?')}",
        f"Avoid: {', '.join(spec.get('avoids') or []) or '(none stated)'}",
    ]
    return "\n".join(lines)


def audit_poster_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic checklist audit mirroring SKILL.md's Quality Gate.
    Not aesthetic judgment — only checks the spec itself makes answerable:
    field presence, counts, and whether hard-avoid terms leaked in."""
    findings: List[Dict[str, str]] = []

    def flag(severity: str, code: str, message: str) -> None:
        findings.append({"severity": severity, "code": code, "message": message})

    # 1. Attention geometry — genuinely 70%+ empty, not just "less full."
    pct = spec.get("negative_space_pct")
    if pct is None:
        flag("fail", "missing_negative_space_pct", "no negative_space_pct declared")
    elif pct < 70:
        flag("fail", "insufficient_negative_space",
             f"negative_space_pct={pct} — zine default is 70-90%; below 70 is a normal "
             "poster wearing a minimal poster's label")
    elif pct < 75:
        flag("warn", "borderline_negative_space",
             f"negative_space_pct={pct} is at the low edge of the 70-90% zine default")

    # 2. Anchor — single subject. Heuristic, not proof: flags a likely second
    # competing subject for a human to confirm, doesn't hard-fail on it.
    anchor = (spec.get("anchor") or "").strip()
    if not anchor:
        flag("fail", "missing_anchor", "no anchor declared")
    elif " and " in anchor.lower() or anchor.count(",") >= 2:
        flag("warn", "possible_multiple_subjects",
             f"anchor='{anchor}' reads like it names more than one subject — "
             "confirm this is one scene, not two competing for attention")

    # 3. Color — exactly one saturated anchor color.
    colors = spec.get("colors") or []
    anchor_colors = [c for c in colors if c.get("role") == "anchor"]
    if len(anchor_colors) == 0:
        flag("fail", "no_anchor_color", "no color with role='anchor' declared")
    elif len(anchor_colors) > 1:
        flag("fail", "multiple_saturated_colors",
             f"{len(anchor_colors)} anchor colors declared "
             f"({', '.join(c.get('name', '?') for c in anchor_colors)}) — "
             "never two saturated colors fighting for attention")
    for c in anchor_colors:
        if not (c.get("source") or "").strip():
            flag("warn", "anchor_color_not_grounded",
                 f"anchor color '{c.get('name', '?')}' has no source — should tie back "
                 "to something real about the subject, not be an arbitrary pretty color")

    # 4. Texture — exactly one, present.
    if not (spec.get("texture") or "").strip():
        flag("fail", "missing_texture", "no texture declared")

    # 5. Typography — a title, not a paragraph.
    typography = spec.get("typography") or ""
    if not typography.strip():
        flag("fail", "missing_typography", "no typography declared")
    elif len(typography) > 200:
        flag("warn", "typography_too_verbose",
             "typography field reads like a paragraph description, not 'a title and "
             "maybe one line' — a zine poster's type occupies very little of the frame")

    # 6. Temperature — editorial register, not commercial/dramatic.
    temperature = (spec.get("temperature") or "").strip().lower()
    if not temperature:
        flag("fail", "missing_temperature", "no temperature declared")
    elif temperature not in _ALLOWED_TEMPERATURES:
        flag("warn", "unrecognized_temperature",
             f"temperature='{temperature}' isn't one of {sorted(_ALLOWED_TEMPERATURES)} — "
             "confirm it's still a quiet/editorial register, not a commercial one")

    # 7. Hard avoids — must be stated, and must not appear inside the fields
    # meant to avoid them (the actual failure mode: a spec that lists an
    # avoid and then does it anyway in the anchor/treatment/color fields).
    avoids = spec.get("avoids") or []
    if not avoids:
        flag("warn", "no_avoids_stated", "no hard avoids listed for this brief")

    haystack_fields = {
        "anchor": anchor,
        "anchor_treatment": spec.get("anchor_treatment") or "",
        "typography": typography,
        "texture": spec.get("texture") or "",
        "temperature": spec.get("temperature") or "",
        "canvas": spec.get("canvas") or "",
    }
    for field_name, text in haystack_fields.items():
        low = text.lower()
        for term in FORBIDDEN_TERMS:
            if term in low:
                flag("fail", "forbidden_term_leak",
                     f"'{term}' found inside '{field_name}' — this is on the skill's own "
                     "Negative Constraints list, it should not appear in the compiled prompt")

    # 8. Genericness — would this same prompt paste onto a different subject?
    # Operationalized as: does the brief's own subject vocabulary actually
    # show up in the fields that are supposed to be specific to it?
    keywords = [k.lower() for k in (spec.get("subject_keywords") or [])]
    if not keywords:
        flag("warn", "no_subject_keywords",
             "no subject_keywords declared — genericness check skipped, cannot confirm "
             "this compiled prompt is tied to this specific brief")
    else:
        anchor_hit = any(k in anchor.lower() for k in keywords)
        color_sources = " ".join((c.get("source") or "") for c in anchor_colors).lower()
        color_hit = any(k in color_sources for k in keywords)
        if not anchor_hit:
            flag("fail", "generic_anchor",
                 "anchor field contains none of subject_keywords — reads like it would "
                 "paste unchanged onto a different subject")
        if anchor_colors and not color_hit:
            flag("warn", "generic_anchor_color",
                 "anchor color's source contains none of subject_keywords — the "
                 "'tied to something real about the subject' rule is unmet")

    severities = {f["severity"] for f in findings}
    verdict = "FAIL" if "fail" in severities else ("WARN" if "warn" in severities else "PASS")

    result: Dict[str, Any] = {"verdict": verdict, "findings": findings}
    if spec.get("anchor_is_photo"):
        result["strength_recommendation"] = recommend_strength(spec.get("anchor_treatment", ""))
    return result


# ───────────────────────────── demo ──────────────────────────────────────────

def _bad_spec_commercial_travel_poster() -> Dict[str, Any]:
    """What actually got sent to an image tool for a London sunset skyline
    photo before this gate existed: a full-bleed commercial travel-poster
    prompt, two saturated colors fighting (burnt orange sky + deep blue sky),
    no real negative-space discipline, and language straight off this
    skill's own Negative Constraints list."""
    return {
        "subject": "London skyline sunset photo",
        "subject_keywords": ["london", "shard", "skyline", "city of london"],
        "canvas": "full-bleed poster",
        "negative_space_pct": 15,
        "anchor": "silhouetted skyline with the shard and a cluster of skyscrapers and lit foreground buildings",
        "anchor_is_photo": True,
        "anchor_treatment": "dramatic cinematic lighting, full color, glossy commercial travel-poster look",
        "typography": "bold minimalist poster typography with a headline and a subheadline across the bottom third",
        "colors": [
            {"role": "anchor", "name": "burnt orange", "hex": "#C1502E", "source": ""},
            {"role": "anchor", "name": "deep blue", "hex": "#1B3A5C", "source": ""},
        ],
        "texture": "none",
        "temperature": "dramatic",
        "avoids": [],
    }


def _good_spec_minimal_editorial() -> Dict[str, Any]:
    """Corrected compile for the same photo, run through the nine
    first-principles fields properly."""
    return {
        "subject": "London skyline sunset photo",
        "subject_keywords": ["london", "shard", "skyline", "city of london"],
        "canvas": "2:3 tall poster, aged matte paper ground",
        "negative_space_pct": 82,
        "anchor_position": "lower-third float, thin skyline band",
        "anchor": "silhouetted City of London skyline with the Shard",
        "anchor_is_photo": True,
        "anchor_treatment": "duotone, simplified background, subject stays recognizable",
        "typography": "typewriter face, single word, under 5% of frame",
        "colors": [
            {"role": "anchor", "name": "burnt orange", "hex": "#C1502E",
             "source": "the real sunset gradient behind the Shard in the source photo"},
            {"role": "ground", "name": "charcoal", "hex": "#1B1B1E", "source": ""},
        ],
        "texture": "scanner noise, subtle",
        "temperature": "quiet",
        "avoids": ["cinematic lighting", "commercial travel-poster headline layout",
                    "multiple competing subjects"],
    }


def demo() -> int:
    print("=" * 72)
    print("DEMO — same London skyline photo, two compiled specs")
    print("=" * 72)

    bad = _bad_spec_commercial_travel_poster()
    bad_result = audit_poster_spec(bad)
    print("\n[commercial travel-poster prompt — what actually got sent to an image tool]")
    print(compile_prompt(bad))
    print(f"\nverdict={bad_result['verdict']}  "
          f"findings={[f['code'] for f in bad_result['findings']]}")

    good = _good_spec_minimal_editorial()
    good_result = audit_poster_spec(good)
    print("\n" + "-" * 72)
    print("[corrected minimal-editorial compile]")
    print(compile_prompt(good))
    print(f"\nverdict={good_result['verdict']}  "
          f"findings={[f['code'] for f in good_result['findings']]}")
    if "strength_recommendation" in good_result:
        lo, hi = good_result["strength_recommendation"]["range"]
        print(f"recommended edit strength: {lo}-{hi} "
              f"({good_result['strength_recommendation']['rationale']})")

    ok = (
        bad_result["verdict"] == "FAIL"
        and good_result["verdict"] in ("PASS", "WARN")
        and any(f["code"] == "multiple_saturated_colors" for f in bad_result["findings"])
        and any(f["code"] == "forbidden_term_leak" for f in bad_result["findings"])
        and any(f["code"] == "insufficient_negative_space" for f in bad_result["findings"])
    )
    print()
    print("=" * 72)
    print("demo OK — same source photo, the gate separates the commercial-poster "
          "prompt from the minimal-editorial compile correctly" if ok
          else "demo UNEXPECTED — check implementation")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compile + audit a minimal-editorial-poster spec against SKILL.md's Quality Gate")
    ap.add_argument("--spec", help="JSON file with the nine compiled fields (see SKILL.md Output Format)")
    ap.add_argument("--json", help="write machine-readable result here instead of stdout")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        return demo()

    if not args.spec:
        ap.error("--demo, or --spec <spec.json>, is required")
        return 2

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    result = audit_poster_spec(spec)
    result["compiled_prompt"] = compile_prompt(spec)

    out = json.dumps(result, indent=2, default=str)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)

    return 0 if result["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
