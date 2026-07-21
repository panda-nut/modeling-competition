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

分支表示一次具体任务或阶段开发，不作为长期文件分类。`main` 只保存团队 SOP、公共模板和工具，以及已经归档的最终成果。

| 分支模式 | 用途 | 合并目标 |
| --- | --- | --- |
| `main` | SOP、模板、公共工具、已完成项目 | — |
| `practice/<题目>` | 训练题、课程作业、模拟赛 | `main`（完成归档后） |
| `contest/<题目>` | 正式竞赛项目 | `main`（比赛结束且允许归档后） |
| `feature/<模块>` | 单项开发，如模型、验证或论文 | 对应项目分支 |
| `fix/<问题>` | 修复代码、公式、数值或图表问题 | 对应项目分支 |

当前推荐的训练题协作关系：

```text
main
└── practice/apmcm-2026-b
    ├── feature/q1-mechanism
    ├── feature/q2-surrogate-review
    └── feature/paper-framework
```

正式国赛可按同样方式建立 `contest/cumcm-2026-b`，并从它创建 `feature/model-v0`、`feature/model-validation` 与 `feature/paper-draft`。每个阶段经 Pull Request 审核后合并回项目分支；项目完成后合并或归档至 `main`，例如创建标签 `apmcm-2026-b-v1.0`。

请避免含义不明的分支名，如 `final`、`final-v2` 或 `really-final`；使用 `feature/q2-cross-validation`、`fix/q3-pareto-normalization` 这类可读名称。

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
