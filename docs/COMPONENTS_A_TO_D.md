# The Four MMALS-CAL Components: A-D

This document explains the four components in accessible English and states their implementation status in v0.3.2.

## A. Regime Detection (CUSUM / BOCPD)

### What is a regime?

A regime is a period during which the observations received by the system come from a sufficiently stable distribution for the same decision and confidence rules to remain valid. A regime change occurs when that distribution changes materially: new classes, a different visual domain, a new user population, a new sensor, or new acquisition conditions.

### Why must it be detected automatically?

A deployed system does not have an oracle announcing that the regime has changed. It must monitor the observation stream and decide, often before ground-truth labels are available, whether the previous evidence remains applicable.

### CUSUM - Cumulative Sum

CUSUM (Page, 1954) is a sequential change-detection method. At each time step, a monitoring score measures how far the current observation departs from the expected behavior of the active regime. CUSUM accumulates persistent departures. Under stability, positive and negative deviations tend to compensate and the statistic remains small. After a sustained change, deviations accumulate in the same direction and cross an alarm threshold.

CUSUM is simple, interpretable, and suitable for real-time systems. Its threshold controls the trade-off between fast detection and false alarms.

### BOCPD - Bayesian Online Changepoint Detection

BOCPD (Adams and MacKay, 2007) maintains a probability distribution over the *run length*: the time elapsed since the most recent change point. Instead of only issuing a binary alarm, it quantifies uncertainty about when the change occurred. BOCPD is usually more computationally demanding than CUSUM but more informative.

### Status in v0.3.2

Automatic online change detection is **not implemented**. Regime and exported `context_top` values are read from final-checkpoint experimental traces. CUSUM and BOCPD are the first planned online extension.

A further distinction is necessary for deployment:

- label-free early warning can monitor confidence, entropy, route instability, context uncertainty, or representation drift;
- delayed-label confirmation can monitor the true-label nonconformity score `1 - p(y|x)` and empirical coverage.

The latter cannot be used immediately when the true label is unavailable.

## B. No-Leakage Calibration Buffer

### What is leakage here?

Leakage occurs when observations used to construct a calibration rule have also influenced change detection, threshold selection, model choice, or the deployment result being reported. Reusing the same observations can make the evidence look better than it will be on genuinely unseen data.

### Three irreversible roles

A complete online design should assign each observation to exactly one role:

1. **Detection:** observations used only to detect or confirm a regime change.
2. **Reserved calibration:** observations arriving after the declared change and used only to estimate the new conformal quantile.
3. **Deployment:** observations on which the newly calibrated rule is evaluated or used.

An observation must not move retrospectively from one role to another.

### Status in v0.3.2

The principle is implemented **offline**. Every `seed x task x true_class` group is split deterministically into 25% reserved calibration and 75% deployment. Assignment is independent of probabilities, predictions, correctness, and context confidence. The online streaming buffer, in which roles are assigned as data arrive, remains future work.

## C. Regime-Aware Conformal Quantile

### What is conformal prediction?

Conformal prediction converts model scores into prediction sets with measurable marginal coverage. Instead of always returning one class, the system returns a set of candidate classes. At a 90% target, the intended statement is that the true class belongs to the set in at least approximately 90% of exchangeable future cases.

### Nonconformity score

MMALS-CAL uses

```text
s(x, y) = 1 - p(y | x)
```

A small score means that the model assigned high probability to the true class. A large score means that the true answer was surprising to the model.

### Why one quantile per regime?

A global quantile can be acceptable on average while being too optimistic for a difficult regime and unnecessarily conservative for an easy one. Regime-aware calibration estimates a distinct quantile from the reserved calibration observations associated with each regime or inferred-context bucket.

### Five strategies in v0.3.2

1. one global calibrator per seed;
2. the T0 quantile reused as stale evidence;
3. fresh calibration under the oracle task/regime;
4. calibration within exported inferred-context buckets;
5. oracle regime quantiles selected by exported inferred context.

The fifth strategy isolates the cost of recalling a valid calibrator under the wrong regime.

## D. ACTION / NO-DECISION Gate

### General principle

The gate decides whether the conformal set is precise enough for automatic action or whether the system should abstain. Abstention is not a prediction failure; it is an explicit statement that the current evidence is insufficient for the requested decision.

### Singleton rule in v0.3.2

The research rule is:

```text
ACTION      if the prediction set contains exactly one class
NO_DECISION otherwise
```

This is a conservative baseline for autonomous single-label actionability. It is not a universal deployment policy and not a formal lower bound unless a family of admissible deployment policies is explicitly defined. Cost-sensitive systems may act on larger sets, request more evidence, or escalate to a human operator.

### Three conditions for a complete gate

A mature deployment gate should require all three:

1. **Sufficient regime confidence:** the active regime is recognized with acceptable confidence.
2. **Fresh calibration:** the quantile was estimated from recent observations belonging to the active regime.
3. **Coverage health:** recent monitored coverage remains compatible with the declared target.

When one condition fails, the system should close or restrict the gate, trigger recalibration, request evidence, or escalate.

### Cost of abstention

NO_DECISION has an operational cost: human review, latency, extra acquisition, or service denial. TPUT or STRAT-Q should model wrong-action cost, abstention cost, evidence-acquisition cost, and long-term system objectives without hiding the explicit conformal constraint.

### Status in v0.3.2

The singleton rule is executable and measured across all seven benchmarks. The complete three-condition runtime gate remains conceptual and belongs to the online roadmap.
