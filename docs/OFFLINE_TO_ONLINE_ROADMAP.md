# Offline-to-Online Roadmap

Version 0.3.2 validates the offline replay chain:

```text
reserved calibration -> conformal quantile -> prediction set -> ACTION/NO_DECISION -> evidence and claim audit
```

The online target is:

```text
detect -> close/restrict gate -> reserve uncontaminated calibration data -> recalibrate -> validate -> reopen
```

## Planned v0.4 state machine

- `STABLE`
- `SUSPECTED_SHIFT`
- `QUARANTINE`
- `CALIBRATING`
- `VALIDATING`
- `READY`
- `DEGRADED`

## Required comparisons

- no detector and fixed calibrator;
- periodic recalibration;
- oracle change point;
- label-free CUSUM;
- delayed-label CUSUM on nonconformity;
- BOCPD;
- adaptive and strongly adaptive conformal baselines.

## Required metrics

False alarms, missed changes, detection delay, coverage during delay, time to restored coverage, contamination rate, ACTION during transition, wrong-action rate, NO_DECISION cost, memory cost, label delay, and cross-seed stability.
