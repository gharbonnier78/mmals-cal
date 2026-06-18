#!/usr/bin/env python3
from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDER = [
    'MNIST',
    'FashionMNIST',
    'PermutedMNIST',
    'RotatedMNIST',
    'SplitCIFAR10',
    'SplitCIFAR100',
    'CORe50',
]


def annotate_with_arrows(ax, points, label_positions):
    """Attach readable labels to dense scatter points with leader arrows.

    The label coordinates are expressed in data coordinates so the published
    figure remains deterministic across Matplotlib versions and renderers.
    """
    for name, x, y in points:
        tx, ty = label_positions[name]
        ax.annotate(
            name,
            xy=(x, y),
            xytext=(tx, ty),
            textcoords='data',
            ha='center',
            va='center',
            fontsize=9.5,
            arrowprops={
                'arrowstyle': '-',
                'linewidth': 0.9,
                'shrinkA': 3,
                'shrinkB': 4,
                'connectionstyle': 'arc3,rad=0.08',
            },
            bbox={
                'boxstyle': 'round,pad=0.16',
                'facecolor': 'white',
                'edgecolor': 'none',
                'alpha': 0.92,
            },
            annotation_clip=False,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', default=str(ROOT / 'results'))
    parser.add_argument('--output-dir', default=str(ROOT / 'figures'))
    args = parser.parse_args()

    results = Path(args.results_dir)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    p = (
        pd.read_csv(results / 'benchmark_profile.csv')
        .set_index('dataset')
        .loc[ORDER]
        .reset_index()
    )

    # ------------------------------------------------------------------
    # Competence versus actionability
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    ax.scatter(
        p.source_final_avg_accuracy,
        p.oracle_singleton_action_rate,
        s=82,
        zorder=3,
    )
    competence_points = [
        (r.dataset, r.source_final_avg_accuracy, r.oracle_singleton_action_rate)
        for _, r in p.iterrows()
    ]
    competence_labels = {
        'CORe50': (0.365, 0.048),
        'SplitCIFAR100': (0.605, 0.145),
        'FashionMNIST': (0.790, 0.835),
        'SplitCIFAR10': (0.790, 0.995),
        'MNIST': (1.035, 0.825),
        'RotatedMNIST': (1.035, 0.935),
        'PermutedMNIST': (0.895, 1.015),
    }
    annotate_with_arrows(ax, competence_points, competence_labels)
    ax.set_xlabel('Final average top-1 accuracy')
    ax.set_ylabel('Fresh singleton ACTION rate')
    ax.set_title('Predictive competence versus operational actionability')
    ax.set_xlim(0.26, 1.075)
    ax.set_ylim(-0.03, 1.055)
    ax.grid(alpha=0.18, linewidth=0.6)
    fig.tight_layout()
    fig.savefig(output / 'competence_vs_actionability.png', dpi=220)
    plt.close(fig)

    # ------------------------------------------------------------------
    # Coverage versus compactness
    # ------------------------------------------------------------------
    compact = 1.0 - p.oracle_normalized_set_size
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    ax.scatter(compact, p.oracle_coverage, s=82, zorder=3)
    compact_points = [
        (r.dataset, float(compact.iloc[i]), r.oracle_coverage)
        for i, r in p.iterrows()
    ]
    compact_labels = {
        'CORe50': (0.490, 0.9050),
        'MNIST': (0.800, 0.8842),
        'FashionMNIST': (0.755, 0.8960),
        'RotatedMNIST': (0.805, 0.8990),
        'PermutedMNIST': (0.790, 0.9093),
        'SplitCIFAR10': (0.850, 0.9160),
        'SplitCIFAR100': (0.935, 0.9112),
    }
    annotate_with_arrows(ax, compact_points, compact_labels)
    ax.axhline(0.9, linestyle='--', label='90% target', zorder=1)
    ax.set_xlabel('Prediction-set compactness = 1 - mean set size / K')
    ax.set_ylabel('Fresh oracle-regime coverage')
    ax.set_title('Coverage can be restored without restoring compactness')
    ax.set_xlim(0.40, 0.97)
    ax.set_ylim(0.882, 0.919)
    ax.grid(alpha=0.18, linewidth=0.6)
    ax.legend(loc='lower left')
    fig.tight_layout()
    fig.savefig(output / 'coverage_vs_compactness.png', dpi=220)
    plt.close(fig)

    # ------------------------------------------------------------------
    # Fresh versus stale coverage
    # ------------------------------------------------------------------
    ax = p.set_index('dataset')[['oracle_coverage', 'stale_coverage']].plot(
        kind='bar', figsize=(11, 6)
    )
    ax.axhline(0.9, linestyle='--', label='90% target')
    ax.set_ylabel('Coverage')
    ax.set_xlabel('Benchmark')
    ax.set_title('Fresh regime calibration versus stale T0 calibration')
    ax.set_ylim(0.70, 1.00)
    ax.legend()
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'fresh_vs_stale_coverage.png', dpi=220)
    plt.close()

    # ------------------------------------------------------------------
    # Context accuracy versus recall loss
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    ax.scatter(
        p.context_accuracy,
        p.context_recall_coverage_loss,
        s=82,
        zorder=3,
    )
    context_points = [
        (r.dataset, r.context_accuracy, r.context_recall_coverage_loss)
        for _, r in p.iterrows()
    ]
    context_labels = {
        'CORe50': (0.755, 0.1795),
        'FashionMNIST': (0.855, 0.0290),
        'SplitCIFAR100': (0.940, 0.0430),
        'SplitCIFAR10': (0.865, 0.0120),
        'PermutedMNIST': (0.890, -0.0150),
        'RotatedMNIST': (1.070, 0.0320),
        'MNIST': (1.072, -0.0140),
    }
    annotate_with_arrows(ax, context_points, context_labels)
    ax.axhline(0, linestyle='--', zorder=1)
    ax.set_xlabel('Exported context accuracy')
    ax.set_ylabel('Coverage loss when context selects a regime calibrator')
    ax.set_title('Regime-recognition errors can invalidate calibration recall')
    ax.set_xlim(0.65, 1.115)
    ax.set_ylim(-0.030, 0.190)
    ax.grid(alpha=0.18, linewidth=0.6)
    fig.tight_layout()
    fig.savefig(output / 'context_accuracy_vs_recall_loss.png', dpi=220)
    plt.close(fig)

    # ------------------------------------------------------------------
    # Five-axis heatmap.  Use a dataset-indexed frame before assigning
    # columns; constructing a DataFrame from RangeIndex Series and a string
    # index silently aligns to NaN, which caused the broken published image.
    # ------------------------------------------------------------------
    matrix = p.set_index('dataset')[
        [
            'source_final_avg_accuracy',
            'oracle_coverage',
            'oracle_normalized_set_size',
            'context_accuracy',
            'oracle_singleton_action_rate',
        ]
    ].copy()
    matrix['oracle_normalized_set_size'] = (
        1.0 - matrix['oracle_normalized_set_size']
    )
    matrix.columns = [
        'Competence',
        'Coverage',
        'Compactness',
        'Context',
        'ACTION',
    ]

    if matrix.isna().any().any():
        raise ValueError('Five-axis profile contains NaN values after alignment.')

    fig, ax = plt.subplots(figsize=(10, 6))
    image = ax.imshow(matrix.to_numpy(), aspect='auto', vmin=0, vmax=1)
    fig.colorbar(image, ax=ax, label='Value')
    ax.set_yticks(np.arange(len(matrix)), matrix.index)
    ax.set_xticks(
        np.arange(len(matrix.columns)),
        matrix.columns,
        rotation=30,
        ha='right',
    )
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = float(matrix.iloc[i, j])
            text_color = 'white' if value < 0.50 else 'black'
            ax.text(
                j,
                i,
                f'{value:.2f}',
                ha='center',
                va='center',
                color=text_color,
                fontsize=9.5,
            )
    ax.set_title('MMALS-CAL five-axis evidence profile - v0.3.2')
    fig.tight_layout()
    fig.savefig(output / 'five_axis_evidence_heatmap.png', dpi=220)
    plt.close(fig)

    # ------------------------------------------------------------------
    # Worst-regime coverage
    # ------------------------------------------------------------------
    worst = p.set_index('dataset')[
        [
            'global_worst_coverage',
            'oracle_worst_coverage',
            'context_selected_oracle_worst_coverage',
        ]
    ]
    ax = worst.plot(kind='bar', figsize=(11, 6))
    ax.axhline(0.9, linestyle='--', label='90% target')
    ax.set_ylabel('Worst seed-task coverage')
    ax.set_xlabel('Benchmark')
    ax.set_title('Aggregate coverage hides local regime failures')
    ax.set_ylim(0, 1)
    ax.legend()
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'worst_regime_coverage.png', dpi=220)
    plt.close()

    # ------------------------------------------------------------------
    # Set size and action rate
    # ------------------------------------------------------------------
    set_action = p.set_index('dataset')[
        ['oracle_normalized_set_size', 'oracle_singleton_action_rate']
    ]
    ax = set_action.plot(kind='bar', figsize=(11, 6))
    ax.set_ylabel('Fraction')
    ax.set_xlabel('Benchmark')
    ax.set_title('Normalized uncertainty-set size and singleton ACTION rate')
    ax.set_ylim(0, 1)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.savefig(output / 'set_size_and_action_rate.png', dpi=220)
    plt.close()

    print(f'Wrote figures to {output}')


if __name__ == '__main__':
    main()
