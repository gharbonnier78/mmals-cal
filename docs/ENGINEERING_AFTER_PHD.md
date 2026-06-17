# Engineering After the PhD

A production MMALS-CAL service should remain a fail-closed evidence shell around the learning system rather than becoming another opaque learned controller.

## Minimal services

1. prediction adapter and probability metadata;
2. context and route evidence service;
3. label-free shift monitor;
4. delayed-label confirmation monitor;
5. immutable calibration registry containing regime, age, hash, sample count, quantile, and observed coverage;
6. conformal set builder;
7. cost-aware gate;
8. evidence ledger connected to Metric, Protocol, and Claim Verification.

## Operational rule

Do not reopen an autonomous gate merely because a change detector fired and a new quantile was computed. Reopening should require an independent validation window and a recorded coverage-health decision.

## Relationship with TPUT / STRAT-Q

TPUT or STRAT-Q can optimize wrong-action, abstention, latency, evidence-acquisition, and long-term retention costs. The conformal constraint should remain visible and auditable rather than being absorbed into one opaque utility score.
