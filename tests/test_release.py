from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIGURE_NAMES = [
    'competence_vs_actionability.png',
    'context_accuracy_vs_recall_loss.png',
    'coverage_vs_compactness.png',
    'five_axis_evidence_heatmap.png',
    'fresh_vs_stale_coverage.png',
    'set_size_and_action_rate.png',
    'worst_regime_coverage.png',
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_profile():
    p = pd.read_csv(ROOT / 'results' / 'benchmark_profile.csv')
    assert p.dataset.nunique() == 7
    assert int(p.n_selected_rows.sum()) == 250000
    assert int(p.n_deployment.sum()) == 187500


def test_traces_present():
    registry = pd.read_csv(ROOT / 'data' / 'selected_trace_registry.csv')
    assert len(registry) == 7
    assert registry.included.all()
    assert all((ROOT / path).exists() for path in registry.relative_path)


def test_five_axis_profile_has_no_missing_values():
    p = pd.read_csv(ROOT / 'results' / 'benchmark_profile.csv')
    cols = [
        'source_final_avg_accuracy', 'oracle_coverage',
        'oracle_normalized_set_size', 'context_accuracy',
        'oracle_singleton_action_rate',
    ]
    assert not p[cols].isna().any().any()


def test_publication_figures_exist_and_are_synchronized():
    for name in FIGURE_NAMES:
        generated = ROOT / 'figures' / name
        paper = ROOT / 'paper' / 'figures' / name
        assert generated.exists() and generated.stat().st_size > 10_000
        assert paper.exists() and paper.stat().st_size > 10_000
        assert sha256(generated) == sha256(paper)


def test_canonical_paper_only():
    assert (ROOT / 'paper' / 'main.pdf').exists()
    assert (ROOT / 'paper' / 'main.pdf').stat().st_size > 100_000
    assert not (ROOT / 'main.pdf').exists()
