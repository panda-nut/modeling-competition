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
| `processed/q2/` | 预留Q2代理模型正式处理结果 | Q2建模 | v0 |
| `processed/q3/` | Pareto集、候选方案、算法比较、收敛轨迹 | Q3多目标优化 | draft |
| `processed/q4/` | 权重扫描、代表情景、遗憾和收敛 | Q4偏好分析 | draft |
| `processed/q5/` | 扰动样本统计、灵敏度、CVaR和风险比较 | Q5鲁棒性分析 | draft |
| `processed/validation/` | 编码交叉验证、结构化留出及跨问复核数据 | V1复核 | v1 |

逐文件的行列数、字段和 SHA-256 见
[`processed/file-index.md`](processed/file-index.md)。该索引由
`04_code/common/build_data_index.py` 生成。迁移文件已完成完整性登记，但没有因此
自动获得 `review=pass`；未登记文件不得晋升到 `07_frozen/`。
