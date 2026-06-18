from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_release_profile():
    profile = pd.read_csv(ROOT / 'results/benchmark_profile.csv')
    assert profile.dataset.nunique() == 7
    assert int(profile.n_selected_rows.sum()) == 250000
    assert int(profile.n_deployment.sum()) == 187500


def test_traces_present():
    registry = pd.read_csv(ROOT / 'data/selected_trace_registry.csv')
    assert len(registry) == 7
    assert registry.included.all()
    assert all((ROOT / path).exists() for path in registry.relative_path)


def test_five_axis_profile_contains_numeric_values():
    profile = pd.read_csv(ROOT / 'results/five_axis_profile.csv')
    assert not profile.isna().any().any()
    numeric = profile.drop(columns=['dataset'])
    assert numeric.apply(lambda column: column.between(0, 1).all()).all()


def test_publication_figures_are_present_and_nonempty():
    required = [
        'competence_vs_actionability.png',
        'context_accuracy_vs_recall_loss.png',
        'coverage_vs_compactness.png',
        'five_axis_evidence_heatmap.png',
        'fresh_vs_stale_coverage.png',
        'set_size_and_action_rate.png',
        'worst_regime_coverage.png',
    ]
    for name in required:
        path = ROOT / 'figures' / name
        assert path.exists()
        assert path.stat().st_size > 10_000
