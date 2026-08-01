"""Q5 鲁棒性分析：误差分布、模型歧义和全局敏感性。"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import qmc


RESULTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESULTS / "q3" / "code"))
import q3_optimize_pareto as q3  # noqa: E402
import q5_optimize_robustness as q45  # noqa: E402


OUTPUT = RESULTS / "q5" / "data"
SCENARIO_OPTIMA = OUTPUT / "q5_operation_design_comparison.csv"
STRUCTURE_OPTIMA = OUTPUT / "q5_structure_layer_optima.csv"
N_LEVELS = (2.0, 4.0, 6.0, 8.0, 10.0)
TAU = 0.025
SEED = 20260730
SCENARIOS = {
    "S1-A": ((0.80, 0.75, 0.25, 0.25), "A"),
    "S1-B": ((0.80, 0.75, 0.25, 0.25), "B"),
    "S2-A": ((0.50, 0.50, 0.50, 0.50), "A"),
    "S2-B": ((0.50, 0.50, 0.50, 0.50), "B"),
    "S3-A": ((0.20, 0.25, 0.80, 0.80), "A"),
    "S3-B": ((0.20, 0.25, 0.80, 0.80), "B"),
}


def cvar_rows(values: np.ndarray, alpha: float = 0.95) -> np.ndarray:
    threshold = np.quantile(values, alpha, axis=1)
    return np.array([row[row >= limit].mean() for row, limit in zip(values, threshold)])


def candidate_designs() -> np.ndarray:
    a = np.linspace(0.105, 0.295, 13)
    b = np.linspace(3.0375, 4.4625, 13)
    aa, bb = np.meshgrid(a, b, indexing="ij")
    designs = [np.column_stack([aa.ravel(), bb.ravel(), np.full(aa.size, n)]) for n in N_LEVELS]
    extra = []
    for path in (SCENARIO_OPTIMA, STRUCTURE_OPTIMA):
        frame = pd.read_csv(path)
        extra.append(frame[["a", "b", "N"]].to_numpy(float))
    all_designs = np.vstack([*designs, *extra])
    all_designs[:, 0] = np.clip(all_designs[:, 0], 0.105, 0.295)
    all_designs[:, 1] = np.clip(all_designs[:, 1], 3.0375, 4.4625)
    return np.unique(np.round(all_designs, 12), axis=0)


def lhs_uniform(n: int, dimensions: int, seed: int) -> np.ndarray:
    return qmc.LatinHypercube(dimensions, seed=seed).random(n)


def structural_distributions(n: int = 2048) -> dict[str, np.ndarray]:
    base_u = lhs_uniform(n, 2, SEED)
    uniform = qmc.scale(base_u, [-TAU, -TAU], [TAU, TAU])
    triangular = np.column_stack(
        [
            np.where(
                base_u[:, index] < 0.5,
                -TAU + np.sqrt(base_u[:, index] * 2.0 * TAU**2),
                TAU - np.sqrt((1.0 - base_u[:, index]) * 2.0 * TAU**2),
            )
            for index in range(2)
        ]
    )
    truncated = stats.truncnorm.ppf(base_u, -2.0, 2.0, loc=0.0, scale=TAU / 2.0)

    normal_scores = stats.norm.ppf(np.clip(base_u, 1e-12, 1 - 1e-12))
    correlated = {}
    for label, rho in (("uniform_positive_rho_0p6", 0.6), ("uniform_negative_rho_m0p6", -0.6)):
        chol = np.linalg.cholesky(np.array([[1.0, rho], [rho, 1.0]]))
        uniforms = stats.norm.cdf(normal_scores @ chol.T)
        correlated[label] = qmc.scale(uniforms, [-TAU, -TAU], [TAU, TAU])

    corners = np.array([[-TAU, -TAU], [-TAU, TAU], [TAU, -TAU], [TAU, TAU]])
    return {
        "independent_uniform": uniform,
        "symmetric_triangular": triangular,
        "truncated_normal_2sigma": truncated,
        **correlated,
        "deterministic_corners": corners,
    }


def structural_risk(designs: np.ndarray, eps: np.ndarray, ridge, pchip, batch_size: int = 24) -> np.ndarray:
    risks = []
    for start in range(0, len(designs), batch_size):
        batch = designs[start : start + batch_size]
        repeated = np.repeat(batch, len(eps), axis=0)
        tiled = np.tile(eps, (len(batch), 1))
        realized = repeated.copy()
        realized[:, 0] += 0.20 * tiled[:, 0]
        realized[:, 1] += 1.50 * tiled[:, 1]
        values = q3.predict(realized, ridge, pchip)
        scores = q45.score(values).reshape(len(batch), len(eps))
        risks.extend(cvar_rows(scores))
    return np.asarray(risks)


def distribution_comparison(designs: np.ndarray, ridge, pchip) -> pd.DataFrame:
    rows = []
    for distribution, eps in structural_distributions().items():
        risks = structural_risk(designs, eps, ridge, pchip)
        index = int(np.argmin(risks))
        rows.append(
            {
                "distribution": distribution,
                "sample_count": len(eps),
                "a": designs[index, 0],
                "b": designs[index, 1],
                "N": designs[index, 2],
                "cvar95": risks[index],
                "candidate_count": len(designs),
                "support_tau": TAU,
            }
        )
    return pd.DataFrame(rows)


def domain_check() -> pd.DataFrame:
    layer = pd.read_csv(STRUCTURE_OPTIMA)
    robust = layer.iloc[int(layer.CVaR95.argmin())]
    designs = {
        "q3_nominal_boundary": np.array([0.2249317396262705, 4.5, 6.0]),
        "q3_nominal_projected": np.array([0.2249317396262705, 4.4625, 6.0]),
        "structure_robust": robust[["a", "b", "N"]].to_numpy(float),
    }
    rows = []
    for name, design in designs.items():
        minimum_a, maximum_a = design[0] - 0.005, design[0] + 0.005
        minimum_b, maximum_b = design[1] - 0.0375, design[1] + 0.0375
        rows.append(
            {
                "candidate": name,
                "a": design[0],
                "b": design[1],
                "N": design[2],
                "min_realized_a": minimum_a,
                "max_realized_a": maximum_a,
                "min_realized_b": minimum_b,
                "max_realized_b": maximum_b,
                "formal_domain_contained": bool(minimum_a >= 0.10 and maximum_a <= 0.30 and minimum_b >= 3.0 and maximum_b <= 4.5),
            }
        )
    return pd.DataFrame(rows)


def common_operation_samples(n: int = 1024) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sample = lhs_uniform(n, 4, SEED + 1)
    eps = qmc.scale(sample[:, :2], [-TAU, -TAU], [TAU, TAU])
    sm = 0.95 + 0.10 * sample[:, 2]
    sq = 0.95 + 0.10 * sample[:, 3]
    return eps, sm, sq


def operation_risk(designs: np.ndarray, eps: np.ndarray, sm: np.ndarray, sq: np.ndarray, ridge, pchip, pars, u_model: str, batch_size: int = 20) -> np.ndarray:
    risks = []
    alpha, theta, exponent_r, exponent_u = pars
    for start in range(0, len(designs), batch_size):
        batch = designs[start : start + batch_size]
        repeated = np.repeat(batch, len(eps), axis=0)
        tiled_eps = np.tile(eps, (len(batch), 1))
        tiled_sm = np.tile(sm, len(batch))
        tiled_sq = np.tile(sq, len(batch))
        realized = repeated.copy()
        realized[:, 0] += 0.20 * tiled_eps[:, 0]
        realized[:, 1] += 1.50 * tiled_eps[:, 1]
        base = q3.predict(realized, ridge, pchip)
        thermal = tiled_sq * base[:, 0] * (theta + (1.0 - theta) * tiled_sm ** (-exponent_r))
        pressure = base[:, 1] * (alpha * tiled_sm + (1.0 - alpha) * tiled_sm**2)
        uniformity = base[:, 2] * tiled_sm ** (-exponent_u)
        if u_model == "B":
            uniformity *= tiled_sq
        scores = q45.score(np.column_stack([thermal, pressure, uniformity])).reshape(len(batch), len(eps))
        risks.extend(cvar_rows(scores))
    return np.asarray(risks)


def model_ambiguity_analysis(designs: np.ndarray, ridge, pchip) -> tuple[pd.DataFrame, pd.DataFrame]:
    eps, sm, sq = common_operation_samples()
    risk_columns = {}
    scenario_rows = []
    for scenario, (pars, u_model) in SCENARIOS.items():
        risks = operation_risk(designs, eps, sm, sq, ridge, pchip, pars, u_model)
        optimum = float(np.min(risks))
        risk_columns[scenario] = risks
        index = int(np.argmin(risks))
        scenario_rows.append(
            {
                "selection": f"scenario_optimum_{scenario}",
                "scenario": scenario,
                "a": designs[index, 0],
                "b": designs[index, 1],
                "N": designs[index, 2],
                "cvar95": risks[index],
            }
        )

    risk_frame = pd.DataFrame(risk_columns)
    regrets = risk_frame - risk_frame.min(axis=0)
    risk_frame.insert(0, "N", designs[:, 2])
    risk_frame.insert(0, "b", designs[:, 1])
    risk_frame.insert(0, "a", designs[:, 0])
    risk_frame["max_model_regret"] = regrets.max(axis=1)
    risk_frame["mean_model_regret"] = regrets.mean(axis=1)
    robust_index = int(np.lexsort((risk_frame.mean_model_regret, risk_frame.max_model_regret))[0])
    scenario_rows.append(
        {
            "selection": "minimax_model_regret",
            "scenario": "all_six",
            "a": designs[robust_index, 0],
            "b": designs[robust_index, 1],
            "N": designs[robust_index, 2],
            "cvar95": np.nan,
            "max_model_regret": risk_frame.loc[robust_index, "max_model_regret"],
            "mean_model_regret": risk_frame.loc[robust_index, "mean_model_regret"],
        }
    )
    return pd.DataFrame(scenario_rows), risk_frame


def sobol_analysis(ridge, pchip, design: np.ndarray, sample_power: int = 15) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = 2**sample_power
    rng = np.random.default_rng(SEED + 2)
    a_matrix = rng.random((n, 4))
    b_matrix = rng.random((n, 4))

    def transform(unit: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        eps = qmc.scale(unit[:, :2], [-TAU, -TAU], [TAU, TAU])
        return eps, 0.95 + 0.10 * unit[:, 2], 0.95 + 0.10 * unit[:, 3]

    def evaluate(unit: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        eps, sm, sq = transform(unit)
        values = q45.operation_values(design, eps, sm, sq, ridge, pchip, SCENARIOS["S2-A"][0], "A")
        z = (values - q45.IDEAL) / q45.SPAN
        dominant = np.argmax(z, axis=1)
        return q45.score(values), dominant

    y_a, dominant_a = evaluate(a_matrix)
    y_b, dominant_b = evaluate(b_matrix)
    variance = float(np.var(np.r_[y_a, y_b], ddof=1))
    names = ("epsilon_a", "epsilon_b", "s_m", "s_q")
    rows = []
    for index, name in enumerate(names):
        hybrid = a_matrix.copy()
        hybrid[:, index] = b_matrix[:, index]
        y_ab, _ = evaluate(hybrid)
        first_raw = float(np.mean(y_b * (y_ab - y_a)) / variance)
        first = max(0.0, first_raw)
        total = float(0.5 * np.mean(np.square(y_a - y_ab)) / variance)
        rows.append(
            {
                "factor": name,
                "sobol_first_order": first,
                "sobol_first_order_raw": first_raw,
                "sobol_total_order": total,
                "interaction_gap": total - first,
                "sample_size": n,
            }
        )

    dominant = np.r_[dominant_a, dominant_b]
    labels = np.array(["thermal", "pressure", "uniformity"])
    shares = pd.DataFrame(
        {
            "dominant_metric": labels,
            "sample_count": [int(np.sum(dominant == index)) for index in range(3)],
        }
    )
    shares["sample_share"] = shares.sample_count / len(dominant)
    return pd.DataFrame(rows), shares


def main() -> None:
    pin, base = q3.read_data()
    ridge, pchip = q3.build_surrogate(pin, base)
    designs = candidate_designs()
    distributions = distribution_comparison(designs, ridge, pchip)
    domain = domain_check()
    ambiguity, scenario_risks = model_ambiguity_analysis(designs, ridge, pchip)
    robust_layer = pd.read_csv(STRUCTURE_OPTIMA)
    robust = robust_layer.iloc[int(robust_layer.CVaR95.argmin())][["a", "b", "N"]].to_numpy(float)
    sobol, dominant = sobol_analysis(ridge, pchip, robust)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT / "q5_error_distribution_comparison.csv": distributions,
        OUTPUT / "q5_perturbation_domain_check.csv": domain,
        OUTPUT / "q5_model_ambiguity_robust.csv": ambiguity,
        OUTPUT / "q5_cross_scenario_regret.csv": scenario_risks,
        OUTPUT / "q5_sobol_indices.csv": sobol,
        OUTPUT / "q5_dominant_metric_switch.csv": dominant,
    }
    for path, frame in outputs.items():
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"wrote {len(frame)} rows to {path}")


if __name__ == "__main__":
    main()
