#!/usr/bin/env python3
"""Populate optional Drive or archive locations in the external-source registry."""
from pathlib import Path
import argparse
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/external_source_locations.csv'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--artifact',required=True,help='Exact original artifact filename')
    p.add_argument('--location',required=True,help='Drive path, URI, or archive location')
    args=p.parse_args()
    df=pd.read_csv(REGISTRY)
    mask=df['artifact_filename']==args.artifact
    if not mask.any(): raise SystemExit(f'Unknown artifact: {args.artifact}')
    df.loc[mask,'user_supplied_location']=args.location
    df.to_csv(REGISTRY,index=False)
    print(f'Updated {args.artifact}')
if __name__=='__main__': main()
