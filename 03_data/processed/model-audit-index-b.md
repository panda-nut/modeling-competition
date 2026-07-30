# [B] 平行模型产物索引

> Evidence ID：`E-Q1-Q5-B-ALT-001`；阶段：`v0`；复核：`pending`。本索引不改变原主模型及其正式状态。

## 数据文件

| 问题 | 路径 | 行 | 列 | 字段 | SHA-256 | 生成程序 |
| --- | --- | ---: | ---: | --- | --- | --- |
| Q1 | `03_data/processed/q1/q1_effect_contributions_b.csv` | 21 | 8 | response、effect、sum_of_squares、contribution_ratio、degrees_of_freedom、analysis_scope、residual_df、significance_test_allowed | `0146e2571acc3c64a77ab94e89299767b44c248f18a0721ced9cce4a5a0bc1bc` | `04_code/q1/model/q1_effect_analysis_b.py` |
| Q1 | `03_data/processed/q1/q1_interaction_effects_b.csv` | 168 | 8 | response、factor_first、factor_second、level_first、level_second、cell_mean、interaction_effect、sample_count | `85e4f481dcd02069d40c0f70d36ead53d8abf63829b362aae36a3e50378059cd` | `04_code/q1/model/q1_effect_analysis_b.py` |
| Q1 | `03_data/processed/q1/q1_main_effects_b.csv` | 39 | 7 | response、factor、level、marginal_mean、overall_mean、relative_deviation_pct、sample_count | `bbefaf5f559ff89f46a89a9697ce10879d9c3c4aa1340309246a5fc06b953026` | `04_code/q1/model/q1_effect_analysis_b.py` |
| Q2 | `03_data/processed/q2/q2_alpha_stability_b.csv` | 44 | 5 | response、degree、alpha、selection_count、selection_share | `c15ce762d624780dd60ed3775776e72b21e2df25ed57cb194f6c933df1d4ebdb` | `04_code/q2/model/q2_surrogate_audit_b.py` |
| Q2 | `03_data/processed/q2/q2_baseline_interpolation_audit_b.csv` | 4009 | 9 | method、b、R、P、U、dominated_by_pin_pareto、points、dominated_points、minimum_dominance_margin | `d92b2233c737afbfc1a59b15fee6d9543164000ec7e6f3d2c7eb7058d2ad3fdb` | `04_code/q2/model/q2_surrogate_audit_b.py` |
| Q2 | `03_data/processed/q2/q2_nested_cv_folds_b.csv` | 450 | 9 | response、degree、outer_fold、outer_repeat、test_size、selected_alpha、rmse、nrmse、max_absolute_error | `49018fa2d9b65b945f4d24e6707f10387c4ea5107b8dc6bc2ea69101bcc28170` | `04_code/q2/model/q2_surrogate_audit_b.py` |
| Q2 | `03_data/processed/q2/q2_nested_model_comparison_b.csv` | 9 | 9 | response、degree、nrmse_mean、nrmse_std、nrmse_max、max_absolute_error、alpha_median、alpha_min、alpha_max | `8bb6d03595129ef7838226cf626ef2659af81e8e2e582495d9e6af421f18a48e` | `04_code/q2/model/q2_surrogate_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_adaptive_pareto_b.csv` | 231 | 13 | weight_id、w_R、w_P、w_U、a、b、N、R、P、U、score、optimizer_success、optimizer_method | `58ffc9f0ed6d4df425d7a1aee81612180bcb76b195b71c15a6dad8fa0a32818f` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_cross_model_candidate_scores_b.csv` | 21 | 9 | candidate_source_model、evaluation_model、a、b、N、R、P、U、equal_weight_score | `bff72a31539f223afe76596d9d5b36a114aa45c3a10e7264918880ac3ddffc4e` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_decision_criteria_comparison_b.csv` | 3 | 8 | criterion、a、b、N、R、P、U、criterion_value | `4d6210f9c18c02c2a816094fac3a81da86f4f7ae5f92883839f95097496961b1` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_grid_convergence_b.csv` | 2 | 4 | method、points、hypervolume、new_refined_points_kept | `b516d095d2815c50f593d365bef1f60d413f5be4bae057eea06b3cfc927c23c5` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_normalization_sensitivity_b.csv` | 27 | 10 | scale_R、scale_P、scale_U、a、b、N、R、P、U、score | `325de7b6654fdfb4fd1336604362d41d62f6c52394d13e935e796627420a8b0b` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q3 | `03_data/processed/q3/q3_surrogate_front_comparison_b.csv` | 3 | 5 | model、pareto_points、hypervolume、union_igd、best_equal_weight_score | `609c9e41d6fd5ac7877f1ece794a4e32744ac96ca7980881e927624e373e9325` | `04_code/q3/model/q3_optimization_audit_b.py` |
| Q4 | `03_data/processed/q4/q4_regret_definition_comparison_b.csv` | 6 | 14 | weight_domain、regret_definition、weight_count、a、b、N、R、P、U、max_regret、mean_regret、p95_regret、minimum_weight_score_range、near_zero_range_weights | `a1569e1bd99e02cdfffa3283cb6d1cc418323f1becff9b216c962edec216e89a` | `04_code/q4/model/q4_preference_audit_b.py` |
| Q4 | `03_data/processed/q4/q4_weight_domain_comparison_b.csv` | 3 | 14 | weight_domain、regret_definition、weight_count、a、b、N、R、P、U、max_regret、mean_regret、p95_regret、minimum_weight_score_range、near_zero_range_weights | `524c89813f544e98fa6bb41139b7e01f6d72718da6bc7312461cf8c5a07e5939` | `04_code/q4/model/q4_preference_audit_b.py` |
| Q4 | `03_data/processed/q4/q4_weight_mapping_b.csv` | 2343 | 10 | weight_domain、weight_id、w_R、w_P、w_U、a、b、N、optimal_score、score_range | `8babcc8ddeee89e04454ebe6442ae9ba3bcba6562cb30340a3ec6e78469aa17d` | `04_code/q4/model/q4_preference_audit_b.py` |
| Q4 | `03_data/processed/q4/q4_weight_share_b.csv` | 13 | 4 | N、winning_weight_count、weight_domain、winning_weight_share | `6ba769864a8264215e4a24fd87019232053f196f9cbbca150012a31b4b8090a0` | `04_code/q4/model/q4_preference_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_cross_scenario_regret_b.csv` | 856 | 11 | a、b、N、S1-A、S1-B、S2-A、S2-B、S3-A、S3-B、max_model_regret、mean_model_regret | `c9dd6006906663c38b0e5e95005a2be7afb21389251294b85fa61a8544b7c1eb` | `04_code/q5/model/q5_robustness_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_dominant_metric_switch_b.csv` | 3 | 3 | dominant_metric、sample_count、sample_share | `705acd13cfa482285ec791445a641804c78f2ffee11a100d7fe58745dddd306d` | `04_code/q5/model/q5_robustness_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_error_distribution_comparison_b.csv` | 6 | 8 | distribution、sample_count、a、b、N、cvar95、candidate_count、support_tau | `819a542b02511c18c0345e146cc13ae1960bcd96bcf354e95fe1942901086fa0` | `04_code/q5/model/q5_robustness_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_model_ambiguity_robust_b.csv` | 7 | 8 | selection、scenario、a、b、N、cvar95、max_model_regret、mean_model_regret | `2cd1f05c6493fcf6d68ec6a714aef74e3d94d4be70c0467470978b5da3df7e5d` | `04_code/q5/model/q5_robustness_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_perturbation_domain_audit_b.csv` | 3 | 9 | candidate、a、b、N、min_realized_a、max_realized_a、min_realized_b、max_realized_b、formal_domain_contained | `08f70b9428d4da71163d1187fa8d2bf6f027a5646ec751abc5397d2f8d4e5ee3` | `04_code/q5/model/q5_robustness_audit_b.py` |
| Q5 | `03_data/processed/q5/q5_sobol_indices_b.csv` | 4 | 6 | factor、sobol_first_order、sobol_first_order_raw、sobol_total_order、interaction_gap、sample_size | `3fbc76f1a8e4af658bee1f153975e91363aeb5d6cb4bc434b088ed8a07b102db` | `04_code/q5/model/q5_robustness_audit_b.py` |

