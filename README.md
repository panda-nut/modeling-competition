# Mathematical Modeling Team Workflow

三人数学建模团队的训练、课程作业与竞赛协作仓库，覆盖审题、建模、编程复现、技术复核、论文写作和成果归档的完整流程。

> 正式比赛期间请将仓库设为 **Private**；比赛后是否公开，应以竞赛规则、数据版权和团队共同决定为准。

## 团队工作流

团队采用“共同破题 → 模型 V0 → 技术复核 V1 → 论文成文 → 最终审核”的滚动协作：

1. 三人共同审题、拆解问题并确定总体路线。
2. 建模负责人形成全题架构、候选模型和各小问 V0。
3. 技术复核负责人独立复现程序，审计数据与假设，补充验证并筛选图表。
4. 论文负责人同步维护论文框架，将已通过复核的结果写入正文。
5. 三人交叉审核，统一图表、冻结结果、归档代码并提交。

## 分支策略

分支表示一次比赛或项目，而不是成员、题目小问或阶段任务。`main` 只保存团队 SOP、公共模板和工具，以及已经归档的最终成果；一个项目只使用一个项目分支。

| 分支模式 | 用途 | 合并目标 |
| --- | --- | --- |
| `main` | SOP、模板、公共工具、已完成项目 | — |
| `practice/<题目>` | 训练题、课程作业、模拟赛 | `main`（完成归档后） |
| `contest/<题目>` | 正式竞赛项目 | `main`（比赛结束且允许归档后） |
| `coursework/<项目>` | 课程作业 | `main`（完成归档后） |

当前训练项目为 `practice/apmcm-2026-b`。`[A]`、`[B]`、`[C]` 是操作人编码，不绑定固定角色；每次对话开始须确认实际操作人。当前 Agent 已确认使用 `[A]`，因此其本地操作与提交一律使用 `[A]`。项目角色依目录责任区分工作，项目结束后使用标签（如 `apmcm-2026-b-v1.0`）标记正式版本。

```text
main
└── practice/apmcm-2026-b
```

正式国赛可建立 `contest/cumcm-2026-b`，课程作业可建立 `coursework/<项目名>`。每个项目完成后合并或归档至 `main`，例如创建标签 `apmcm-2026-b-v1.0`。

请避免含义不明的分支名，如 `final`、`final-v2` 或 `really-final`；也不保留 `develop`、`release` 等长期分支。

## 项目目录

```text
.
├─ README.md                       # 本说明与协作约定
├─ SOP.md                          # 可执行的团队 SOP
├─ .gitignore                      # 忽略原始资料、AI 中间产物和本地缓存
├─ templates/                      # paper、problem-card、model-review、final-checklist
├─ common/                         # plotting、validation、utils
└─ projects/<项目名>/              # 仅在对应项目分支中创建
   ├─ 00_problem/                  # 题面与可公开资料索引
   ├─ 01_architecture/             # 路线、假设与任务拆解
   ├─ 02_data/                     # 小型可复现数据与数据说明
   ├─ 03_q1/ ... 07_q5/            # 分问模型、代码与结果
   ├─ 08_figures/                  # 审核通过的出图脚本与最终图表
   ├─ 09_paper/                    # 论文源文件与参考文献
   └─ 10_final/                    # 可提交的冻结版本
```

## 提交信息

```text
[MODEL] 完成Q2代理模型V0
[REVIEW] 补充Q2交叉验证与外推检验
[PAPER] 完成Q2论文初稿
[FIGURE] 重绘Pareto前沿
[FIX] 修正Q3归一化范围
[FINAL] 冻结Q3结果
```

## AI 与大文件管理

仓库只提交能让队友复现和审核的源代码、配置、数据说明、最终图表和冻结成果。题目附件、文献 PDF、AI 对话记录、模型缓存、批量试验、临时导出和本地构建物默认不推送，具体规则见 [`.gitignore`](.gitignore)。如某份数据或产物确需共享，请先压缩/脱敏并在项目 README 中说明来源、版本、用途与获取方式；大文件建议使用 Git LFS 或受权限控制的云盘链接，而不是直接提交。

