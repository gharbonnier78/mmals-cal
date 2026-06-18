# MMALS-CAL v0.3.2 Paper

[Open the compiled article](./main.pdf)

The canonical article now contains three reviewer-oriented layers in addition to the experimental results:

- `from_initial_gap_analysis_to_v032.tex` - before/after/remaining status, offline-versus-online boundary, context inference versus change detection, two-channel online design, and layer responsibilities;
- `semantic_foundations_and_research_dialogue.tex` - the complete translated semantic and architectural dialogue;
- `annotated_references.tex` - paraphrased abstracts, engineer translations, and the contribution of each reference to MMALS-CAL.

Readable Markdown counterparts are included where applicable.

## Compile from source

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The compiled release article is `paper/main.pdf`. There is intentionally no duplicate root-level `main.pdf` in the repository.
