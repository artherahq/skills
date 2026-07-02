---
name: equity-research-report
description: >-
  Produce comprehensive, evidence-backed public-equity research reports with
  market, filing, fundamental, valuation, technical, risk, catalyst, scenario,
  and source analysis. Use when the user asks for "全面分析报告", "股票研报",
  "深度分析公司", "完整个股分析", "comprehensive equity report", or requests
  analysis of a stock, company, or equity thesis with current auditable data.
---

# Equity Research Report

Build a report through an explicit research workflow. Treat an attractive narrative as insufficient unless the evidence and completion gates pass.

## Workflow

1. Resolve the instrument, exchange, currency, locale, and report `as_of` timestamp. Stop if the identity is ambiguous.
2. Publish a concise execution plan containing data collection, specialist analyses, synthesis, critique, and validation. Do not expose private chain-of-thought.
3. Collect one normalized market-data bundle first. Reuse it across specialists instead of fetching the same quote independently.
4. Collect point-in-time evidence for market data, financial statements or filings, valuation inputs, risk history, and current catalysts. Record source, timestamp, and limitations for every item.
5. Run independent technical, fundamental, valuation, risk, and catalyst analyses. Use deterministic calculations for indicators, multiples, returns, volatility, drawdown, and scenarios.
6. Retry only missing or failed evidence, at most twice per gap. Fall back to deterministic analysis when an LLM fails but verified inputs remain available. Mark fallback output `degraded` and cap its confidence.
7. Run a critic pass. Check unit scale, stale data, contradictory prices, unsupported targets, missing filings, circular citations, and conclusions that exceed the evidence.
8. Build the report and its machine-readable manifest. Include the decision trace: plan, tools used, evidence IDs, checks, retries, degraded steps, and unresolved limitations.
9. Run `scripts/validate_equity_report.py MANIFEST.json`. Claim `complete` only when it exits successfully. Otherwise label the report `partial` or `blocked` and retain the failed checks.

Read [references/completion-gates.md](references/completion-gates.md) before validating or changing completion criteria.

## Tool Routing

- Prefer normalized market-data, filing, factor, risk, news, and web-search tools over model memory.
- In Aria Code, use the market-data service once, then pass its bundle to `/team` or specialist agents. Use the full team for comprehensive reports.
- Use web search for current filings, investor-relations releases, regulatory events, and other facts that can change. Cite the primary source.
- Never substitute an LLM estimate for unavailable market, filing, or risk evidence.

## Required Outputs

Create:

1. A human-readable report with executive summary, company and industry, fundamentals, valuation, technicals, risk, catalysts, scenarios, limitations, and sources.
2. A JSON manifest accepted by the validator. Preserve source timestamps, units, agent status, and evidence provenance.

Keep investment language conditional. Separate observed facts, calculated metrics, model estimates, and analyst judgment. Do not present the output as personalized investment advice.
