# 正式整合论文工作区

`main.tex` 是可编辑源，`main.pdf` 是同名预览。所有正式数字必须来自 `08_results/results-index.md` 中已经晋升的结果包；当前论文仍属于迁移保留稿，不因进入本目录而自动完成结果复核。

编译：

```powershell
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=.latex-build/main main.tex
```

只编辑 TEX；编译失败时保留现有 PDF。辅助文件写入 `.latex-build/`，不得提交。
