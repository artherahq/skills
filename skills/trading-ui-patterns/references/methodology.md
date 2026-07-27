# Methodology — how the audit works, and what it deliberately doesn't judge

## Division of labor

- **Taste calls** — which of these three products' *feel* fits the user's
  app, exact spacing rhythm, motion/haptics character, whether to lean X's
  density or Trading212's simplicity for a given screen — are conversation,
  informed by `references/x_patterns.md`, `references/tradingview_patterns.md`,
  `references/trading212_patterns.md`. This skill has an opinion about what
  each product's pattern *is*; it has no opinion about which pattern the user
  should pick for a given screen.
- **Machine checks** — does the component the user built actually contain the
  structural elements its claimed pattern requires, and does one specific
  field (direction color today; more can be added) match the *market* the
  component is rendering, not the market it was originally built against.
  That's what `scripts/pattern_audit.py` enforces, driven entirely by
  `references/patterns.json` — no hardcoded pattern logic in the script
  itself, so adding a seventh pattern is a JSON edit, not a code change.

## Why a "market-aware field" check exists at all

Direction color is the one field in this catalog that is not a fixed
constant — it's a function of which market's convention the data represents:

| Market | Up | Down |
|---|---|---|
| US, UK, HK, most of the world | green | red |
| Mainland China, Taiwan | red | green |

A component built and visually verified against US test data, then pointed
at a CN feed without re-deriving the color mapping, produces a plausible,
fully-rendered watchlist row that is simply backwards for every user on that
feed. Nothing throws, nothing looks broken in a screenshot taken by someone
who doesn't already know the correct CN convention — this is the same shape
of bug as a sign-convention flip in a quant computation (see the
`gamma-exposure` skill), just expressed as a color instead of a number.

`patterns.json`'s `market_aware_fields` block is how a pattern declares that
one of its fields has this property: a map from market code to expected
value, plus a `"default"` for when the manifest doesn't declare a market.
`audit_manifest()` only raises `market_convention_mismatch` when the manifest
supplies both the field and the market — it will never guess a market for
you, and it never fails a manifest for a market-aware field it wasn't told
about (that's a `missing_required_field` instead, a different finding).

## Manifest shape

A component manifest is the thing you hand the auditor — not a screenshot,
not source code, a small JSON describing what the component actually has:

```json
{
  "pattern": "tradingview_watchlist_row",
  "market": "CN",
  "fields": {
    "symbol": true,
    "price": true,
    "change_value": true,
    "change_percent": true,
    "direction_color": "red_up_green_down",
    "sparkline": false,
    "tap_target_pt": 48
  }
}
```

`fields` values are whatever the pattern's checklist needs to reason about:
booleans for "is this element present", strings for enums like
`direction_color`, numbers for anything a `rules` entry constrains (tap
target size, minimum data points behind a gauge, etc). Building this
manifest by hand from a component you already wrote is itself a useful
exercise — if you can't easily answer "does this have `estimated_total`",
the component's structure is probably not as clear as you think it is.

## Extending the catalog

Add a new pattern by editing `references/patterns.json`, not the script:

1. Pick a `product` (`X`, `TradingView`, `Trading212`, or a new one) and an
   id (`snake_case`, product-prefixed: `tradingview_order_book_ladder`).
2. `required_fields` — the structural elements that must exist for the
   component to read as this pattern at all. Keep this list to what's
   actually load-bearing for the pattern's identity, not everything nice to
   have.
3. `recommended_fields` — present in the reference product, absent doesn't
   break the pattern's identity, but the component reads thinner without it.
4. `forbidden_fields` — booleans the manifest can set to `true` to declare a
   known-bad condition is present (e.g. `single_color_for_both_directions`).
   These are opt-in flags the manifest author sets when they know the
   condition applies — the audit can't detect them from field presence alone.
5. `rules` — numeric (`min`) or exact-match (`equals`) constraints on a field
   the manifest declares. Only enforced when that field is present in the
   manifest, so patterns can add device-dependent rules (tap target size)
   without forcing every manifest to declare them.
6. `market_aware_fields` — only for fields whose *correct* value is a
   function of market, with a `"default"` plus any market overrides that
   differ from it.

Then extend `references/<product>_patterns.md` with the prose description of
what the pattern looks/feels like in the real product — the audit only
checks structure, so the "does this feel right" knowledge has to live in the
prose an agent reads before building the component, not in the JSON.
