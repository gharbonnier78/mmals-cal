# MMALS-CAL v0.3.2

## Regime-Aware Conformal Evidence Verification for Continual-Learning Systems

MMALS-CAL is a standalone companion verification layer within the broader MMALS research program. The MMALS Chronicle describes the learning architecture - inferred context, routing, host specialization, and route-function memory. MMALS-CAL does not train MMALS. It verifies whether evidence exported by a final-checkpoint run is calibrated, appropriate for the current regime, compact enough to support action, and reported without overclaiming.

> **Fresh calibration restores coverage; it does not manufacture competence.**

## Release status

Version 0.3.2 is an **offline, final-checkpoint, seven-benchmark replay**. It is not yet an online change-point detector or a runtime adaptive calibration controller.

The release includes:

- the complete replay implementation for all five calibration strategies;
- all seven compressed filtered traces under `data/raw/`;
- deterministic 25% calibration / 75% deployment splitting;
- derived metrics, figures, protocol checks, and claim checks;
- an executed reproduction notebook;
- a compiled arXiv-style article and LaTeX source;
- explicit documentation of the future online components A-D.

## Reproduce the complete analysis

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/run_cross_benchmark_replay.py \
  --config configs/cross_benchmark_v0.3.2.json \
  --output-dir results/reproduced

python scripts/reproduce_figures.py \
  --results-dir results/reproduced \
  --output-dir figures/reproduced

python scripts/verify_release.py
PYTHONPATH=src pytest -q
```

The replay is portable because the seven selected-policy traces are included. The much larger original MMALS evidence archives are not included; they are listed by exact filename and checksum in `data/external_source_locations.csv`. The final column is intentionally blank so a Drive or archive path can be added later without changing the scientific results.

## Main evidence

- Fresh oracle-regime calibration reaches approximately the 0.90 aggregate marginal-coverage target on all seven benchmarks.
- On CORe50, coverage falls from **0.9011** under fresh oracle-regime calibration to **0.7255** when those calibrators are selected by inferred context: a **17.6 percentage-point loss**.
- SplitCIFAR100 obtains 0.9062 fresh coverage but only 9.44% singleton ACTION.
- CORe50 obtains 0.9011 fresh coverage with a mean 28.67-label set and only 0.15% singleton ACTION.
- The singleton gate is a conservative baseline for autonomous single-label actionability, not a universal deployment policy or the maximum achievable action rate.

## Repository map

- `src/mmals_cal/`: reusable conformal, split, replay, metrics, and verification code
- `scripts/`: complete CLI replay, figure reproduction, release verification, extraction helpers
- `configs/`: portable experiment configuration
- `data/raw/`: seven compressed selected-policy traces
- `data/`: selected-trace and external-source registries
- `results/`: release evidence tables
- `figures/`: reproduced figures
- `paper/`: compiled article and LaTeX source
- `docs/`: conceptual, engineering, child-friendly, and reproducibility documentation
- `tests/`: unit and release tests

## Scientific boundary

MMALS-CAL is empirical and statistical evidence verification, not formal verification and not a proof of universal safety. Its coverage statement is marginal and depends on exchangeability between calibration and deployment observations. SplitCIFAR10, SplitCIFAR100, and CORe50 use frozen small-CNN feature representations inherited from the source runs, so their results are conditional on those representations.

## Citation

See `CITATION.cff` and the article in `paper/main.pdf`.
