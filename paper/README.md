# MMALS-CAL v0.3.2 Paper

[Open the compiled article](./main.pdf)

The article now includes the complete annotated references chapter with, for each cited work:

- a concise paraphrased abstract;
- an engineer-oriented translation;
- the exact contribution to MMALS-CAL;
- implementation status and limitations;
- collective positioning of the bibliography in the MMALS-CAL roadmap.


The article also includes the complete **Semantic Foundations and Research Dialogue** chapter. It preserves the full English translation of the supplied reasoning on:

- the conformal calibration quantile;
- why regime-change detection is foundational in continual learning;
- change probability versus geometric regime proximity;
- direct reuse, warm-start recombination, and new host/route formation;
- the permanent distinction between offline CAL and online CAL;
- a framework-neutral signal contract for auditable CL/RL systems;
- natural mathematical meta-routing versus additional rule boxes;
- the inventory of existing MMALS repositories and exported signals;
- defensible semantics and the role of the MMALS Chronicle.

The chapter source is maintained in both:

- `semantic_foundations_and_research_dialogue.md`;
- `semantic_foundations_and_research_dialogue.tex`.

The annotated-reference chapter source is maintained in both:

- `annotated_references.md` — readable source text;
- `annotated_references.tex` — LaTeX fragment included by `main.tex`.

## Compile from source

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The compiled release article is `main.pdf`. This directory also contains the LaTeX source, bibliography, annotated-reference sources, and publication figures used by the paper.
