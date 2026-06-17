"""Complete seven-benchmark replay used by MMALS-CAL v0.3.2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from .conformal import finite_sample_quantile, lac_nonconformity
from .metrics import rank_auc, summarize_decisions
from .splitting import assign_harmonized_roles
from .verification import score_columns, sha256_file, verify_trace

STRATEGIES = [
    'global_seed',
    'stale_t0_seed',
    'oracle_task',
    'inferred_bucket',
    'oracle_qhat_selected_by_inferred_context',
]


def _qmaps(calibration: pd.DataFrame, alpha: float):
    q_global = {
        int(seed): finite_sample_quantile(group['nonconformity'], alpha)
        for seed, group in calibration.groupby('seed')
    }
    q_stale = {
        int(seed): finite_sample_quantile(
            group.loc[group['task_id'] == 0, 'nonconformity'], alpha
        )
        for seed, group in calibration.groupby('seed')
    }
    q_oracle = {
        (int(seed), int(task)): finite_sample_quantile(group['nonconformity'], alpha)
        for (seed, task), group in calibration.groupby(['seed', 'task_id'])
    }
    q_inferred = {
        (int(seed), int(context)): finite_sample_quantile(group['nonconformity'], alpha)
        for (seed, context), group in calibration.groupby(['seed', 'context_top'])
    }
    return q_global, q_stale, q_oracle, q_inferred


def replay_dataset(dataset: str, df: pd.DataFrame, cfg: dict, target: float, alpha: float, split_seed: int):
    df = df.copy()
    scores = score_columns(df)
    k_classes = len(scores)
    probs = df[scores].to_numpy(dtype=np.float32)
    labels = df['true_class'].to_numpy(dtype=int)
    df['nonconformity'] = lac_nonconformity(probs, labels)
    df = assign_harmonized_roles(df, split_seed)
    calibration = df[df['role'] == 'calibration_reserved'].copy()
    deployment = df[df['role'] == 'deployment'].copy().reset_index(drop=True)

    dep_probs = deployment[scores].to_numpy(dtype=np.float32)
    dep_labels = deployment['true_class'].to_numpy(dtype=int)
    dep_true_probability = dep_probs[np.arange(len(deployment)), dep_labels]
    q_global, q_stale, q_oracle, q_inferred = _qmaps(calibration, alpha)

    seed_task_rows, seed_rows = [], []
    for strategy in STRATEGIES:
        if strategy == 'global_seed':
            q_values = np.array([q_global[int(seed)] for seed in deployment['seed']], dtype=float)
        elif strategy == 'stale_t0_seed':
            q_values = np.array([q_stale[int(seed)] for seed in deployment['seed']], dtype=float)
        elif strategy == 'oracle_task':
            q_values = np.array([
                q_oracle.get((int(seed), int(task)), np.nan)
                for seed, task in zip(deployment['seed'], deployment['task_id'])
            ], dtype=float)
        elif strategy == 'inferred_bucket':
            q_values = np.array([
                q_inferred.get((int(seed), int(context)), np.nan)
                for seed, context in zip(deployment['seed'], deployment['context_top'])
            ], dtype=float)
        else:
            q_values = np.array([
                q_oracle.get((int(seed), int(context)), np.nan)
                for seed, context in zip(deployment['seed'], deployment['context_top'])
            ], dtype=float)

        valid = np.isfinite(q_values)
        thresholds = np.where(valid, 1.0 - q_values, np.inf)
        membership = dep_probs >= thresholds[:, None]
        set_size = membership.sum(axis=1)
        covered = valid & (dep_true_probability >= thresholds)
        action = valid & (set_size == 1)
        top1 = dep_probs.argmax(axis=1)

        decisions = pd.DataFrame({
            'dataset': dataset,
            'strategy': strategy,
            'seed': deployment['seed'].to_numpy(),
            'task_id': deployment['task_id'].to_numpy(),
            'covered': covered,
            'set_size': set_size,
            'normalized_set_size': set_size / k_classes,
            'is_empty': set_size == 0,
            'action': action,
            'action_correct': action & (top1 == dep_labels),
            'wrong_action': action & (top1 != dep_labels),
            'top1_correct': top1 == dep_labels,
            'valid_calibrator': valid,
        })

        for (seed, task), group in decisions.groupby(['seed', 'task_id']):
            row = {'dataset': dataset, 'strategy': strategy, 'seed': int(seed), 'task_id': int(task)}
            row.update(summarize_decisions(group, target))
            seed_task_rows.append(row)
        for seed, group in decisions.groupby('seed'):
            row = {'dataset': dataset, 'strategy': strategy, 'seed': int(seed)}
            row.update(summarize_decisions(group, target))
            seed_rows.append(row)

    seed_task = pd.DataFrame(seed_task_rows)
    seed_summary = pd.DataFrame(seed_rows)
    strategy_rows = []
    for strategy, group in seed_summary.groupby('strategy'):
        local = seed_task[seed_task['strategy'] == strategy]
        strategy_rows.append({
            'dataset': dataset,
            'strategy': strategy,
            'n_seeds': int(group['seed'].nunique()),
            'K': int(k_classes),
            'n_tasks': int(df['task_id'].nunique()),
            'n_selected_rows': int(len(df)),
            'n_calibration': int(len(calibration)),
            'n_deployment': int(len(deployment)),
            'target_coverage': target,
            'coverage_mean_across_seeds': float(group['coverage'].mean()),
            'coverage_std_across_seeds': float(group['coverage'].std(ddof=1)),
            'worst_seed_task_coverage': float(local['coverage'].min()),
            'max_seed_task_coverage_deficit': float(local['coverage_deficit'].max()),
            'mean_set_size_mean_across_seeds': float(group['mean_set_size'].mean()),
            'normalized_mean_set_size': float(group['normalized_mean_set_size'].mean()),
            'p90_set_size_mean_across_seeds': float(group['p90_set_size'].mean()),
            'empty_rate_mean': float(group['empty_rate'].mean()),
            'singleton_action_rate_mean': float(group['singleton_action_rate'].mean()),
            'no_decision_rate_mean': float(group['no_decision_rate'].mean()),
            'action_accuracy_mean': float(group['action_accuracy'].mean()),
            'wrong_action_rate_all_mean': float(group['wrong_action_rate_all'].mean()),
            'top1_accuracy_mean': float(group['top1_accuracy'].mean()),
            'valid_calibrator_rate_mean': float(group['valid_calibrator_rate'].mean()),
        })
    strategy_summary = pd.DataFrame(strategy_rows)

    context_correct = deployment['context_top'].to_numpy(int) == deployment['task_id'].to_numpy(int)
    context_frame = deployment[['task_id', 'context_margin', 'context_entropy']].copy()
    context_frame['context_correct'] = context_correct
    context_by_task = context_frame.groupby('task_id').agg(
        n=('context_correct','size'),
        context_accuracy=('context_correct','mean'),
        context_margin_mean=('context_margin','mean'),
        context_entropy_mean=('context_entropy','mean'),
    ).reset_index()
    context_by_task.insert(0, 'dataset', dataset)

    context_summary = pd.DataFrame([{
        'dataset': dataset,
        'context_accuracy': float(context_correct.mean()),
        'worst_task_context_accuracy': float(context_by_task['context_accuracy'].min()),
        'context_margin_auc_correct': rank_auc(deployment['context_margin'], context_correct),
        'negative_context_entropy_auc_correct': rank_auc(-deployment['context_entropy'], context_correct),
        'source_final_avg_acc_mean': float(cfg['final_avg_acc_mean']),
        'source_final_avg_acc_std': float(cfg['final_avg_acc_std']),
        'source_min_task_acc_mean': float(cfg['min_task_acc_mean']),
        'source_avg_forgetting_mean': float(cfg['avg_forgetting_mean']),
        'selected_method': cfg['selected_method'],
        'representation': cfg['representation'],
        'K': int(k_classes),
        'n_tasks': int(df['task_id'].nunique()),
        'n_selected_rows': int(len(df)),
        'n_calibration': int(len(calibration)),
        'n_deployment': int(len(deployment)),
    }])

    split_summary = df.groupby(['seed','task_id','true_class','role']).size().unstack(fill_value=0).reset_index()
    split_summary.insert(0, 'dataset', dataset)
    return strategy_summary, seed_task, seed_summary, context_by_task, context_summary, split_summary


def build_benchmark_profile(strategy_summary: pd.DataFrame, context_summary: pd.DataFrame) -> pd.DataFrame:
    index = strategy_summary.set_index(['dataset','strategy'])
    rows = []
    for _, r in context_summary.iterrows():
        d = r['dataset']
        def m(strategy, column):
            return float(index.loc[(d, strategy), column])
        rows.append({
            'dataset': d,
            'K': int(r['K']),
            'n_tasks': int(r['n_tasks']),
            'n_selected_rows': int(r['n_selected_rows']),
            'n_calibration': int(r['n_calibration']),
            'n_deployment': int(r['n_deployment']),
            'source_final_avg_accuracy': float(r['source_final_avg_acc_mean']),
            'source_min_task_accuracy': float(r['source_min_task_acc_mean']),
            'source_avg_forgetting': float(r['source_avg_forgetting_mean']),
            'context_accuracy': float(r['context_accuracy']),
            'worst_task_context_accuracy': float(r['worst_task_context_accuracy']),
            'context_margin_auc_correct': float(r['context_margin_auc_correct']) if np.isfinite(r['context_margin_auc_correct']) else np.nan,
            'negative_context_entropy_auc_correct': float(r['negative_context_entropy_auc_correct']) if np.isfinite(r['negative_context_entropy_auc_correct']) else np.nan,
            'global_coverage': m('global_seed','coverage_mean_across_seeds'),
            'global_worst_coverage': m('global_seed','worst_seed_task_coverage'),
            'stale_coverage': m('stale_t0_seed','coverage_mean_across_seeds'),
            'stale_worst_coverage': m('stale_t0_seed','worst_seed_task_coverage'),
            'oracle_coverage': m('oracle_task','coverage_mean_across_seeds'),
            'oracle_worst_coverage': m('oracle_task','worst_seed_task_coverage'),
            'oracle_mean_set_size': m('oracle_task','mean_set_size_mean_across_seeds'),
            'oracle_normalized_set_size': m('oracle_task','normalized_mean_set_size'),
            'oracle_singleton_action_rate': m('oracle_task','singleton_action_rate_mean'),
            'oracle_action_accuracy': m('oracle_task','action_accuracy_mean'),
            'oracle_wrong_action_rate_all': m('oracle_task','wrong_action_rate_all_mean'),
            'inferred_bucket_coverage': m('inferred_bucket','coverage_mean_across_seeds'),
            'inferred_bucket_action_rate': m('inferred_bucket','singleton_action_rate_mean'),
            'context_selected_oracle_coverage': m('oracle_qhat_selected_by_inferred_context','coverage_mean_across_seeds'),
            'context_selected_oracle_worst_coverage': m('oracle_qhat_selected_by_inferred_context','worst_seed_task_coverage'),
            'context_recall_coverage_loss': m('oracle_task','coverage_mean_across_seeds') - m('oracle_qhat_selected_by_inferred_context','coverage_mean_across_seeds'),
            'stale_coverage_loss_vs_oracle': m('oracle_task','coverage_mean_across_seeds') - m('stale_t0_seed','coverage_mean_across_seeds'),
            'representation': r['representation'],
            'selected_method': r['selected_method'],
        })
    return pd.DataFrame(rows)


def run_from_config(config_path: Path, output_dir: Path) -> dict:
    config_path = Path(config_path).resolve()
    project_root = config_path.parent.parent
    config = json.loads(config_path.read_text(encoding='utf-8'))
    data_root = project_root / config.get('data_root','data/raw')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    strategy_parts, regime_parts, seed_parts = [], [], []
    context_task_parts, context_summary_parts, split_parts = [], [], []
    input_rows, source_rows = [], []

    for dataset, cfg in config['datasets'].items():
        trace = data_root / cfg['trace']
        df = pd.read_csv(trace)
        input_rows.append(verify_trace(dataset, df, cfg['selected_method']))
        source_rows.append({
            'dataset': dataset,
            'selected_trace': str(Path(config.get('data_root','data/raw')) / cfg['trace']),
            'selected_trace_sha256': sha256_file(trace),
            'selected_method': cfg['selected_method'],
            'representation': cfg['representation'],
        })
        parts = replay_dataset(dataset, df, cfg, config['target_coverage'], config['alpha'], config['split_seed'])
        strategy_parts.append(parts[0]); regime_parts.append(parts[1]); seed_parts.append(parts[2])
        context_task_parts.append(parts[3]); context_summary_parts.append(parts[4]); split_parts.append(parts[5])

    strategy_summary = pd.concat(strategy_parts, ignore_index=True)
    regime_summary = pd.concat(regime_parts, ignore_index=True)
    seed_summary = pd.concat(seed_parts, ignore_index=True)
    context_by_task = pd.concat(context_task_parts, ignore_index=True)
    context_summary = pd.concat(context_summary_parts, ignore_index=True)
    split_summary = pd.concat(split_parts, ignore_index=True)
    input_verification = pd.DataFrame(input_rows)
    source_manifest = pd.DataFrame(source_rows)
    benchmark_profile = build_benchmark_profile(strategy_summary, context_summary)
    five_axis = benchmark_profile[['dataset','source_final_avg_accuracy','oracle_coverage','oracle_normalized_set_size','context_accuracy','oracle_singleton_action_rate']].copy()
    five_axis['set_compactness'] = 1.0 - five_axis['oracle_normalized_set_size']
    five_axis = five_axis[['dataset','source_final_avg_accuracy','oracle_coverage','set_compactness','context_accuracy','oracle_singleton_action_rate']]

    files = {
        'strategy_summary.csv': strategy_summary,
        'regime_summary_by_seed_task.csv': regime_summary,
        'seed_summary.csv': seed_summary,
        'context_by_task.csv': context_by_task,
        'context_summary.csv': context_summary,
        'split_summary.csv': split_summary,
        'input_verification.csv': input_verification,
        'source_manifest.csv': source_manifest,
        'benchmark_profile.csv': benchmark_profile,
        'five_axis_profile.csv': five_axis,
    }
    for name, frame in files.items():
        frame.to_csv(output_dir/name, index=False)

    status = {
        'version': config['version'],
        'benchmarks': int(benchmark_profile['dataset'].nunique()),
        'selected_rows': int(benchmark_profile['n_selected_rows'].sum()),
        'calibration_rows': int(benchmark_profile['n_calibration'].sum()),
        'deployment_rows': int(benchmark_profile['n_deployment'].sum()),
        'all_input_checks_pass': bool(input_verification['passed'].all()),
    }
    (output_dir/'replay_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    return {'status': status, 'benchmark_profile': benchmark_profile, 'strategy_summary': strategy_summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/cross_benchmark_v0.3.2.json')
    parser.add_argument('--output-dir', default='results')
    args = parser.parse_args()
    result = run_from_config(Path(args.config), Path(args.output_dir))
    print(json.dumps(result['status'], indent=2))
    print(result['benchmark_profile'][['dataset','source_final_avg_accuracy','context_accuracy','oracle_coverage','oracle_mean_set_size','oracle_singleton_action_rate']].to_string(index=False))


if __name__ == '__main__':
    main()
