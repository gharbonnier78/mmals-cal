#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['MNIST','FashionMNIST','PermutedMNIST','RotatedMNIST','SplitCIFAR10','SplitCIFAR100','CORe50']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', default=str(ROOT/'results'))
    parser.add_argument('--output-dir', default=str(ROOT/'figures'))
    args = parser.parse_args()
    results, output = Path(args.results_dir), Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(results/'benchmark_profile.csv').set_index('dataset').loc[ORDER].reset_index()

    plt.figure(figsize=(9,6)); plt.scatter(p.source_final_avg_accuracy,p.oracle_singleton_action_rate,s=90)
    for _,r in p.iterrows(): plt.annotate(r.dataset,(r.source_final_avg_accuracy,r.oracle_singleton_action_rate),xytext=(5,5),textcoords='offset points')
    plt.xlabel('Final average top-1 accuracy'); plt.ylabel('Fresh singleton ACTION rate'); plt.title('Predictive competence versus operational actionability'); plt.xlim(.25,1.01); plt.ylim(-.03,1.02); plt.tight_layout(); plt.savefig(output/'competence_vs_actionability.png',dpi=190); plt.close()

    compact = 1-p.oracle_normalized_set_size
    plt.figure(figsize=(9,6)); plt.scatter(compact,p.oracle_coverage,s=90)
    for i,r in p.iterrows(): plt.annotate(r.dataset,(compact.iloc[i],r.oracle_coverage),xytext=(5,5),textcoords='offset points')
    plt.axhline(.9,linestyle='--',label='90% target'); plt.xlabel('Prediction-set compactness = 1 - mean set size / K'); plt.ylabel('Fresh oracle-regime coverage'); plt.title('Coverage can be restored without restoring compactness'); plt.ylim(.86,.92); plt.legend(); plt.tight_layout(); plt.savefig(output/'coverage_vs_compactness.png',dpi=190); plt.close()

    ax=p.set_index('dataset')[['oracle_coverage','stale_coverage']].plot(kind='bar',figsize=(11,6)); ax.axhline(.9,linestyle='--',label='90% target'); ax.set_ylabel('Coverage'); ax.set_xlabel('Benchmark'); ax.set_title('Fresh regime calibration versus stale T0 calibration'); ax.set_ylim(.70,1.00); ax.legend(); plt.xticks(rotation=35,ha='right'); plt.tight_layout(); plt.savefig(output/'fresh_vs_stale_coverage.png',dpi=190); plt.close()

    plt.figure(figsize=(9,6)); plt.scatter(p.context_accuracy,p.context_recall_coverage_loss,s=90)
    for _,r in p.iterrows(): plt.annotate(r.dataset,(r.context_accuracy,r.context_recall_coverage_loss),xytext=(5,5),textcoords='offset points')
    plt.axhline(0,linestyle='--'); plt.xlabel('Exported context accuracy'); plt.ylabel('Coverage loss when context selects a regime calibrator'); plt.title('Regime-recognition errors can invalidate calibration recall'); plt.xlim(.65,1.01); plt.tight_layout(); plt.savefig(output/'context_accuracy_vs_recall_loss.png',dpi=190); plt.close()

    matrix=pd.DataFrame({'Competence':p.source_final_avg_accuracy,'Coverage':p.oracle_coverage,'Compactness':1-p.oracle_normalized_set_size,'Context':p.context_accuracy,'ACTION':p.oracle_singleton_action_rate},index=p.dataset)
    plt.figure(figsize=(10,6)); img=plt.imshow(matrix.to_numpy(),aspect='auto',vmin=0,vmax=1); plt.colorbar(img,label='Value'); plt.yticks(np.arange(len(matrix)),matrix.index); plt.xticks(np.arange(len(matrix.columns)),matrix.columns,rotation=30,ha='right')
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]): plt.text(j,i,f'{matrix.iloc[i,j]:.2f}',ha='center',va='center')
    plt.title('MMALS-CAL five-axis evidence profile'); plt.tight_layout(); plt.savefig(output/'five_axis_evidence_heatmap.png',dpi=190); plt.close()

    worst=p.set_index('dataset')[['global_worst_coverage','oracle_worst_coverage','context_selected_oracle_worst_coverage']]
    ax=worst.plot(kind='bar',figsize=(11,6)); ax.axhline(.9,linestyle='--',label='90% target'); ax.set_ylabel('Worst seed-task coverage'); ax.set_xlabel('Benchmark'); ax.set_title('Aggregate coverage hides local regime failures'); ax.set_ylim(0,1); ax.legend(); plt.xticks(rotation=35,ha='right'); plt.tight_layout(); plt.savefig(output/'worst_regime_coverage.png',dpi=190); plt.close()

    sa=p.set_index('dataset')[['oracle_normalized_set_size','oracle_singleton_action_rate']]
    ax=sa.plot(kind='bar',figsize=(11,6)); ax.set_ylabel('Fraction'); ax.set_xlabel('Benchmark'); ax.set_title('Normalized uncertainty-set size and singleton ACTION rate'); ax.set_ylim(0,1); plt.xticks(rotation=35,ha='right'); plt.tight_layout(); plt.savefig(output/'set_size_and_action_rate.png',dpi=190); plt.close()

    print(f'Wrote figures to {output}')

if __name__=='__main__': main()
