# MMALS-CAL v0.3.2 Paper

[Open the compiled article](./main.pdf)

The article now includes the complete annotated references chapter with, for each cited work:

- a concise paraphrased abstract;
- an engineer-oriented translation;
- the exact contribution to MMALS-CAL;
- implementation status and limitations;
- collective positioning of the bibliography in the MMALS-CAL roadmap.

The chapter source is maintained in both:

- `annotated_references.md` — readable source text;
- `annotated_references.tex` — LaTeX fragment included by `main.tex`.

## Compile from source

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The compiled release article is `main.pdf`. This directory also contains the LaTeX source, bibliography, annotated-reference sources, and publication figures used by the paper.
