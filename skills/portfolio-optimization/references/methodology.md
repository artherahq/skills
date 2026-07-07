# Portfolio optimization — methods & interpretation

## Why no expected returns

Mean-variance optimization is famously an "error maximizer": weight
sensitivity to the mean estimate is an order of magnitude higher than to the
covariance estimate, and sample means over any practical window carry standard
errors comparable to the means themselves. Every method in the harness is
mean-free by design:

| Method | Needs | Bet |
|---|---|---|
| equal | nothing | ignorance is a position; hard benchmark |
| invvol | variances | risk scales inversely with size |
| minvar | full covariance | low-vol corner is exploitable |
| erc | full covariance | every asset contributes equal risk |
| hrp | correlation structure | clusters should share, not multiply, budget |

## Implementation notes

- **Shrinkage**: sample covariance blended toward `tr(Σ)/n · I` with intensity
  `min(1, 0.5·N/T)` — a Ledoit–Wolf-flavored heuristic; intensity is disclosed
  whenever > 0.05.
- **minvar**: projected gradient descent on the simplex (long-only). In-sample
  portfolio variance is never above equal weight's by construction.
- **erc**: multiplicative cyclical updates until risk contributions equalize
  (spread < 2% in tests).
- **hrp**: single-linkage clustering on √((1−ρ)/2) distance, quasi-diagonal
  leaf order, recursive bisection with inverse-variance split. No matrix
  inversion anywhere — stable when Σ is ill-conditioned.
- **Cap**: iterative clip-and-redistribute, long-only.

## Reading the walk-forward table

Fit 252, hold 21 (defaults). OOS vol ordering is usually minvar ≤ hrp ≤ erc ≤
invvol ≤ equal; OOS **Sharpe** ordering is the honest question — when equal
weight wins, `optimizer_no_edge` fires. That finding is robust in the
literature (DeMiguel et al., "1/N") and should be delivered as a result, not
hidden as an inconvenience.

## Known limits

- Static weights within each hold block; no intra-block drift handling.
- Long-only. Shorting changes the projection and the risk story.
- Walk-forward table ignores transaction costs — chain the chosen method's
  weight path into backtest-validation's cost ladder for the net answer.
- Covariance stationarity is assumed within the fit window; regime shifts
  inside the window blur the structure (engine-level DCC/HMM work).
