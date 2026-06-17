# MMALS-CAL v0.3.2 delta package

This archive upgrades the v0.3.1 GitHub package to v0.3.2.

## Contents

- 36 added files
- 34 modified files
- 15 paths removed or superseded
- compiled arXiv-style PDF and LaTeX source under `paper/`
- complete replay code, documentation, tests, and release metadata
- portable selected-policy traces in the FULL delta only

## Apply

1. Back up the v0.3.1 repository.
2. Extract this archive over the repository root.
3. Remove every path listed in `DELETED_PATHS.txt`.
4. Run:

```bash
python scripts/verify_release.py
pytest
```

The CODE_PAPER delta excludes `data/raw/` to remain small. Pair it with the separately released `MMALS_CAL_v0_3_2_Selected_Traces.zip`.

The FULL delta includes all seven portable selected traces and is sufficient to reproduce the cross-benchmark replay.
