# Q2 验证

`q2_revision_analysis.py` 用于代理模型编码、交叉验证和跨问复核。强制检查数据切分与泄漏、基线、残差、数值范围、合法域、外推和不确定度。

`q2_q5_reproduction_validation.py` 不导入模型模块，只读取官方 XLSX 和重建 CSV/JSON 并检查 Q2—Q5 接口与不变量。`E-Q2-Q5-REPRO-001` 已通过 19 项检查，当前为 `stage=v1`、`review=pass_with_limits`；外推和物理有效性限制仍见复现报告。
