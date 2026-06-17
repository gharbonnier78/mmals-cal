# Reproducibility and Data Access

## What is fully included

The repository contains all seven compressed selected-policy final-checkpoint traces required to replay the published analysis. No external download is required for the v0.3.2 numerical reproduction.

The complete replay is implemented by:

- `src/mmals_cal/replay.py`
- `scripts/run_cross_benchmark_replay.py`
- `configs/cross_benchmark_v0.3.2.json`

## What is intentionally not included

The original full MMALS evidence packages and multipart raw score dumps are much larger than the filtered traces and are not required for the replay. They are retained only for upstream provenance and future re-extraction.

Their exact filenames and known SHA-256 hashes are recorded in:

- `data/external_source_locations.csv`

The `user_supplied_location` field is blank. It can later contain a Google Drive path, institutional archive URI, Zenodo DOI, or local archival path.

## Reproduction levels

1. **Result inspection:** use the committed `results/` and `figures/`.
2. **Full metric replay:** run the CLI against the included seven traces.
3. **Trace re-extraction:** use the original evidence packages and `scripts/extract_selected_traces.py` where the archive follows the standard MMALS ZIP layout.
4. **Upstream model retraining:** outside this repository; it belongs to the benchmark-specific MMALS packages.

## Portability

All release paths are relative to the repository root. No `/mnt/data/...` build paths appear in the replay configuration or selected-trace registry.
