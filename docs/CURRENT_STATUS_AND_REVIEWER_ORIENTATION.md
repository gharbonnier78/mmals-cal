# From the Initial Gap Analysis to MMALS-CAL v0.3.2

This document gives reviewers a compact map of what the original MMALS-CAL gap analysis identified, what v0.3.2 now implements, and what remains outside the offline replay scope.

## Status transition

| Component | Before MMALS-CAL | Implemented in v0.3.2 | Remaining work |
|---|---|---|---|
| A. Regime-change detection | RC2O and Geometry-MMALS inferred context and route, but did not formally detect temporal distribution changes. | Still absent online; offline traces provide regime identifiers and exported context. | Label-free warning, delayed-label confirmation, CUSUM/BOCPD, delay and false-alarm control, persistent regime state. |
| B. No-leakage calibration buffer | No conformal separation between detection, calibration, and deployment use. | Deterministic 25/75 reserved-calibration/deployment split independent of scores and predictions. | Irreversible streaming assignment and separate temporal detection/calibration/validation/deployment windows. |
| C. Regime-aware conformal quantile | Scores existed, but no measured set-coverage guarantee was attached to them. | Five offline strategies: global, stale T0, fresh oracle, inferred bucket, and context-selected oracle. | Online adaptation, delayed labels, uncertain boundaries, small buffers, and local-window coverage. |
| D. ACTION/NO-DECISION gate | Conceptual through TPUT, forward-backward control, and STRAT-Q. | Executable singleton gate used as a conservative comparison baseline. | Full cost-aware gate combining regime confidence, calibration freshness, measured coverage, latency, abstention cost, and escalation. |
| Evidence and claim audit | Many metrics existed, but calibration-specific protocol and claim checks were incomplete. | Metric, Protocol, and Claim Verification are integrated. | Runtime event linkage, online evidence ledger, standardized signal contract. |

## Main distinction

Context inference and regime-change detection are not the same operation.

- RC2O asks which known context best explains one observation.
- A change detector asks whether the process generating the stream has changed enough to invalidate the current confidence rule.

## Two-channel online design

The current nonconformity score, `s(x,y) = 1 - p(y|x)`, requires the true label. A future online system therefore needs:

1. label-free early warning from entropy, confidence, context, route, host, latent, and memory-drift signals;
2. delayed-label confirmation from true nonconformity, empirical miscoverage, error, and quantile drift.

## Layer responsibilities

- MMALS / RC2O: learn, infer context, select routes and hosts, export evidence.
- Geometry-MMALS: measure proximity to known regimes.
- MMALS-CAL offline: audit calibration, coverage, compactness, and actionability.
- MMALS-CAL online: detect staleness, buffer, recalibrate, validate, close and reopen the gate.
- TPUT / STRAT-Q: model the costs of action, abstention, delay, retraining, and escalation.
- Verification Stack: verify that the scientific artifacts and claims match execution.

## Remaining transition

The next problem is:

`detect change -> measure proximity -> reuse/recombine/create -> recalibrate and reopen without leakage`

This is the bridge between MMALS-CAL, Geometry-MMALS, and TPUT.
