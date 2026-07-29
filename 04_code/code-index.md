# 程序文件索引

| 问题 | 程序 | 作用 | 输入 | 主要输出 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Q1 | `q1/model/q1_prepare_data.py` | 从官方工作簿整理作图输入 | 原始 XLSX | Q1 response CSV | Python 3.14 已运行 |
| Q1 | `q1/plotting/q1_plot_results.py` | 主效应、权衡和 ANOVA 图 | Q1 CSV | Q1 PDF 图 | Python 3.14 已运行 |
| Q2 | `q2/validation/q2_revision_analysis.py` | 代理模型编码、交叉验证与跨问复核 | 原始数据、Q3/Q4结果 | validation CSV | 语法通过，待独立复现 |
| Q3 | `q3/model/q3_multiobjective_optimization.py` | 分段代理与确定性 Pareto 搜索 | 原始数据 | Pareto 与候选 CSV | 语法通过，待独立复现 |
| Q3 | `q3/model/q3_candidate_algorithm_comparison.py` | 网格与 NSGA-II 比较 | Q3模型 | 算法指标与轨迹 CSV | 语法通过，待独立复现 |
| Q3 | `q3/model/q3_methodology_finalization.py` | 合并参考集、精确 HV 和连续精化 | Q3过程 CSV | 定稿过程 CSV | 语法通过，待独立复现 |
| Q3 | `q3/plotting/q3_plot_results.py` | Pareto、候选和算法比较图 | Q3 CSV | Q3 PDF 图 | Python 3.14 已运行 |
| Q4—Q5 | `q4/model/q45_preference_and_robustness.py` | 权重、偏好与扰动情景基础计算 | Q3 Pareto集 | Q4/Q5过程 CSV | 语法通过，待独立复现 |
| Q4—Q5 | `q4/model/q45_final_revision.py` | 遗憾、风险、敏感性补充计算 | Q3/Q4/Q5过程数据 | 修订 CSV 与草稿 | 语法通过，待独立复现 |
| Q4—Q5 | `q4/model/q45_evidence_boundary_revision.py` | 域内证据边界修订 | Q4/Q5修订数据 | 正式域风险与 SRC 数据 | 语法通过，待独立复现 |
| Q4 | `q4/plotting/q4_plot_results.py` | 权重映射图 | Q4 CSV | Q4 PDF 图 | Python 3.14 已运行 |
| Q5 | `q5/plotting/q5_plot_results.py` | 风险、工况与敏感性图 | Q5 CSV | Q5 PDF 图 | Python 3.14 已运行 |
| 全局 | `common/build_data_index.py` | 生成处理数据逐文件索引 | processed CSV | `file-index.md` | Python 3.14 已运行 |

“语法通过”只证明脚本可被解释器加载，不代表数值结论已经 V1 复核。
