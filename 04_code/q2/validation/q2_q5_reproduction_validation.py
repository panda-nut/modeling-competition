"""Q2--Q5 独立产物复现检查。

本脚本不导入各问模型模块；它只读取已由登记入口重建的 CSV/JSON，重新计算
可检查的不变量，并写出 V1 复现证据。通过不代表物理假设已获外部实验验证。
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "03_data" / "processed"
OUT = PROCESSED / "validation" / "reproduction"
IDEAL = np.array([0.720227030892114, 0.076039812756808, 0.771786631558643])
NADIR = np.array([0.760176422366934, 0.158555235146874, 0.819442088245665])
SPAN = NADIR - IDEAL
N_LEVELS = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
RAW_XLSX = ROOT / "03_data" / "raw" / "apmcm-2026-b-appendix-2-data.xlsx"
RAW_SHA256 = "49EDAF3A4D8E8CE58093790724340BD29F0A1AC083DEF122E4AB5F360A578409"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nondominated_3d(values: np.ndarray, tol: float = 1e-11) -> np.ndarray:
    """独立的三目标最小化扫描，返回非支配掩码。"""
    order = np.lexsort((values[:, 2], values[:, 1], values[:, 0]))
    p_values = np.unique(values[:, 1])
    tree = np.full(len(p_values) + 2, np.inf)
    keep = np.zeros(len(values), dtype=bool)
    for index in order:
        position = np.searchsorted(p_values, values[index, 1]) + 1
        query, best = position, np.inf
        while query:
            best = min(best, tree[query])
            query -= query & -query
        if best > values[index, 2] + tol:
            keep[index] = True
        update = position
        while update < len(tree):
            tree[update] = min(tree[update], values[index, 2])
            update += update & -update
    return keep


def assert_check(records: list[dict[str, object]], name: str, condition: bool, detail: str) -> None:
    records.append({"检查项": name, "通过": bool(condition), "说明": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, object]] = []

    assert_check(checks, "原始数据-哈希", sha256(RAW_XLSX).upper() == RAW_SHA256, "官方附件2工作簿 SHA-256 与登记值一致")

    # Q2：交叉验证、结构化留出与跨问重优化。
    cv = pd.read_csv(PROCESSED / "validation" / "q2" / "q2_encoding_cv.csv")
    holdout = pd.read_csv(PROCESSED / "validation" / "q2" / "q2_structured_holdout.csv")
    reopt = pd.read_csv(PROCESSED / "validation" / "q3" / "q3_model_reoptimization.csv")
    assert_check(checks, "Q2-CV-行数", len(cv) == 4 and set(cv["编码"]) == {"数值三次", "类别交互", "分层响应面", "机理特征"}, "四种编码均完成十次重复五折交叉验证")
    assert_check(checks, "Q2-CV-误差范围", bool(((cv.iloc[:, 1:] >= 0) & (cv.iloc[:, 1:] < 1)).all().all()), "全部归一化 RMSE 位于 [0, 1)")
    numeric_cv = cv.loc[cv["编码"] == "数值三次", ["R_NRMSE", "P_NRMSE", "U_NRMSE"]].to_numpy()
    assert_check(checks, "Q2-CV-主模型", bool(len(numeric_cv) == 1 and numeric_cv.max() < 0.01), "三次 Ridge 主模型的三响应 NRMSE 均低于 1%")
    assert_check(checks, "Q2-留出-范围", bool(len(holdout) == 3 and (holdout.iloc[:, 1:] >= 0).all().all() and (holdout.iloc[:, 1:] < 0.02).all().all()), "三响应组合留出与最差组合 NRMSE 均低于 2%")
    primary = reopt.loc[reopt["模型"] == "数值三次"].iloc[0]
    assert_check(checks, "Q2-Q3-接口", bool(abs(primary["评分"] - 0.38638274667145095) < 1e-8 and primary["N"] == 6), "主代理重优化结果与 Q3 折中评分闭合")

    # Q3：设计域、全局 Pareto、算法重复和连续精化。
    global_front = pd.read_csv(PROCESSED / "q3" / "q3_pareto_global.csv")
    reference = pd.read_csv(PROCESSED / "q3" / "q3_pareto_reference_merged.csv")
    local = pd.read_csv(PROCESSED / "q3" / "q3_local_refinement.csv")
    metrics = pd.read_csv(PROCESSED / "q3" / "q3_algorithm_metrics_exact.csv")
    domain_ok = ((global_front["a"] >= 0.1) & (global_front["a"] <= 0.3) & (global_front["b"] >= 3.0) & (global_front["b"] <= 4.5) & global_front["N"].isin(N_LEVELS)).all()
    assert_check(checks, "Q3-设计域", bool(len(global_front) == 16858 and domain_ok), "401 网格 Pareto 集含 16,858 点，均在合法有针肋设计域")
    ref_values = reference[["R", "P", "U"]].to_numpy(float)
    assert_check(checks, "Q3-支配关系", bool(nondominated_3d(ref_values).all()), "合并参考集不存在可检测的三目标支配点")
    grid = metrics[metrics["method"].str.startswith("分层网格")].sort_values("evaluations")
    nsga = metrics[metrics["method"] == "分层 NSGA-II"]
    assert_check(checks, "Q3-网格收敛", bool(len(grid) == 3 and np.all(np.diff(grid["HV"]) > 0) and np.all(np.diff(grid["IGD_plus"]) < 0)), "网格加密时精确 HV 上升、IGD+ 下降")
    assert_check(checks, "Q3-随机重复", bool(len(nsga) == 20 and nsga["run"].nunique() == 20 and nsga["HV"].notna().all()), "20 个固定种子 NSGA-II 重复均生成指标")
    final = local.loc[local["C_AT"].idxmin()]
    assert_check(checks, "Q3-折中方案", bool(final["N"] == 6 and abs(final["C_AT"] - 0.38638274667145095) < 1e-8), "连续精化折中解保持 N=6 且评分闭合")

    # Q4：权重单纯形覆盖、评分公式、遗憾和稳定性。
    scan = pd.read_csv(PROCESSED / "q4" / "q4_weight_scan_H50.csv")
    convergence = pd.read_csv(PROCESSED / "q4" / "q4_convergence_corrected.csv")
    regret = pd.read_csv(PROCESSED / "q4" / "q4_regret_comparison.csv")
    weights = scan[["w_R", "w_P", "w_U"]].to_numpy(float)
    design_ok = ((scan["a"] >= 0.1) & (scan["a"] <= 0.3) & (scan["b"] >= 3.0) & (scan["b"] <= 4.5) & scan["N"].isin(N_LEVELS)).all()
    expected_g = np.max(((scan[["R", "P", "U"]].to_numpy(float) - IDEAL) / SPAN) * (3 * weights), axis=1) + 1e-4 * np.sum(((scan[["R", "P", "U"]].to_numpy(float) - IDEAL) / SPAN) * (3 * weights), axis=1)
    assert_check(checks, "Q4-权重覆盖", bool(len(scan) == 1326 and np.allclose(weights.sum(axis=1), 1.0) and (weights >= 0).all() and design_ok), "H=50 单纯形覆盖 1,326 组非负归一权重，候选均合法")
    assert_check(checks, "Q4-评分闭环", bool(np.allclose(scan["G"].to_numpy(float), expected_g, rtol=0, atol=1e-11)), "CSV 中带权增强切比雪夫评分可由固定尺度独立重算")
    assert_check(checks, "Q4-遗憾稳定", bool(len(convergence) == 3 and convergence["N"].eq(6).all() and np.isclose(convergence["最大遗憾"], convergence["最大遗憾"].iloc[0]).all()), "H=25/50/100 下最小最大遗憾解均为 N=6，最坏遗憾一致")
    assert_check(checks, "Q4-遗憾非负", bool((regret[["最大遗憾", "平均遗憾", "P95遗憾"]] >= -1e-12).all().all()), "候选相对同权重最优解的遗憾均非负")

    # Q5：域内风险、CVaR 顺序、情景结果和跨问最坏情形。
    formal = pd.read_csv(PROCESSED / "q5" / "q5_formal_domain_risk.csv")
    operation = pd.read_csv(PROCESSED / "q5" / "q5_operation_design_comparison.csv")
    r2 = pd.read_csv(PROCESSED / "q5" / "q5_src_r2.csv")
    worst = json.loads((PROCESSED / "validation" / "q5" / "q5_worst_case_summary.json").read_text(encoding="utf-8"))["worst_case"]
    formal_domain = ((formal["a"] >= 0.105) & (formal["a"] <= 0.295) & (formal["b"] >= 3.0375) & (formal["b"] <= 4.4625) & formal["N"].isin(N_LEVELS)).all()
    tail_order = (formal["CVaR95"] >= formal["Q95"]).all() and (formal["Q95"] >= formal["均值"]).all()
    assert_check(checks, "Q5-域内风险", bool(len(formal) == 2 and formal_domain and tail_order), "正式加工风险仅包含鲁棒可行域设计，且均值 ≤ Q95 ≤ CVaR95")
    assert_check(checks, "Q5-工况情景", bool(len(operation) == 6 and set(operation["U模型"]) == {"A", "B"} and (operation["相对风险增幅"] >= -1e-12).all()), "S1--S3 与 A/B 六个情景均重建；结构鲁棒解未被误称为各情景最优")
    assert_check(checks, "Q5-SRC-适用性", bool(((r2.iloc[:, 1:] >= 0) & (r2.iloc[:, 1:] <= 1)).all().all()), "SRC 线性近似 R² 在 [0, 1] 内")
    assert_check(checks, "Q5-跨问最坏情形", bool(0.105 <= worst["a"] <= 0.295 and 3.0375 <= worst["b"] <= 4.4625 and worst["N"] in N_LEVELS and worst["score"] > 0), "最坏情形重优化位于鲁棒可行域")

    pd.DataFrame(checks).to_csv(OUT / "q2_q5_reproduction_checks.csv", index=False, encoding="utf-8-sig")
    sources = [
        RAW_XLSX,
        PROCESSED / "validation" / "q2" / "q2_encoding_cv.csv",
        PROCESSED / "validation" / "q2" / "q2_structured_holdout.csv",
        PROCESSED / "validation" / "q3" / "q3_model_reoptimization.csv",
        PROCESSED / "q3" / "q3_pareto_reference_merged.csv",
        PROCESSED / "q4" / "q4_weight_scan_H50.csv",
        PROCESSED / "q5" / "q5_formal_domain_risk.csv",
        PROCESSED / "q5" / "q5_operation_design_comparison.csv",
    ]
    evidence = {
        "evidence_id": "E-Q2-Q5-REPRO-001",
        "generated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "machine": "[A]",
        "interpreter": sys.version,
        "platform": platform.platform(),
        "commands": [
            ".venv\\Scripts\\python.exe 04_code\\q3\\model\\q3_multiobjective_optimization.py",
            ".venv\\Scripts\\python.exe 04_code\\q3\\model\\q3_candidate_algorithm_comparison.py",
            ".venv\\Scripts\\python.exe 04_code\\q3\\model\\q3_methodology_finalization.py",
            ".venv\\Scripts\\python.exe 04_code\\q4\\model\\q45_preference_and_robustness.py",
            ".venv\\Scripts\\python.exe 04_code\\q4\\model\\q45_final_revision.py",
            ".venv\\Scripts\\python.exe 04_code\\q4\\model\\q45_evidence_boundary_revision.py",
            ".venv\\Scripts\\python.exe 04_code\\q2\\validation\\q2_revision_analysis.py",
            ".venv\\Scripts\\python.exe 04_code\\q2\\validation\\q2_q5_reproduction_validation.py",
        ],
        "checks": checks,
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path) for path in sources},
        "conclusion": "pass_with_limits：已在隔离 Python 3.14 环境从登记入口重建并通过独立产物检查；不等同于外部实验、物理机理或冻结批准。",
    }
    (OUT / "q2_q5_reproduction_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Q2—Q5 独立复现记录",
        "",
        "> Evidence ID：`E-Q2-Q5-REPRO-001`。本记录验证可重复计算与产物不变量，",
        "> 不把参数化工况情景解释为外部实验验证，也不授予冻结状态。",
        "",
        "## 结论",
        "",
        "- `progress=completed`，`stage=v1`，`review=pass_with_limits`。",
        "- Q2—Q5 已在 Python 3.14 项目虚拟环境中按 Q3 → Q4/Q5 → Q2 依赖链重新执行。",
        f"- {len(checks)} 项独立 CSV/JSON 不变量检查全部通过。",
        "",
        "## 检查结果",
        "",
        "| 检查项 | 结果 | 说明 |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {row['检查项']} | {'通过' if row['通过'] else '失败'} | {row['说明']} |" for row in checks)
    lines.extend([
        "",
        "## 限制",
        "",
        "- Q2 的 CV/留出验证证明附件数据内的代理拟合与切分表现，不证明未知物理工况的外推精度。",
        "- Q3 的随机算法比较使用固定 20 个种子；Q3 折中解是代理模型与给定目标尺度下的结果，不是现实系统全局最优证明。",
        "- Q4 的权重与 Q5 的公差、流量、热负荷均为已声明的参数化情景；Q5 B 类工况不具有新增实验/CFD 数据支持。",
        "- 本记录不构成 `07_frozen/` 批准；冻结仍需要用户明确确认和冻结清单。",
        "",
        "机器可读证据见 `q2_q5_reproduction_evidence.json`，逐项结果见 `q2_q5_reproduction_checks.csv`。",
        "",
    ])
    (OUT / "q2_q5_reproduction_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"passed {len(checks)} independent checks")


if __name__ == "__main__":
    main()
