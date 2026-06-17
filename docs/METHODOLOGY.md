# Methodology

- Version: 0.3.2
- Selected-policy final-checkpoint traces: seven
- Seeds per benchmark: five
- Split: 25% reserved calibration / 75% deployment in each seed-task-class group
- Split seed: 20260616
- Nonconformity: `1 - p_true`
- Target marginal coverage: 0.9
- Finite-sample quantile: `k = min(n, ceil((n+1)*(1-alpha)))`
- Primary gate: singleton prediction set

The split is independent of scores, predictions, correctness, and context confidence. Aggregate marginal coverage is reported together with worst seed-task coverage, normalized set size, context accuracy, and ACTION rate.
