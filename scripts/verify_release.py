#!/usr/bin/env python3
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'

def main():
    profile=pd.read_csv(RESULTS/'benchmark_profile.csv')
    strategies=pd.read_csv(RESULTS/'strategy_summary.csv')
    checks=[]
    checks.append(('seven_benchmarks',profile.dataset.nunique()==7))
    checks.append(('five_strategies_each',(strategies.groupby('dataset').strategy.nunique()==5).all()))
    checks.append(('250000_selected_rows',int(profile.n_selected_rows.sum())==250000))
    checks.append(('187500_deployment_rows',int(profile.n_deployment.sum())==187500))
    checks.append(('normalized_set_size_range',strategies.normalized_mean_set_size.between(0,1).all()))
    checks.append(('action_partition',np.allclose(strategies.singleton_action_rate_mean+strategies.no_decision_rate_mean,1,atol=1e-10)))
    checks.append(('oracle_coverage_near_target',(profile.oracle_coverage.sub(.9).abs()<=.02).all()))
    for name,passed in checks: print(('PASS' if passed else 'FAIL'),name)
    status={'passed':bool(all(v for _,v in checks)),'checks':len(checks)}
    (RESULTS/'verification_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    raise SystemExit(0 if status['passed'] else 1)
if __name__=='__main__': main()
