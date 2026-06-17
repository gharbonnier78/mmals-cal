"""Input and release-verification helpers."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
import numpy as np
import pandas as pd


def score_columns(df: pd.DataFrame):
    cols = [c for c in df.columns if re.fullmatch(r'score_class_\d+', c)]
    return sorted(cols, key=lambda c: int(c.rsplit('_', 1)[1]))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verify_trace(dataset: str, df: pd.DataFrame, expected_method: str) -> dict:
    scores = score_columns(df)
    values = df[scores].to_numpy(dtype=float)
    score_sum_deviation = np.abs(values.sum(axis=1) - 1.0)
    argmax = values.argmax(axis=1)
    predicted = df['predicted_class'].to_numpy(dtype=int)
    duplicate_count = int(df.duplicated(['seed', 'task_id', 'sample_id']).sum())
    mismatch_count = int((argmax != predicted).sum())
    method = str(df['method'].iloc[0])
    passed = bool(
        score_sum_deviation.max() < 1e-5
        and mismatch_count == 0
        and duplicate_count == 0
        and method == expected_method
    )
    return {
        'dataset': dataset,
        'n_rows': int(len(df)),
        'n_score_classes': int(len(scores)),
        'n_seeds': int(df['seed'].nunique()),
        'n_tasks': int(df['task_id'].nunique()),
        'n_true_classes': int(df['true_class'].nunique()),
        'after_task_values': str(sorted(int(x) for x in df['after_task'].unique())),
        'selected_method': method,
        'expected_selected_method': expected_method,
        'max_probability_sum_deviation': float(score_sum_deviation.max()),
        'argmax_mismatch_count': mismatch_count,
        'duplicate_key_count': duplicate_count,
        'method_matches_manifest': method == expected_method,
        'probabilities_normalized': bool(score_sum_deviation.max() < 1e-5),
        'argmax_consistent': mismatch_count == 0,
        'unique_sample_keys': duplicate_count == 0,
        'passed': passed,
    }
