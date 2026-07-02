# Completion Gates

Use these gates for a comprehensive single-equity report.

## Required Manifest Shape

```json
{
  "report": {"symbol": "603212.SH", "as_of": "2026-07-01T08:00:00Z", "status": "complete"},
  "metrics": {"price": 45.0, "currency": "CNY", "volume": 2000000, "market_cap": 20000000000},
  "agents": [{"agent": "technical", "success": true, "degraded": false, "analysis": "..."}],
  "evidence": [{"kind": "market_data", "source": "provider", "as_of": "2026-07-01T08:00:00Z", "verified": true}],
  "sections": ["executive_summary", "fundamentals", "valuation", "technical", "risk", "scenarios", "sources"]
}
```

## Complete

- Reference price is positive; volume is non-negative; market-cap and implied-share scales are plausible.
- At least 60% of requested specialists produce non-empty usable analysis.
- At least two of `technical`, `fundamental`, and `risk` are usable when requested.
- Verified evidence includes `market_data`, `filing`, and `risk`.
- All required report sections are present.
- Data status is not stale, partial, unavailable, or failed.
- No blocking validation failure remains.

## Partial

Use `partial` when the report remains useful but one or more non-blocking gates fail, such as a missing filing, stale inputs, insufficient specialist coverage, degraded-agent majority, implausible market-cap scale, or missing report sections. State exactly what is absent and do not silently infer it.

## Blocked

Use `blocked` when the instrument is unresolved, the reference price is unavailable or invalid, volume is negative, all specialists fail, or market data is unavailable. Do not issue a confident signal, target, stop, or complete-report claim.

## Provenance Rules

- Use primary filings and issuer or regulator sources for company facts where possible.
- Store source, as-of timestamp, unit, and content hash when available.
- Mark LLM-authored interpretation separately from deterministic calculations.
- A deterministic fallback is usable but `degraded`; include its limitation and cap confidence at 45%.
- Preserve failed checks in the final manifest and report metadata.
