#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDER = [
    'MNIST', 'FashionMNIST', 'PermutedMNIST', 'RotatedMNIST',
    'SplitCIFAR10', 'SplitCIFAR100', 'CORe50'
]


def annotate_points(ax, x, y, labels, offsets):
    """Add deterministic, readable labels with leader lines."""
    for xv, yv, label in zip(x, y, labels):
        dx, dy = offsets.get(label, (8, 8))
        ax.annotate(
            label,
            xy=(xv, yv),
            xytext=(dx, dy),
            textcoords='offset points',
            ha='left' if dx >= 0 else 'right',
            va='bottom' if dy >= 0 else 'top',
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.88),
            arrowprops=dict(arrowstyle='-', lw=0.8, shrinkA=2, shrinkB=2),
            annotation_clip=False,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', default=str(ROOT / 'results'))
    parser.add_argument('--output-dir', default=str(ROOT / 'figures'))
    args = parser.parse_args()
    results, output = Path(args.results_dir), Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    p = pd.read_csv(results / 'benchmark_profile.csv').set_index('dataset').loc[ORDER].reset_index()
    labels = p['dataset'].tolist()

    competence_offsets = {
        'MNIST': (-44, 20),
        'FashionMNIST': (10, -26),
        'PermutedMNIST': (10, 26),
        'RotatedMNIST': (-70, -22),
        'SplitCIFAR10': (12, 4),
        'SplitCIFAR100': (-62, 18),
        'CORe50': (12, 10),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(p.source_final_avg_accuracy, p.oracle_singleton_action_rate, s=90)
    annotate_points(ax, p.source_final_avg_accuracy, p.oracle_singleton_action_rate, labels, competence_offsets)
    ax.set_xlabel('Final average top-1 accuracy')
    ax.set_ylabel('Fresh singleton ACTION rate')
    ax.set_title('Predictive competence versus operational actionability')
    ax.set_xlim(.25, 1.03)
    ax.set_ylim(-.05, 1.06)
    fig.tight_layout()
    fig.savefig(output / 'competence_vs_actionability.png', dpi=190)
    plt.close(fig)

    compact = 1 - p.oracle_normalized_set_size
    compact_offsets = {
        'MNIST': (-55, -24),
        'FashionMNIST': (10, 18),
        'PermutedMNIST': (10, -22),
        'RotatedMNIST': (-62, 22),
        'SplitCIFAR10': (10, 8),
        'SplitCIFAR100': (-75, 18),
        'CORe50': (12, -20),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(compact, p.oracle_coverage, s=90)
    annotate_points(ax, compact, p.oracle_coverage, labels, compact_offsets)
    ax.axhline(.9, linestyle='--', label='90% target')
    ax.set_xlabel('Prediction-set compactness = 1 - mean set size / K')
    ax.set_ylabel('Fresh oracle-regime coverage')
    ax.set_title('Coverage can be restored without restoring compactness')
    ax.set_xlim(.38, 1.02)
    ax.set_ylim(.884, .912)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / 'coverage_vs_compactness.png', dpi=190)
    plt.close(fig)

    ax = p.set_index('dataset')[['oracle_coverage', 'stale_coverage']].plot(kind='bar', figsize=(11, 6))
    ax.axhline(.9, linestyle='--', label='90% target')
    ax.set_ylabel('Coverage')
    ax.set_xlabel('Benchmark')
    ax.set_title('Fresh regime calibration versus stale T0 calibration')
    ax.set_ylim(.70, 1.00)
    ax.legend()
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'fresh_vs_stale_coverage.png', dpi=190)
    plt.close()

    context_offsets = {
        'MNIST': (-28, 18),
        'FashionMNIST': (10, 18),
        'PermutedMNIST': (-70, -18),
        'RotatedMNIST': (10, -28),
        'SplitCIFAR10': (12, 4),
        'SplitCIFAR100': (-76, 18),
        'CORe50': (12, 8),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(p.context_accuracy, p.context_recall_coverage_loss, s=90)
    annotate_points(ax, p.context_accuracy, p.context_recall_coverage_loss, labels, context_offsets)
    ax.axhline(0, linestyle='--')
    ax.set_xlabel('Exported context accuracy')
    ax.set_ylabel('Coverage loss when context selects a regime calibrator')
    ax.set_title('Regime-recognition errors can invalidate calibration recall')
    ax.set_xlim(.68, 1.025)
    ymax = max(.02, float(p.context_recall_coverage_loss.max()) * 1.16)
    ax.set_ylim(-.012, ymax)
    fig.tight_layout()
    fig.savefig(output / 'context_accuracy_vs_recall_loss.png', dpi=190)
    plt.close(fig)

    matrix = pd.DataFrame(
        np.column_stack([
            p.source_final_avg_accuracy.to_numpy(dtype=float),
            p.oracle_coverage.to_numpy(dtype=float),
            (1 - p.oracle_normalized_set_size).to_numpy(dtype=float),
            p.context_accuracy.to_numpy(dtype=float),
            p.oracle_singleton_action_rate.to_numpy(dtype=float),
        ]),
        index=p['dataset'].to_numpy(),
        columns=['Competence', 'Coverage', 'Compactness', 'Context', 'ACTION'],
    )
    if matrix.isna().any().any():
        raise ValueError('Five-axis heatmap contains NaN values; aborting figure generation.')
    fig, ax = plt.subplots(figsize=(10, 6))
    img = ax.imshow(matrix.to_numpy(), aspect='auto', vmin=0, vmax=1)
    fig.colorbar(img, ax=ax, label='Value')
    ax.set_yticks(np.arange(len(matrix)), labels=matrix.index)
    ax.set_xticks(np.arange(len(matrix.columns)), labels=matrix.columns, rotation=30, ha='right')
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f'{matrix.iloc[i, j]:.2f}', ha='center', va='center', fontsize=8)
    ax.set_title('MMALS-CAL five-axis evidence profile')
    fig.tight_layout()
    fig.savefig(output / 'five_axis_evidence_heatmap.png', dpi=190)
    plt.close(fig)

    worst = p.set_index('dataset')[['global_worst_coverage', 'oracle_worst_coverage', 'context_selected_oracle_worst_coverage']]
    ax = worst.plot(kind='bar', figsize=(11, 6))
    ax.axhline(.9, linestyle='--', label='90% target')
    ax.set_ylabel('Worst seed-task coverage')
    ax.set_xlabel('Benchmark')
    ax.set_title('Aggregate coverage hides local regime failures')
    ax.set_ylim(0, 1)
    ax.legend()
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'worst_regime_coverage.png', dpi=190)
    plt.close()

    sa = p.set_index('dataset')[['oracle_normalized_set_size', 'oracle_singleton_action_rate']]
    ax = sa.plot(kind='bar', figsize=(11, 6))
    ax.set_ylabel('Fraction')
    ax.set_xlabel('Benchmark')
    ax.set_title('Normalized uncertainty-set size and singleton ACTION rate')
    ax.set_ylim(0, 1)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'set_size_and_action_rate.png', dpi=190)
    plt.close()

    # Keep the canonical paper figures synchronized with generated figures.
    if output.resolve() == (ROOT / 'figures').resolve():
        paper_figures = ROOT / 'paper' / 'figures'
        paper_figures.mkdir(parents=True, exist_ok=True)
        for figure in output.glob('*.png'):
            shutil.copy2(figure, paper_figures / figure.name)

    print(f'Wrote figures to {output}')


if __name__ == '__main__':
    main()
