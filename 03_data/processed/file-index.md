# 处理数据逐文件索引

> 由 `04_code/common/build_data_index.py` 生成。SHA-256 用于迁移和复现核对；
> 本索引不等同于技术复核通过或冻结批准。

| 路径 | 数据行 | 列数 | 字段 | SHA-256 |
| --- | ---: | ---: | --- | --- |
| `q1/q1_anova_contributions.csv` | 21 | 4 | 响应、效应、SS、贡献率 | `472871d0dff0da24584fd8ef4abf20b5b8166265652cdd72a7c4917d51fc69f7` |
| `q1/q1_response_data.csv` | 84 | 7 | id、a、b、N、R、P、U | `e8e93605d705644ca690df43577bf2fee1877576d3ef8834520b0317f91d77d9` |
| `q3/q3_algorithm_metrics.csv` | 23 | 8 | method、run、points、HV、IGD_plus、Spacing、seconds、evaluations | `56da37305054c2d4f262d1a737e2e53b62fcee7a64d61cee5e5b6d7e6c7f0f80` |
| `q3/q3_algorithm_metrics_exact.csv` | 23 | 7 | method、run、points、HV、IGD_plus、Spacing、evaluations | `8f8de04543a14c0cd8cda9aee08951914ff288a31a3037ab70627223283ecb75` |
| `q3/q3_compromise_candidates.csv` | 6 | 9 | 方案、a、b、N、R、P、U、C_AT、C2 | `8a11d613bb820bdfd37d94fd1edf47719fa74f6e4a32a4c05a2ed6b481588e8f` |
| `q3/q3_local_refinement.csv` | 6 | 8 | 方案、a、b、N、R、P、U、C_AT | `d817165ab8066cc2018d49a1559992328b4d0d8226e9e3af3d6cdbd8388a157c` |
| `q3/q3_nsga2_runs.csv` | 2159 | 7 | seed、a、b、N、R、P、U | `43a94e85a539bc79f9a0b7a197f109407bd712f418348c05d9cabdddc4679152` |
| `q3/q3_nsga2_trace.csv` | 600 | 6 | seed、N、generation、min_R、min_P、min_U | `44fff6ef47f906c3035b5ddc3d686ae58681a7065bdb1e0a2d6de389a7906c9e` |
| `q3/q3_pareto_global.csv` | 16858 | 6 | a、b、N、R、P、U | `bbaef95706c7efb01c275894065cf3405b075b9639660a9933307f282569f60a` |
| `q3/q3_pareto_nsga2.csv` | 1628 | 6 | a、b、N、R、P、U | `6d4c6875891f8f79fe4aae71ff14a5194d9febf11325dd8aeaac4156687781db` |
| `q3/q3_pareto_reference_merged.csv` | 18183 | 6 | a、b、N、R、P、U | `5507968a60a2980998cb23a4818957293ca5156d37fb73e79d49776ed1b48ecc` |
| `q3/q3_payoff_matrix.csv` | 3 | 4 | 、R、P、U | `81fa9021c4c6be26162457f62223d60d84256f442f1c8b1345505426103867e7` |
| `q4/q4_convergence.csv` | 3 | 8 | H、权重数、pi_N2、pi_N4、pi_N6、pi_N8、pi_N10、mean_G | `72556b2b7b9e884008b0367c103009b58742464845f3de0d168e040e3a6c218b` |
| `q4/q4_convergence_corrected.csv` | 3 | 8 | H、权重数、a、b、N、最大遗憾、平均遗憾、P95遗憾 | `69b8d14f14d698553afb423b8ec620c0fa53a6f2af3abc0ef25b392e2fe51285` |
| `q4/q4_regret_comparison.csv` | 6 | 10 | 方案、a、b、N、R、P、U、最大遗憾、平均遗憾、P95遗憾 | `3cc64e03921107fb309f7db6e7f685fc8918164d4531373eda3b08636f3ce96c` |
| `q4/q4_representative_scenarios.csv` | 5 | 11 | w_R、w_P、w_U、a、b、N、R、P、U、G、场景 | `182f8c4a194aac4c8ca05ebe2c1f28c5051e40a573e4fe0e42ee527ce7bd18aa` |
| `q4/q4_representative_scenarios_corrected.csv` | 5 | 11 | w_R、w_P、w_U、a、b、N、R、P、U、G、场景 | `30a78c4866bd0bddf9f5ac756429a1f330b1cb3cf137d8e23c6673299e0d05a8` |
| `q4/q4_weight_scan_H50.csv` | 1326 | 10 | w_R、w_P、w_U、a、b、N、R、P、U、G | `e18951d6e7ce04ce6f0138dcde4f269b5c07c725961657efc10e1b046ca79fee` |
| `q4/q4_weight_share.csv` | 5 | 2 | N、权重区域占比 | `cf3306ac86f0c632905b1236617f5c450a22ca2a515c553c6a622a9cd287ccce` |
| `q5/q5_formal_domain_risk.csv` | 2 | 9 | 方案、a、b、N、名义评分、均值、标准差、Q95、CVaR95 | `f6e3ceaf18eba6d648d27671902393c9d589321b06f80dd613fd2d60fea5b44a` |
| `q5/q5_local_sensitivity.csv` | 6 | 4 | 设计、响应、\|dz/dã\|、\|dz/db̃\| | `1b77c998727d208435e5d8909b26ca3c126e9d099ff68cb970cefa08a24582a8` |
| `q5/q5_operation_design_comparison.csv` | 6 | 17 | 情景、U模型、alpha_P、theta_R、m_R、m_U、sm_lo、sm_hi、sq_lo、sq_hi、a、b、N、最优CVaR、结构鲁棒CVaR、差额、相对风险增幅 | `0426235abba7808b802adf82410584b5d8254574151f84d985910514cbe5e6a0` |
| `q5/q5_operation_scenarios.csv` | 6 | 23 | 机制、U模型、a、b、N、CVaR95_Cop、Cmax、Cnom、mean_Theta、sd_Theta、q95_Theta、cvar95_Theta、max_Theta、mean_P、sd_P、q95_P、cvar95_P、max_P、mean_U、sd_U、q95_U、cvar95_U、max_U | `a566bee6280e11883fa3751648fa500fdfd1a08d062e98aa00efd1b40a047531` |
| `q5/q5_operation_src_S2A.csv` | 4 | 5 | 扰动因素、Theta_R、P、U、C_op | `24d62e90ac5e9df6510f13fcad8f05f9c54a833a67eae9fc03ddbd2a20e4a133` |
| `q5/q5_signed_src.csv` | 6 | 5 | 、热目标、P、U、综合评分 | `5f267922bcfdc2654cb4224ddfd5b6873d167e38c75d32c69b055d21f093e026` |
| `q5/q5_src_r2.csv` | 2 | 5 | 模型、热目标、P、U、综合评分 | `f66eda178d203b952c87610982a1396919eade7d30655ac160dd7f77180f9abd` |
| `q5/q5_structure_layer_optima.csv` | 5 | 7 | a、b、N、R、P、U、CVaR95 | `0ff65fd3d92192bb29979874c4bfd8cd2c05963cb723677eca51da2629af76db` |
| `q5/q5_structure_propagation.csv` | 4 | 26 | 方案、a、b、N、C_nom、CVaR95_C、C_max、mean_R、sd_R、q95_R、cvar95_R、max_R、mean_P、sd_P、q95_P、cvar95_P、max_P、mean_U、sd_U、q95_U、cvar95_U、max_U、D_R、D_P、D_U、D_rms | `6aa612411021e5f58c883e36b5c07e17bc516cf16bdf6f7bf334f018bc28cc58` |
| `q5/q5_structure_risk_comparison.csv` | 5 | 11 | 方案、a、b、N、C_nom、均值、标准差、Q95、CVaR95_L20000、CVaR95_L40000、收敛差 | `e95fb0593c0b1a8e3fbe719a169e2a88a2ab5520e6531f791fc450b0771fa275` |
| `q5/q5_structure_src.csv` | 2 | 5 | 扰动因素、R、P、U、C_str | `084b7e48907ec37c2254c43cf294e0fd063769e7bf4b3b31b1d1450bc9a2ae5e` |
| `validation/q2/q2_encoding_cv.csv` | 4 | 4 | 编码、R_NRMSE、P_NRMSE、U_NRMSE | `7c216356bd90d10b78572ac171d115143c927d6a1b8ba3111181795e443438e1` |
| `validation/q2/q2_structured_holdout.csv` | 3 | 3 | 响应、组合留出NRMSE、最差组合NRMSE | `5053769ba25694fdccd4a1f532d3cc73b000e541199346945e2d04da9135989c` |
| `validation/q3/q3_model_reoptimization.csv` | 7 | 8 | 模型、a、b、N、R、P、U、评分 | `77cdd8cc14c59a5d58c0b5b3e2d40827c378b6976b6816914333af4e2524aa31` |
| `validation/q4/q4_preference_sensitivity.csv` | 4 | 7 | 权重域、判据、权重数、a、b、N、最大遗憾 | `80553191146a6b0412ab220f4ac376f392450347ec6d6eb1c3eb6e4c2a61cc2b` |
| `validation/q5/q5_operation_pressure_test.csv` | 4 | 5 | candidate、min_CVaR、max_CVaR、max_score、max_regret | `295c8cf821cd93d78aeea6da0fe3ca1824309b0f8960f42b82dab4461a3eba63` |
| `validation/reproduction/q2_q5_reproduction_checks.csv` | 19 | 3 | 检查项、通过、说明 | `e08befda3e55a5215a2bbe11c8bf4dc6f826bbc6ab830275b934958e240c6b31` |

重新生成：

```bat
.venv\Scripts\python.exe 04_code\common\build_data_index.py
```
