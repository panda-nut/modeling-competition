# LaTeX build guide

Install XeLaTeX and latexmk. From the repository root, compile a document with:

```powershell
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=.latex-build/q1 08_results/q1/q1-physical-model.tex
```

After success, copy the generated PDF from the build directory beside its TEX source with the same basename. Keep only the TEX/PDF pair in Git; `.latex-build/` and auxiliary files are ignored. On failure, retain any existing PDF and fix the first reported TEX error before retrying.
