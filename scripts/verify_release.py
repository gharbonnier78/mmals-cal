#!/usr/bin/env python3
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
FIGURES = ROOT / 'figures'
PAPER = ROOT / 'paper' / 'main.pdf'
REQUIRED_FIGURES = [
    'competence_vs_actionability.png',
    'context_accuracy_vs_recall_loss.png',
    'coverage_vs_compactness.png',
    'five_axis_evidence_heatmap.png',
    'fresh_vs_stale_coverage.png',
    'set_size_and_action_rate.png',
    'worst_regime_coverage.png',
]


def main():
    profile = pd.read_csv(RESULTS / 'benchmark_profile.csv')
    strategies = pd.read_csv(RESULTS / 'strategy_summary.csv')
    five_axis = pd.read_csv(RESULTS / 'five_axis_profile.csv')

    figures_ok = all(
        (FIGURES / name).exists() and (FIGURES / name).stat().st_size > 10_000
        for name in REQUIRED_FIGURES
    )

    checks = [
        ('seven_benchmarks', profile.dataset.nunique() == 7),
        (
            'five_strategies_each',
            (strategies.groupby('dataset').strategy.nunique() == 5).all(),
        ),
        ('250000_selected_rows', int(profile.n_selected_rows.sum()) == 250000),
        ('187500_deployment_rows', int(profile.n_deployment.sum()) == 187500),
        (
            'normalized_set_size_range',
            strategies.normalized_mean_set_size.between(0, 1).all(),
        ),
        (
            'action_partition',
            np.allclose(
                strategies.singleton_action_rate_mean
                + strategies.no_decision_rate_mean,
                1,
                atol=1e-10,
            ),
        ),
        (
            'oracle_coverage_near_target',
            (profile.oracle_coverage.sub(0.9).abs() <= 0.02).all(),
        ),
        ('five_axis_profile_has_no_nan', not five_axis.isna().any().any()),
        ('required_figures_present_and_nonempty', figures_ok),
        ('compiled_paper_present', PAPER.exists() and PAPER.stat().st_size > 100_000),
    ]

    for name, passed in checks:
        print(('PASS' if passed else 'FAIL'), name)

    status = {
        'passed': bool(all(value for _, value in checks)),
        'checks': len(checks),
        'figure_integrity_pass': bool(
            not five_axis.isna().any().any() and figures_ok
        ),
    }
    (RESULTS / 'verification_status.json').write_text(
        json.dumps(status, indent=2), encoding='utf-8'
    )
    raise SystemExit(0 if status['passed'] else 1)


if __name__ == '__main__':
    main()
