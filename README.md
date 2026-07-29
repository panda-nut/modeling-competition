# 数学建模项目仓库

本仓库用于管理题面、文献、数据、程序、图表、演示稿、冻结快照、论文参考结果和最终提交材料。当前项目分支为 `practice/apmcm-2026-b`，当前机器标识为 `[A]`。

AI Agent 开始工作前必须完整阅读 [AGENTS.md](AGENTS.md)。`[A][B][C]` 只标识执行提交或推送的机器，不表示团队职责。

## 当前结构

| 目录 | 中文用途 | 主要入口 |
| --- | --- | --- |
| `00_progress/` | 进度与模型总览 | `progress-log.md`、`model-map.md` |
| `01_problem/` | 官方题面与可读文本 | `README.md` |
| `02_references/` | 文献、索引与引用 | `references-index.md` |
| `03_data/` | 原始数据与处理 CSV | `README.md` |
| `04_code/` | 建模、验证和绘图程序 | `README.md` |
| `05_figures/` | 工作阶段图表 | `README.md` |
| `06_drafts/` | 每问演示性 TEX/PDF | `README.md` |
| `07_frozen/` | 经确认的冻结快照 | `README.md` |
| `08_results/` | 论文写作参考结果 | `results-index.md` |
| `09_submission/` | 正式提交材料 | `submission-checklist.md` |

## 工作链

```text
题面与文献
→ 原始数据
→ 处理 CSV
→ 建模/验证程序
→ 绘图程序读取 CSV
→ 演示性论文
→ 复核
→ 07_frozen 冻结
→ 08_results 晋升
→ 09_submission 正式提交
```

工作进度、技术阶段和复核结论是三套独立字段：

| 类别 | 允许值 |
| --- | --- |
| 工作进度 | `planned`、`in_progress`、`completed`、`blocked` |
| 技术阶段 | `v0`、`v1`、`draft`、`frozen` |
| 复核结论 | `pending`、`pass`、`pass_with_limits`、`reject` |

正式结果只能从 `07_frozen/` 晋升到 `08_results/`。未经冻结的过程 CSV、探索图和演示稿不能作为论文正式结论。