AI 可自动进行本地读写、测试与本地提交；所有远端上传、远端分支删除、Release 和仓库设置修改均由团队成员人工确认执行，且不允许 force push。完整 AI 上下文、角色边界和上传流程见 [AGENTS.md](AGENTS.md)。

## Current project: APMCM 2026 Problem B

- Project branch: `practice/apmcm-2026-b`
- Workflow: the Modeling Lead produces model V0; the Validation Lead independently validates it; the Paper Lead writes the paper; the designated technical reviewer performs final review. Operator codes are recorded separately.

| Role | Operator assignment | Primary directories |
| --- | --- | --- |
| Modeling Lead | designated per task | `01_architecture/`, `02_references/`, `04_code/`, `06_figures/` |
| Validation Lead | designated per task | `03_data/`, `05_validation/`, `08_results/` |
| Paper Lead | designated per task | `07_paper/`, `09_submission/` |

`07_paper/main.tex` is maintained by the designated Paper Lead. The Modeling Lead and Validation Lead place paper material in their respective `paper-notes/` directories and do not overwrite `main.tex`. `08_results/final-results.md` is the only source of formal numeric values. Team members must not edit the same file at the same time.

Before work: `git switch practice/apmcm-2026-b` then `git pull --rebase origin practice/apmcm-2026-b`. Before committing: run `git status`, stage specific paths, and use the confirmed operator code (currently `[A]`), e.g. `[A][REVIEW] validate surrogate model`; then manually run a rebase pull and normal push. AI may make local changes and commits only; a team member must manually push, and force push is prohibited.

## Project directory status

| Directory | Owner | Purpose | Current status |
| --- | --- | --- | --- |
| `00_problem` | [A] | immutable problem sources | imported |
| `01_architecture` | [A] | architecture and decisions | in progress |
| `02_references` | [A] | traceable literature | planned |
| `03_data` | [B] | raw and processed data | raw imported |
| `04_code` | [A] | Q1–Q5 programs | partial migration |
| `05_validation` | [B] | checks and reviews | partial migration |
| `06_figures` | [A] | formal figures | planned |
| `07_paper` | [C] | LaTeX manuscript | draft migrated |
| `08_results` | [B] | results registry | in progress |
| `09_submission` | [C] | delivery files | planned |

Empty directories use substantive README, templates, or indexes rather than only `.gitkeep`. Such files do not imply a model is complete; task status is governed by the architecture records and `08_results/final-results.md`.

## LaTeX result documents

Formal stage results use same-name `.tex + .pdf` pairs. TEX is the editable source and AI's default reading target; PDF is the human preview and must be regenerated after TEX changes. Intermediate compilation files are ignored, while formal TEX/PDF pairs are tracked. The complete paper is `07_paper/main.tex` / `07_paper/main.pdf`; result documents live in `08_results/`; `08_results/final-results.md` remains the sole formal numerical registry.

| Document | TEX source | PDF preview | Owner | Status |
| --- | --- | --- | --- | --- |
| Q1 physical model | `08_results/q1/q1-physical-model.tex` | `08_results/q1/q1-physical-model.pdf` | [A] | imported; not revalidated |
| Q2 surrogate model | `08_results/q2/q2-surrogate-model.tex` | `08_results/q2/q2-surrogate-model.pdf` | [A]/[B] | imported; not revalidated |
| Q3 optimization | `08_results/q3/q3-multi-objective-optimization.tex` | `08_results/q3/q3-multi-objective-optimization.pdf` | [A]/[B] | imported; not revalidated |
| Q4–Q5 combined analysis | `08_results/q4-q5/q4-q5-robustness-analysis.tex` | `08_results/q4-q5/q4-q5-robustness-analysis.pdf` | [A]/[B] | combined source; split deferred |
| Full paper draft | `07_paper/main.tex` | `07_paper/main.pdf` | [C] | imported draft |

## CSV data management

CSV files preserve important program-to-paper evidence. Raw inputs are read-only in `03_data/raw/`; reproducible transformations live in `03_data/processed/`; model process data live in `08_results/intermediate/`; review evidence lives in `05_validation/`; only [B]-validated formal outputs may enter `08_results/final/`. [C] does not alter formal numeric CSV, and formal paper values remain governed by `08_results/final-results.md`.
