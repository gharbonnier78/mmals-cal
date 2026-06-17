# The Conformal Calibration Quantile - Definition

## Starting point: what is a quantile?

Sort a list of numbers from smallest to largest. The 90% quantile is a value below which approximately 90% of those numbers fall. For example, if 100 scores are sorted and their 90% quantile is 0.42, approximately 90 scores are at or below 0.42 and 10 are above it.

## The values sorted by MMALS-CAL: nonconformity scores

For an observation `x` with known true class `y`, MMALS-CAL computes

```text
s(x, y) = 1 - p(y | x)
```

where `p(y | x)` is the probability assigned by the model to the true class.

- If the model assigns high probability to the true class, the score is near zero: the observation is not very nonconforming.
- If the model assigns low probability to the true class, the score is near one: the correct answer surprised the model.

These scores are computed only on the reserved calibration set. That set is distinct from model training data and from the deployment set used to evaluate the resulting rule.

## The conformal quantile

For `n` calibration scores sorted as

```text
s_(1) <= s_(2) <= ... <= s_(n)
```

and tolerated error rate `alpha`, the finite-sample corrected index is

```text
k = min(n, ceil((n + 1) * (1 - alpha)))
```

and the conformal calibration quantile is

```text
q_hat = s_(k)
```

For a 90% target, `alpha = 0.10`. The `(n + 1)` correction, rather than simply taking the ordinary empirical 90th percentile, is the standard finite-sample split-conformal adjustment.

## From quantile to prediction set

For a new observation `x`, include every class whose hypothetical nonconformity score is no larger than the quantile:

```text
Gamma(x) = { y : 1 - p(y | x) <= q_hat }
```

Equivalently, include every class with

```text
p(y | x) >= 1 - q_hat
```

The quantile sets the tolerance bar:

- a smaller `q_hat` creates a more restrictive and usually smaller set;
- a larger `q_hat` creates a broader set, often improving coverage but reducing compactness and actionability.

## Why is it called conformal?

The method asks whether a new candidate label appears sufficiently consistent, or *conformal*, with the calibration scores. Under exchangeability - informally, calibration and deployment observations come from the same regime and no observation receives special treatment - the resulting set has a finite-sample marginal-coverage guarantee.

The guarantee is marginal, not automatically conditional for every task, class, seed, subgroup, or time interval. MMALS-CAL therefore reports both aggregate coverage and the worst seed-regime cells.

## Why regime-specific quantiles matter

If scores from different regimes are mixed, a global quantile can be valid on average but locally wrong. It may be too small for a difficult regime, causing undercoverage, and too large for an easy regime, causing unnecessarily broad sets. MMALS-CAL tests separate quantiles by oracle regime, inferred-context bucket, and context-selected recall to expose this difference.
