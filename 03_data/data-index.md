# 数据文件索引

> 本索引记录数据用途和当前位置。迁移前已有结果尚未完成新冻结流程，统一标记为 `review=pending`。

## 原始数据

| 路径 | 作用 | 来源 | 修改规则 |
| --- | --- | --- | --- |
| `raw/apmcm-2026-b-appendix-2-data.xlsx` | Q1—Q5结构参数与无量纲响应的官方数据 | 题目附件2 | 只读 |

## 处理与模型输出

| 目录 | 主要内容 | 主要用途 | 当前阶段 |
| --- | --- | --- | --- |
| `processed/q1/` | 方差/主效应贡献 | Q1机理趋势分析 | draft |
| `processed/q2/` | 预留Q2代理模型正式处理结果 | Q2建模 | v1 / pass_with_limits |
| `processed/q3/` | Pareto集、候选方案、算法比较、收敛轨迹 | Q3多目标优化 | v1 / pass_with_limits |
| `processed/q4/` | 权重扫描、代表情景、遗憾和收敛 | Q4偏好分析 | v1 / pass_with_limits |
| `processed/q5/` | 扰动样本统计、灵敏度、CVaR和风险比较 | Q5鲁棒性分析 | v1 / pass_with_limits |
| `processed/validation/` | 编码交叉验证、结构化留出、跨问复核与复现证据 | V1复核 | v1 / pass_with_limits |

## 关键 JSON 产物

| 路径 | 生成程序 | 作用 | 状态 |
| --- | --- | --- | --- |
| `processed/q4/q45_summary.json` | `q45_preference_and_robustness.py` | Q4/Q5 主计算的偏好、结构和工况摘要 | v1 / pass_with_limits |
| `processed/q4/q45_revision_summary.json` | `q45_final_revision.py` | 修订风险和偏好摘要 | v1 / pass_with_limits |
| `processed/validation/q5/q5_worst_case_summary.json` | `q2_revision_analysis.py` | 跨问最坏情形重优化摘要 | v1 / pass_with_limits |
| `processed/validation/reproduction/q2_q5_reproduction_evidence.json` | `q2_q5_reproduction_validation.py` | 环境、命令、输入哈希和检查结论 | v1 / pass_with_limits |

逐文件的行列数、字段和 SHA-256 见
[`processed/file-index.md`](processed/file-index.md)。该索引由
`04_code/common/build_data_index.py` 生成。迁移文件已完成完整性登记，但没有因此
自动获得 `review=pass`；未登记文件不得晋升到 `07_frozen/`。Q2—Q5 当前复现
证据见 `processed/validation/reproduction/q2_q5_reproduction_report.md`，其结论为
`pass_with_limits`，不等同于冻结批准。
