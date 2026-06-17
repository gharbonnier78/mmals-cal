from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def test_release_profile():
    p=pd.read_csv(ROOT/'results/benchmark_profile.csv')
    assert p.dataset.nunique()==7
    assert int(p.n_selected_rows.sum())==250000
    assert int(p.n_deployment.sum())==187500

def test_traces_present():
    registry=pd.read_csv(ROOT/'data/selected_trace_registry.csv')
    assert len(registry)==7
    assert registry.included.all()
    assert all((ROOT/path).exists() for path in registry.relative_path)
