# MMALS-CAL v0.3.2 - Submission Patch Report

<p align="center">
  <a href="./paper/main.pdf">
    <img src="https://img.shields.io/badge/Open-Article-0B5FFF?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" alt="Open PDF">
  </a>
</p>

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
