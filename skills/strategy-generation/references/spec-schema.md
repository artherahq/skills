# Strategy spec contract

Every field below is required unless marked optional. The validator
(`scripts/validate_strategy_spec.py`) enforces this mechanically.

| Field | Type | Notes |
|---|---|---|
| `strategy_name` | str | descriptive; no performance claims in the name |
| `archetype` | str | one of: momentum, mean_reversion, multi_factor, pairs_trading, technical, ml_enhanced, event_driven, value |
| `market` | str | US / CN / HK / CRYPTO / … |
| `universe` | list or str | explicit symbols, or a reproducible selection rule |
| `signal.entry_logic` | str | testable sentence — a reviewer must be able to say "false" |
| `signal.exit_logic` | str | same; empty exits fail |
| `signal.parameters` | dict | every free number, named. Hidden prose numbers are a gate violation |
| `risk_control` | dict | ≥1 of `stop_loss_pct`, `max_position_weight`, `max_gross_exposure`, `max_drawdown_halt_pct` |
| `position_sizing` | dict/str | method; "all-in" has no hard control and fails |
| `costs_bps` | number > 0 | per unit of turnover; gross-only specs are refused |
| `data_requirements.history_periods` | int | drives the overfit preflight |
| `data_requirements.fields` | list | e.g. adj_close, volume |
| `data_requirements.pit_reviewed` | bool | false → WARN with a plan to run point-in-time-research |
| `variants_tried` | int ≥ 1 | the honesty ledger; feeds backtest-validation `--trials` |
| `backtest_config` | dict | freq, split, benchmark (optional) |
| `status` | str | `spec_only` → `implemented` → `backtested` → `paper`; never `live` from this skill |

## Overfit preflight

`observations ≈ history_periods × max(1, |universe|)`, divided by the count of
numeric values in `signal.parameters`:

- < 10 obs/param → FAIL (`overfit_preflight`) — curve-fitting by construction
- < 30 obs/param → WARN (`thin_data_budget`)

This is a *preflight*, not a proof: passing it earns the right to be judged by
backtest-validation, nothing more.

## Archetype quick reference

| Archetype | Core bet | Typical failure |
|---|---|---|
| momentum | winners persist | crash reversals; crowding |
| mean_reversion | spreads close | trends that don't revert; regime break |
| multi_factor | diversified premia | factor crowding; correlation of premia |
| pairs_trading | relative value | cointegration decay |
| technical | pattern persistence | parameter proliferation (watch the preflight) |
| ml_enhanced | learnable structure | leakage (PIT!), unstable features |
| event_driven | post-event drift | event definition drift; sparse samples |
| value | price ≠ worth | value traps; long droughts |
