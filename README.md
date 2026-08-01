# 数学建模团队通用基线

`main` 保存团队 SOP、AI Agent 规则、环境与依赖声明、通用模板和经过冻结后沉淀的经验；不作为某一题目的日常工作区。训练、比赛和课程项目应从 `main` 创建对应项目分支，再按下列结构落地题面、数据、代码和结果。

AI Agent 开始工作前必须完整阅读 [AGENTS.md](AGENTS.md)。`[A][B][C]` 只标识执行提交或推送的机器，不表示团队职责；人类协作流程见 [SOP.md](SOP.md)。

## 自动反馈工作流同步

`.github/workflows/welcome.yml` 是仓库的自动反馈工作流。`main` 与每个需要使用自动反馈的项目分支应保留内容一致的副本。

- 从 `main` 创建新分支时，该工作流会随分支基线自动带入；创建后应确认文件存在。
- 若新分支基于其他分支或外部基线创建，首次推送前必须从 `main` 同步该文件，并仅暂存 `.github/workflows/welcome.yml`。
- 同步或更新前先获取目标远程分支快照，比较该精确路径；若存在未整合变更，展示差异与时间戳后等待处理决定。
- 除非用户明确要求调整工作流行为，不得在项目分支中改写该文件；后续新分支的同步以 `main` 中的版本为准。

## 项目分支结构

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

## 项目工作链

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

正式结果只能从 `07_frozen/` 晋升到 `08_results/`。未经冻结的过程 CSV、探索图和演示稿不能作为论文正式结论。题目专属代码、数据、文献、图表、草稿和提交件应留在对应项目分支；只有冻结后的通用经验、模板或已授权归档材料才回流 `main`。
