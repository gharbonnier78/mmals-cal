PYTHON ?= python
CONFIG := configs/cross_benchmark_v0.3.2.json

.PHONY: replay figures verify test paper all
replay:
	PYTHONPATH=src $(PYTHON) scripts/run_cross_benchmark_replay.py --config $(CONFIG) --output-dir results
figures:
	$(PYTHON) scripts/reproduce_figures.py --results-dir results --output-dir figures
verify:
	$(PYTHON) scripts/verify_release.py
test:
	PYTHONPATH=src pytest -q
paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
all: replay figures verify test paper
