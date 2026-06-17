"""Conformal quantile and prediction-set construction."""
from __future__ import annotations

import math
import numpy as np


def finite_sample_quantile(scores, alpha: float = 0.10) -> float:
    """Return the finite-sample corrected split-conformal quantile.

    For sorted calibration scores s_(1) <= ... <= s_(n), this returns
    s_(k), where k = min(n, ceil((n + 1) * (1 - alpha))).
    """
    values = np.sort(np.asarray(scores, dtype=float))
    n = len(values)
    if n == 0:
        return float('nan')
    k = min(n, int(math.ceil((n + 1) * (1.0 - alpha))))
    return float(values[k - 1])


def lac_nonconformity(probabilities, true_labels):
    """Least-ambiguous-class score s(x,y)=1-p(y|x)."""
    probs = np.asarray(probabilities, dtype=float)
    labels = np.asarray(true_labels, dtype=int)
    return 1.0 - probs[np.arange(len(labels)), labels]


def prediction_membership(probabilities, qhat):
    """Boolean prediction-set membership for LAC scores."""
    probs = np.asarray(probabilities, dtype=float)
    q = np.asarray(qhat, dtype=float)
    threshold = 1.0 - q
    if threshold.ndim == 0:
        return probs >= threshold
    return probs >= threshold[:, None]