## 图表文件

| 问题 | 路径 | SHA-256 | 生成程序 |
| --- | --- | --- | --- |
| Q1 | `05_figures/q1/fig_q1_01_main_effects_b.pdf` | `be383bb40e052f8a282bde4a2403e0a8c3cc1b49734fcda1dc9d885ccfa13046` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_01_main_effects_b.png` | `5dda8aae479a0e7881f3ca7121bc7c53e2eb0a57e8a327a59ad92214d9e8531d` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_02_performance_tradeoff_b.pdf` | `ace7b3ce654fbb8b5a656e091268d1a5c4a93bd8dd531f21319e85a76770d223` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_02_performance_tradeoff_b.png` | `32f10cdb8399f77111a1e878ca93f0ff45ddb3ded2a358ed6c7e040991996761` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_03_effect_contributions_b.pdf` | `af86f1f21a70abb0b757e0db01c314d63bc73c8cabce941165711f94f03d1e0a` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_03_effect_contributions_b.png` | `f565e8d023b6603ec9670dd189e67b34b9ae1af2b83ffae3fcfe06a642c1d784` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_04_interaction_effects_b.pdf` | `d29a5c88b631546b544da40d2c768586c89bd24b2dfe1774a8ab308750090b07` | `04_code/q1/plotting/q1_plot_results_b.py` |
| Q1 | `05_figures/q1/fig_q1_04_interaction_effects_b.png` | `ed31a1c22595289ab20f3babb115a0afbccdb422f28bc75aa36c209dcf0a8d0b` | `04_code/q1/plotting/q1_plot_results_b.py` |

## 统一运行口径

- 输入：官方原始数据的现有只读处理结果与原模型工作产物。
- 单位：`R`、`P`、`U` 延续附件无量纲口径；结构参数延续题面定义。
- 缺失值：生成程序发现关键字段缺失时停止，不做静默填补。
- 随机种子：程序内固定为 `20260730` 及明确偏移值。
- 当前环境：本机 Python 3.14.0 系统解释器；项目 `.venv` 因中文路径启动问题尚未完成复核。
- 当前结论：仅为 `[B]` 平行候选与审计结果，不得写入冻结结果或替换主模型。
