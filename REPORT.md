# MMALS-CAL v0.3.2 - Submission Patch Report

## Changes from v0.3.1

1. Quantifies the CORe50 oracle-to-context-selected loss in the abstract: 0.9011 to 0.7255, or 17.6 percentage points.
2. Duplicates the frozen small-CNN caveat in the abstract and limitations.
3. Defines the singleton gate as a conservative autonomous single-label baseline, not a universal deployment policy.
4. Makes the paper standalone relative to the MMALS Chronicle while preserving companion provenance.
5. Includes the complete replay implementation and all seven filtered traces.
6. Adds English documentation for components A-D and the conformal calibration quantile.
7. Adds a portable external-source registry for original archives omitted due to size.

## Reproduction status

- 7 benchmarks
- 250,000 selected-policy observations
- 62,500 reserved calibration observations
- 187,500 deployment observations
- 5 calibration strategies
- full replay code included
- 7/7 filtered traces included
- original upstream archives not required for replay

## Scientific status

MMALS-CAL v0.3.2 is an offline evidence-verification and operational-readiness replay harness. It is not yet an online regime-change detector or runtime adaptive calibration controller.

## Reviewer-orientation consolidation

The canonical paper now includes a dedicated section that maps the initial A-D gap analysis to the current v0.3.2 implementation. It explicitly distinguishes context inference from temporal change detection, explains why the label-dependent LAC nonconformity score cannot be the sole early-warning signal, defines a future label-free plus delayed-label two-channel design, and assigns responsibilities across MMALS/RC2O, Geometry-MMALS, offline and online CAL, TPUT/STRAT-Q, and the Verification Stack.
