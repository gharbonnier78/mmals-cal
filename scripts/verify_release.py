#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
FIGURE_NAMES = [
    'competence_vs_actionability.png',
    'context_accuracy_vs_recall_loss.png',
    'coverage_vs_compactness.png',
    'five_axis_evidence_heatmap.png',
    'fresh_vs_stale_coverage.png',
    'set_size_and_action_rate.png',
    'worst_regime_coverage.png',
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    profile = pd.read_csv(RESULTS / 'benchmark_profile.csv')
    strategies = pd.read_csv(RESULTS / 'strategy_summary.csv')
    five_cols = [
        'source_final_avg_accuracy', 'oracle_coverage',
        'oracle_normalized_set_size', 'context_accuracy',
        'oracle_singleton_action_rate',
    ]
    checks = []
    checks.append(('seven_benchmarks', profile.dataset.nunique() == 7))
    checks.append(('five_strategies_each', (strategies.groupby('dataset').strategy.nunique() == 5).all()))
    checks.append(('250000_selected_rows', int(profile.n_selected_rows.sum()) == 250000))
    checks.append(('187500_deployment_rows', int(profile.n_deployment.sum()) == 187500))
    checks.append(('normalized_set_size_range', strategies.normalized_mean_set_size.between(0, 1).all()))
    checks.append(('action_partition', np.allclose(strategies.singleton_action_rate_mean + strategies.no_decision_rate_mean, 1, atol=1e-10)))
    checks.append(('oracle_coverage_near_target', (profile.oracle_coverage.sub(.9).abs() <= .02).all()))
    checks.append(('five_axis_values_finite', not profile[five_cols].isna().any().any()))
    checks.append(('canonical_paper_exists', (ROOT / 'paper' / 'main.pdf').exists() and (ROOT / 'paper' / 'main.pdf').stat().st_size > 100_000))
    checks.append(('root_main_pdf_absent', not (ROOT / 'main.pdf').exists()))
    figures_ok = True
    synchronized = True
    for name in FIGURE_NAMES:
        generated = ROOT / 'figures' / name
        paper = ROOT / 'paper' / 'figures' / name
        figures_ok &= generated.exists() and paper.exists() and generated.stat().st_size > 10_000 and paper.stat().st_size > 10_000
        if generated.exists() and paper.exists():
            synchronized &= digest(generated) == digest(paper)
        else:
            synchronized = False
    checks.append(('publication_figures_present', figures_ok))
    checks.append(('paper_figures_synchronized', synchronized))

    for name, passed in checks:
        print(('PASS' if passed else 'FAIL'), name)
    status = {'passed': bool(all(v for _, v in checks)), 'checks': len(checks)}
    (RESULTS / 'verification_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    raise SystemExit(0 if status['passed'] else 1)


if __name__ == '__main__':
    main()
