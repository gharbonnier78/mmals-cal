Below, **“abstract” means a concise paraphrase of the work’s contribution**, not a reproduction of the publisher’s official abstract.

## How the references fit together

| Role in MMALS-CAL | References | Status in v0.3.2 |
|---|---|---|
| Foundations of conformal prediction | Vovk et al.; Angelopoulos & Bates | Directly implemented |
| Coverage versus set compactness | Sadinle et al. | Direct conceptual support |
| Online adaptation under drift | Gibbs & Candès 2021/2022; Bhatnagar et al. | Roadmap, not yet implemented |
| Automatic regime-change detection | Page; Adams & MacKay | Roadmap component A |
| Fail-closed and constraint-oriented design | Thomas et al. | Architectural and verification philosophy |

---

# 1. Vovk, Gammerman, and Shafer, 2005  
## *Algorithmic Learning in a Random World*

### Paraphrased abstract

This foundational book develops conformal prediction as a way to attach statistically meaningful confidence information to machine-learning predictions. Instead of returning only a point prediction, a conformal predictor evaluates how unusual—or non-conforming—a candidate output is relative to previously observed examples. Under the classical randomness or exchangeability assumptions, the resulting prediction regions have controlled error rates without requiring the underlying predictive model to be probabilistically correct. The book connects these methods to algorithmic randomness, online prediction, confidence, and credibility. ([link.springer.com](https://link.springer.com/book/10.1007/b106715?utm_source=chatgpt.com))

### Engineer translation

You already have a classifier producing scores. Conformal prediction adds an external validation wrapper:

```text
model scores
    ↓
nonconformity score
    ↓
calibration quantile
    ↓
prediction set with a measurable error rate
```

The important engineering idea is that **the classifier does not need to estimate perfect probabilities**. The calibration layer looks at how the scores behaved on held-out data and converts them into a prediction set.

For MMALS-CAL, this is the origin of:

\[
s(x,y)=1-p(y\mid x)
\]

and:

\[
\Gamma(x)=\{y:s(x,y)\leq\widehat q\}.
\]

### What it brings to the MMALS-CAL paper

This is the principal theoretical foundation for:

- the use of nonconformity scores;
- conformal calibration quantiles;
- prediction sets rather than unconditional single-label answers;
- marginal error control under exchangeability;
- separating the predictor from the uncertainty-verification layer.

It supports the claim that MMALS-CAL is **model-agnostic**: it can wrap MMALS outputs without modifying the MMALS learner.

### Important limitation

The classical validity result depends on calibration and deployment observations being exchangeable. It does not automatically remain valid when the operating regime changes.

That limitation is exactly why MMALS-CAL studies:

- stale calibration;
- global versus regime-specific calibration;
- context-selected calibrators;
- future online change detection.

---

# 2. Angelopoulos and Bates, 2021  
## *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification*

### Paraphrased abstract

This tutorial presents conformal prediction as a practical framework for converting the outputs of arbitrary pretrained models into prediction sets or intervals with explicit finite-sample coverage guarantees. It emphasizes that the method requires very few assumptions about the model or data distribution, while still requiring an appropriate exchangeability relationship between calibration and future observations. The paper provides practical examples, implementation guidance, evaluation methods, and extensions to structured prediction, distribution shift, abstention, and risk control. ([arxiv.org](https://arxiv.org/abs/2107.07511?utm_source=chatgpt.com))

### Engineer translation

This paper is the practical manual for turning conformal prediction into software.

The recipe is:

1. train or obtain a predictive model;
2. freeze it;
3. reserve a calibration dataset;
4. calculate one nonconformity score per calibration observation;
5. take a finite-sample corrected quantile;
6. use this quantile to form sets on new observations;
7. evaluate both coverage and set size.

It says, in effect:

> Do not redesign your neural network merely to obtain uncertainty estimates. Add a statistically controlled layer around its outputs.

### What it brings to the MMALS-CAL paper

It directly supports the practical implementation choices in v0.3.2:

- black-box wrapping of existing MMALS traces;
- held-out calibration data;
- finite-sample quantile correction;
- 90% target coverage;
- reporting set size alongside coverage;
- abstention and prediction-set evaluation.

It is probably the best citation for readers who want to understand **how MMALS-CAL works operationally** without first reading the deeper theoretical literature.

### Important nuance

“Distribution-free” does not mean “valid under every possible deployment shift.”

It means that the method does not require a parametric distribution such as Gaussian noise. Classical validity still relies on exchangeability between calibration and deployment data.

---

# 3. Sadinle, Lei, and Wasserman, 2019  
## *Least Ambiguous Set-Valued Classifiers with Bounded Error Levels*

### Paraphrased abstract

The paper considers multiclass classifiers that return a set of plausible labels rather than a single label. It formulates the design problem as satisfying a user-specified coverage or error constraint while minimizing ambiguity, measured through the expected size of the returned label set. It derives optimal classifiers when the true class probabilities are known and proposes estimators with theoretical and finite-sample properties when those probabilities must be estimated. It also examines the possibility of empty prediction sets and practical ways to handle them. ([arxiv.org](https://arxiv.org/abs/1609.00451?utm_source=chatgpt.com))

### Engineer translation

Coverage alone is easy to achieve badly.

A system could always return:

```text
{every possible class}
```

and obtain almost perfect coverage.

That would be statistically correct but operationally useless.

Sadinle et al. formalize the real engineering objective:

```text
meet the error constraint
while
returning the smallest useful set
```

This produces two separate metrics:

- **validity:** is the true answer usually inside the set?
- **efficiency or ambiguity:** how many answers are inside the set?

### What it brings to the MMALS-CAL paper

This paper is the strongest support for the distinction between:

- **coverage**, and
- **compactness**.

It justifies why MMALS-CAL reports both:

\[
\Pr(Y\in\Gamma(X))
\]

and:

\[
\mathbb E[|\Gamma(X)|].
\]

It is directly relevant to the CORe50 result:

- approximately 90% coverage;
- average set size of about 28.7 labels out of 50;
- almost no singleton actions.

The reference helps us argue that **coverage without low ambiguity is not enough for actionability**.

### Important distinction

MMALS-CAL does not implement the exact optimization procedure proposed by Sadinle et al.

The paper supports our **compactness axis and engineering objective**, rather than serving as the exact algorithmic source of the LAC split-conformal method used in v0.3.2.

---

# 4. Gibbs and Candès, 2021  
## *Adaptive Conformal Inference Under Distribution Shift*

### Paraphrased abstract

The paper introduces adaptive conformal inference for online environments where the data-generating distribution changes over time. Instead of using one fixed calibration threshold indefinitely, the method continuously adjusts a parameter controlling prediction-set size according to recent coverage errors. The authors prove long-run coverage-frequency behavior without assuming a stationary or exchangeable sequence and demonstrate robustness under substantial real-world distribution shifts. ([proceedings.neurips.cc](https://proceedings.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html))

### Engineer translation

Classical split conformal works like a fixed configuration:

```text
calibrate once
→ obtain threshold
→ reuse threshold
```

Adaptive conformal inference adds a feedback loop:

```text
produce prediction set
→ later receive true label
→ check whether coverage failed
→ widen or narrow future sets
```

It behaves like a controller:

- too many misses → become more conservative;
- too much excess coverage → potentially tighten the sets.

### What it brings to the MMALS-CAL paper

This reference supports the transition from:

> offline evidence verification

to:

> online adaptive calibration.

It is central to the proposed v0.4 roadmap.

It shows that the stale-calibrator problem observed experimentally in MMALS-CAL is not merely descriptive. There is an existing theoretical family of methods designed to update coverage control during changing conditions.

### What it does **not** provide to v0.3.2

Adaptive conformal inference is not implemented in v0.3.2.

The current release:

- uses offline final-checkpoint traces;
- constructs fixed quantiles from reserved calibration subsets;
- compares fresh and stale quantiles;
- does not update quantiles sequentially.

Also, adaptive conformal inference is an adaptation mechanism, not necessarily a semantic detector that announces which named MMALS regime is active.

---

# 5. Gibbs and Candès, 2022  
## *Conformal Inference for Online Prediction with Arbitrary Distribution Shifts*

### Paraphrased abstract

This work extends adaptive conformal inference to respond more effectively to changing environments. It addresses the problem that excessive reliance on historical observations can make an online conformal method react too slowly. The proposed procedure dynamically tunes its adaptation rate and provides regret guarantees over local time intervals, allowing it to respond to distribution shifts of different sizes and speeds without prior knowledge of the shift dynamics. ([arxiv.org](https://arxiv.org/abs/2208.08401?utm_source=chatgpt.com))

### Engineer translation

The 2021 method needs an update speed:

- update too slowly → the system remains stale after a change;
- update too quickly → the threshold becomes noisy and unstable.

The 2022 method effectively manages several possible adaptation speeds and learns which one is useful.

Engineer analogy:

```text
slow controller  → stable but sluggish
fast controller  → reactive but noisy
adaptive controller → chooses speed from recent behavior
```

### What it brings to the MMALS-CAL paper

It supports two important observations from our experiments:

1. **Calibration age matters.**
2. **Not all changes occur at the same speed.**

PermutedMNIST resembles a relatively abrupt functional shift, while RotatedMNIST suggests a more ordered or gradual geometric variation. A fixed adaptation speed may not be appropriate for both.

This paper is therefore relevant to:

- calibration freshness;
- local-window evaluation;
- adaptive recalibration speed;
- the future comparison between fixed, periodic, and adaptive calibration.

### Important limitation

This reference does not mean that MMALS-CAL v0.3.2 is already robust to arbitrary shifts.

It defines a candidate future method that should be compared against:

- fixed calibration;
- periodic recalibration;
- CUSUM-triggered recalibration;
- oracle change points.

---

# 6. Bhatnagar, Wang, Xiong, and Bai, 2023  
## *Improved Online Conformal Prediction via Strongly Adaptive Online Learning*

### Paraphrased abstract

The authors study online prediction sets when distributions may change arbitrarily. They argue that performance measured over the entire history can hide failures during shorter local intervals. They introduce strongly adaptive online conformal methods that control regret simultaneously over intervals of different lengths and obtain approximately valid coverage. Their experiments show improved local coverage and smaller prediction sets under distribution shift compared with earlier methods. ([proceedings.mlr.press](https://proceedings.mlr.press/v202/bhatnagar23a.html))

### Engineer translation

Imagine a system that is correct over one year on average but fails badly for two weeks after every regime change.

A global annual metric may still look acceptable.

Strongly adaptive methods ask:

> Did the system perform correctly on every meaningful local interval?

The proposed architecture uses multiple online experts, each active over different temporal intervals. This allows the system to adapt to:

- short abrupt shifts;
- long stable periods;
- medium-duration changes;

without choosing one fixed monitoring window in advance.

### What it brings to the MMALS-CAL paper

This reference strongly supports one of our main findings:

> Aggregate coverage can conceal local undercoverage.

MMALS-CAL already reports:

- global coverage;
- seed-level coverage;
- task-level coverage;
- worst seed-task coverage.

Bhatnagar et al. provide a theoretical online continuation of that idea: validity and efficiency should also be monitored over **local time windows**, not only over the complete run.

This is highly relevant to future metrics such as:

- worst-window coverage;
- local coverage error;
- recovery time after drift;
- window-dependent action rate.

### Current versus future status

MMALS-CAL v0.3.2 already adopts the **evaluation philosophy** of local auditing, but it does not implement SAOCP or strongly adaptive online learning.

---

# 7. Adams and MacKay, 2007  
## *Bayesian Online Changepoint Detection*

### Paraphrased abstract

This paper presents an online Bayesian method for detecting abrupt changes in the generative mechanism of sequential observations. The method maintains a probability distribution over the current run length—the time elapsed since the most recent changepoint. New observations update the posterior probability of each possible run length, allowing the system to represent both the likely position of a change and uncertainty about that position. ([arxiv.org](https://arxiv.org/abs/0710.3742?utm_source=chatgpt.com))

### Engineer translation

Rather than returning only:

```text
change / no change
```

BOCPD returns something closer to:

```text
70% probability that the current regime began 3 samples ago
20% probability that it began 8 samples ago
10% probability that no recent change occurred
```

Its internal state is the posterior distribution:

\[
P(r_t\mid x_{1:t}),
\]

where \(r_t\) is the current run length.

### What it brings to the MMALS-CAL paper

It provides the probabilistic design option for component A:

> automatic regime-change detection.

BOCPD would allow future MMALS-CAL versions to:

- identify suspected regime transitions;
- quantify uncertainty about the transition;
- estimate how long the current regime has existed;
- decide whether enough post-change observations have accumulated for calibration;
- trigger quarantine and buffer creation.

### Important limitation

BOCPD requires an explicit probabilistic model for observations and a hazard model for changepoints.

It is not distribution-free in the conformal-prediction sense.

For MMALS-CAL, a design question remains:

> What signal should BOCPD observe?

Candidates include:

- prediction entropy;
- context entropy;
- route drift;
- embedding drift;
- delayed-label nonconformity;
- empirical miscoverage.

---

# 8. Page, 1954  
## *Continuous Inspection Schemes*

### Paraphrased abstract

Page studies sequential monitoring procedures designed to detect when an observed process has moved away from its expected operating condition. The central idea underlying CUSUM is to accumulate small deviations over time so that a persistent shift becomes detectable even when each individual observation is not sufficiently unusual to trigger an alarm. The method balances detection delay against false alarms through its reference value and alarm threshold. ([jstor.org](https://www.jstor.org/stable/2333009?utm_source=chatgpt.com))

### Engineer translation

A single strange observation may be noise.

Ten slightly strange observations in the same direction may indicate a real regime change.

CUSUM keeps a running statistic such as:

\[
S_t=\max(0,S_{t-1}+z_t-k),
\]

and raises an alarm when:

\[
S_t>h.
\]

Where:

- \(z_t\) is the monitored deviation;
- \(k\) ignores small expected fluctuations;
- \(h\) controls alarm sensitivity.

### What it brings to the MMALS-CAL paper

CUSUM is the simplest interpretable candidate for component A.

It is attractive because it is:

- incremental;
- computationally cheap;
- easy to audit;
- suitable for real-time systems;
- explicit about the false-alarm versus detection-delay trade-off.

For MMALS-CAL, it could monitor separate channels:

```text
CUSUM on class uncertainty
CUSUM on context uncertainty
CUSUM on route drift
CUSUM on embedding drift
CUSUM on delayed-label nonconformity
```

### Important limitation

CUSUM detects sustained change in a chosen signal. It does not explain the semantic meaning of the new regime, and it is only as good as:

- the monitored statistic;
- the reference distribution;
- the selected threshold;
- the assumed shift direction.

It should therefore not be confused with MMALS context inference itself.

---

# 9. Thomas et al., 2019  
## *Preventing Undesirable Behavior of Intelligent Machines*

### Paraphrased abstract

The paper proposes a framework for designing machine-learning algorithms around explicit user-defined constraints on undesirable behavior. Rather than expecting users to indirectly control risk through penalties or hyperparameters, the framework asks them to specify the behavior that must be avoided and the acceptable probability of violation. The resulting Seldonian approach may refuse to return a solution when the available evidence is insufficient to support the required constraint. The authors demonstrate the approach on examples involving harmful or unfair behavior. ([science.org](https://www.science.org/doi/10.1126/science.aag3311?utm_source=chatgpt.com))

### Engineer translation

Normal ML design asks:

> Which model maximizes performance?

The Seldonian design question is:

> Which model maximizes performance while giving us enough statistical evidence that an undesirable condition will not be violated?

And when evidence is insufficient:

```text
do not return a supposedly safe solution
```

This is the same general fail-closed philosophy as:

```text
insufficient evidence
→ NO_DECISION
```

### What it brings to the MMALS-CAL paper

This reference supports the **system-design philosophy**, especially:

- explicit undesirable outcomes;
- evidence-based constraints;
- separating candidate construction from independent verification;
- refusing to act when the constraint cannot be supported;
- moving responsibility from the end user to the algorithm and protocol designer.

It also connects strongly to the MMALS Verification Stack:

```text
candidate result
    ↓
protocol verification
    ↓
statistical safety/evidence test
    ↓
release, ACTION, or refusal
```

### Critical distinction

MMALS-CAL is **not currently a Seldonian algorithm**.

The guarantee types differ:

- conformal prediction controls marginal coverage of prediction sets;
- Seldonian methods seek high-probability satisfaction of explicitly specified behavioral constraints.

Thomas et al. support our **fail-closed architecture and claim discipline**, but they should not be cited as proof that MMALS-CAL provides broad machine-safety guarantees.

---

# What the references collectively bring to MMALS-CAL

## 1. They establish the statistical foundation

Vovk et al. and Angelopoulos–Bates justify the transformation:

```text
model output
→ calibrated prediction set
→ measurable marginal coverage
```

Without these references, MMALS-CAL could look like an ad hoc confidence-thresholding mechanism.

With them, it is situated within conformal prediction.

## 2. They justify the five-axis decomposition

Sadinle et al. show why coverage must be separated from ambiguity.

That directly supports:

```text
Competence
Coverage
Compactness
Context
ACTION
```

A system can satisfy coverage while being non-actionable because its sets are too large.

## 3. They explain why v0.3.2 is deliberately offline

Classical split conformal gives the cleanest experimental foundation under controlled calibration/deployment separation.

The online papers demonstrate that the next step is possible, but also that it introduces new questions:

- adaptation rate;
- local-window validity;
- delayed labels;
- temporal dependence;
- calibration recovery;
- shift speed.

Thus, v0.3.2 validates components B, C, and a simplified D before adding component A.

## 4. They provide two different ways to handle changing regimes

### Explicit change detection

- Page: lightweight cumulative alarm;
- Adams–MacKay: probabilistic run-length inference.

### Continuous calibration adaptation

- Gibbs–Candès: feedback adaptation;
- FACI-style adaptation to shift speed;
- Bhatnagar et al.: interval-local strongly adaptive methods.

These are complementary rather than identical:

```text
change detection asks:
“Did the regime change?”

adaptive conformal asks:
“How should the prediction-set threshold evolve?”
```

A complete runtime MMALS-CAL may eventually need both.

## 5. They justify fail-closed behavior

Thomas et al. support the principle that an intelligent system should be allowed to return:

```text
insufficient evidence
```

rather than being forced to provide an answer.

This gives stronger intellectual grounding to:

```text
ACTION / NO_DECISION
```

and to MMALS-CAL’s prohibited-claims discipline.

---

# Recommended citation placement in the paper

| Paper section | References |
|---|---|
| Introduction to conformal prediction | Vovk et al.; Angelopoulos & Bates |
| Calibration quantile and exchangeability | Vovk et al.; Angelopoulos & Bates |
| Coverage versus compactness | Sadinle et al. |
| Stale evidence and distribution shift | Gibbs & Candès 2021 |
| Future adaptive calibration | Gibbs & Candès 2021, 2022; Bhatnagar et al. |
| Regime-change detector roadmap | Page; Adams & MacKay |
| ACTION/NO_DECISION and fail-closed design | Thomas et al. |
| Limitations | All online references, explicitly marked as not implemented |

## Suggested literature-positioning paragraph

MMALS-CAL builds on three complementary research traditions. Classical conformal prediction provides the statistical foundation for converting black-box model scores into prediction sets with finite-sample marginal coverage under exchangeability. Set-valued classification further establishes that coverage alone is insufficient and that ambiguity, measured through prediction-set size, must be controlled separately. Online conformal inference and changepoint-detection methods provide the foundations for the future transition from offline replay to runtime calibration freshness, while Seldonian algorithm design motivates the fail-closed principle that a system should refuse to act when the available evidence cannot support its declared constraint.

The current v0.3.2 release implements offline no-leakage calibration, regime-aware conformal quantiles, compactness auditing, and a conservative singleton ACTION/NO_DECISION baseline. It does not yet implement CUSUM, Bayesian online changepoint detection, adaptive conformal inference, FACI, or strongly adaptive online conformal prediction. These references therefore serve both as foundations for the implemented verification layer and as explicit methodological anchors for the next online stage.

The most important message is that the bibliography is not one undifferentiated list. It describes the evolution of the project:

\[
\text{offline conformal validity}
\rightarrow
\text{compactness and actionability}
\rightarrow
\text{regime-change detection}
\rightarrow
\text{online adaptive calibration}
\rightarrow
\text{fail-closed operational control}.
\]
