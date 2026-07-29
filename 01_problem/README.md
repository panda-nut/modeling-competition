# 题面与官方附件

## 读取顺序

1. 优先阅读 `extracted/` 中的 Markdown 文本以定位问题；
2. 遇到公式、表格、结构图、页码或歧义时回看 `source/` 原 PDF；
3. 数据附件在 `03_data/raw/`，不得从本地重复副本读取。

## 文件

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `source/apmcm-2026-b-problem.pdf` | APMCM 2026 B 题官方题面 | 原始文件，只读 |
| `source/apmcm-2026-b-appendix-1-structure.pdf` | 芯片歧管式微通道结构参数说明 | 原始文件，只读 |
| `extracted/apmcm-2026-b-problem.md` | 题面可搜索文本 | 从原 PDF 提取，需结合原 PDF 核验 |
| `extracted/apmcm-2026-b-appendix-1-structure.md` | 附件1可搜索文本 | 从原 PDF 提取，结构图需回看原 PDF |

原始 Excel 数据位于 `03_data/raw/apmcm-2026-b-appendix-2-data.xlsx`。
