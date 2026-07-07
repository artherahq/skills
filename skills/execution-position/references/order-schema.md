# Pre-trade spec schema

One JSON object with four blocks. The gate applies conservative defaults where
marked, and refuses (rather than guesses) where honesty requires an input.

```jsonc
{
  "order": {
    "symbol": "AAPL",
    "side": "buy",                 // buy | sell
    "price": 230.0,
    "stop_price": 216.0,           // optional; absent → no_stop warning
    "execution": "paper",          // "live" fails the gate mechanically
    "sizing": {
      "method": "vol_target",      // vol_target | kelly | fixed_weight
      "risk_budget_pct": 0.02,     // vol_target: share of equity at risk (ann.)
      "win_rate": 0.55,            // kelly: DECLARED edge, required
      "payoff_ratio": 1.8,         // kelly: DECLARED edge, required
      "fraction": 0.25,            // kelly: hard-capped at 0.25
      "weight": 0.10               // fixed_weight
    }
  },
  "portfolio": {
    "equity": 100000,
    "cash": 40000,
    "positions": {"MSFT": 0.20}    // symbol → current weight
  },
  "limits": {
    "max_position_weight": 0.20,   // default 0.20
    "max_gross_exposure": 1.0,     // default 1.0
    "min_cash_pct": 0.05           // default 0
  },
  "market": {
    "ann_vol": 0.28,               // or pass --history CSV(date,close)
    "adv_shares": 50000000,        // absent → liquidity check skipped, disclosed
    "spread_bps": 2,               // default 5
    "commission_bps": 5            // default 5
  }
}
```

## Gate outcomes

| Flag | Severity | Meaning |
|---|---|---|
| `live_execution_refused` | fail | live orders are outside this skill's authority |
| `no_volatility` | fail | vol_target without a vol estimate — refuse, don't guess |
| `kelly_without_declared_edge` | fail | Kelly needs the user's explicit claim |
| `negative_edge` | fail | declared edge ≤ 0 → position is zero |
| `position_limit` / `gross_exposure_limit` | fail | hard caps |
| `insufficient_cash` | fail | respects the cash floor |
| `liquidity_limit` | fail | order > 10% of ADV |
| `kelly_fraction_capped` | warn | requested fraction reduced to 0.25 |
| `position_capped` | warn | sized weight clipped to the per-name cap |
| `noise_stop` | warn | stop inside one daily sigma triggers on noise |
| `no_stop` | warn | exit discipline undefined |
| `liquidity_notable` | warn | 2–10% of ADV |

## Cost model (labeled estimate)

`total_bps ≈ commission + half-spread + 2 bps per 1% of ADV` — linear impact
placeholder. Real impact is convex in size and regime-dependent; treat the
figure as a floor for planning, and let backtest-validation's cost ladder
judge the strategy-level consequence.
