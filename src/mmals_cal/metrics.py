"""Metrics for coverage, compactness, context, and actionability."""
from __future__ import annotations

import numpy as np
import pandas as pd


def rank_auc(scores, labels) -> float:
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=bool)
    valid = np.isfinite(scores)
    scores, labels = scores[valid], labels[valid]
    n_pos, n_neg = int(labels.sum()), int((~labels).sum())
    if n_pos == 0 or n_neg == 0:
        return float('nan')
    ranks = pd.Series(scores).rank(method='average').to_numpy()
    return float((ranks[labels].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def summarize_decisions(group: pd.DataFrame, target_coverage: float = 0.90) -> dict:
    action = group['action'].astype(bool)
    coverage = float(group['covered'].mean())
    return {
        'n': int(len(group)),
        'coverage': coverage,
        'coverage_deficit': float(max(0.0, target_coverage - coverage)),
        'mean_set_size': float(group['set_size'].mean()),
        'normalized_mean_set_size': float(group['normalized_set_size'].mean()),
        'p90_set_size': float(group['set_size'].quantile(0.90, interpolation='higher')),
        'empty_rate': float(group['is_empty'].mean()),
        'singleton_action_rate': float(action.mean()),
        'no_decision_rate': float(1.0 - action.mean()),
        'action_accuracy': float(group.loc[action, 'action_correct'].mean()) if action.any() else float('nan'),
        'wrong_action_rate_all': float(group['wrong_action'].mean()),
        'top1_accuracy': float(group['top1_correct'].mean()),
        'valid_calibrator_rate': float(group['valid_calibrator'].mean()),
    }
