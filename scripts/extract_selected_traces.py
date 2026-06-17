#!/usr/bin/env python3
"""Extract a selected-policy score trace from a standard MMALS evidence ZIP.

For very large multipart archives (SplitCIFAR100 and CORe50), use the already
released selected traces or first reconstruct/extract the full score dump as
explained in data/README.md.
"""
from pathlib import Path
import argparse, io, zipfile
import pandas as pd


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True)
    p.add_argument('--method',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--after-task',type=int,default=None)
    args=p.parse_args()
    archive=Path(args.archive); output=Path(args.output)
    with zipfile.ZipFile(archive) as z:
        candidates=[n for n in z.namelist() if n.endswith('biometric_style_score_dump_robust.csv')]
        if not candidates: raise SystemExit('No biometric_style_score_dump_robust.csv found')
        with z.open(candidates[0]) as handle:
            df=pd.read_csv(handle)
    selected=df[df['method']==args.method].copy()
    if args.after_task is not None:
        selected=selected[selected['after_task']==args.after_task].copy()
    output.parent.mkdir(parents=True,exist_ok=True)
    selected.to_csv(output,index=False,compression='gzip' if output.suffix=='.gz' else None)
    print(f'Wrote {len(selected):,} rows to {output}')
if __name__=='__main__': main()
