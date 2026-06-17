"""Deterministic no-leakage offline split utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd


def assign_harmonized_roles(df: pd.DataFrame, split_seed: int = 20260616) -> pd.DataFrame:
    """Assign 25% calibration and 75% deployment per seed-task-class group.

    Selection is deterministic and independent of probabilities, correctness,
    predicted labels, and context confidence. Each observation receives exactly
    one irreversible role in the offline replay.
    """
    required = {'seed', 'task_id', 'true_class'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing split columns: {sorted(missing)}')

    out = df.copy()
    out['role'] = 'deployment'
    groups = out.groupby(['seed', 'task_id', 'true_class']).groups
    for (seed, task, true_class), indices in groups.items():
        indices = np.asarray(list(indices))
        n_cal = len(indices) // 4
        rng = np.random.default_rng(
            int(split_seed) + int(seed) * 100000 + int(task) * 1000 + int(true_class)
        )
        selected = indices[rng.permutation(len(indices))[:n_cal]]
        out.loc[selected, 'role'] = 'calibration_reserved'
    return out
