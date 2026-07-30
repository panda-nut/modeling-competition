# [B] 平行模型程序索引

> 本文件只登记 `[B]` 新增程序，不修改原模型入口。Evidence ID：`E-Q1-Q5-B-ALT-001`。

| 问题 | 程序 | 主要作用 | 主要输出 |
| --- | --- | --- | --- |
| Q1 | `q1/model/q1_effect_analysis_b.py` | 主效应、交互效应和无重复全因子描述性平方和分解 | `q1_*_b.csv` |
| Q1 | `q1/plotting/q1_plot_results_b.py` | 相对偏差、无针肋基线、效应贡献和交互图 | `fig_q1_*_b.pdf/png` |
| Q2 | `q2/model/q2_surrogate_audit_b.py` | 严格嵌套交叉验证、阶数/alpha 稳定性、无针肋插值审计 | `q2_*_b.csv` |
| Q3 | `q3/model/q3_optimization_audit_b.py` | 代理前沿比较、权重连续精化、判据和归一化敏感性 | `q3_*_b.csv` |
| Q4 | `q4/model/q4_preference_audit_b.py` | 权重域、绝对/相对遗憾和胜出分区审计 | `q4_*_b.csv` |
| Q5 | `q5/model/q5_robustness_audit_b.py` | 误差分布、合法域、跨模型遗憾和 Sobol 敏感性 | `q5_*_b.csv` |
| 全局 | `common/build_model_audit_index_b.py` | 生成 `[B]` 数据/图表哈希索引和 JSON 元数据 | `model-audit-index-b.md/json` |

## 运行顺序

```powershell
.venv\Scripts\python.exe 04_code\q1\model\q1_effect_analysis_b.py
.venv\Scripts\python.exe 04_code\q1\plotting\q1_plot_results_b.py
.venv\Scripts\python.exe 04_code\q2\model\q2_surrogate_audit_b.py
.venv\Scripts\python.exe 04_code\q3\model\q3_optimization_audit_b.py
.venv\Scripts\python.exe 04_code\q4\model\q4_preference_audit_b.py
.venv\Scripts\python.exe 04_code\q5\model\q5_robustness_audit_b.py
.venv\Scripts\python.exe 04_code\common\build_model_audit_index_b.py
```

本机此次实际使用 Python 3.14.0 系统解释器完成计算；项目 `.venv` 因当前中文路径启动问题尚未通过，因此上述标准入口仍需在环境修复后复核。
