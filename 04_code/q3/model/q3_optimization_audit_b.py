"""Q3 的 [B] 平行审计：代理模型分歧、连续精化和决策尺度敏感性。"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "04_code" / "q3" / "model"))
sys.path.insert(0, str(ROOT / "04_code" / "q4" / "model"))
import q3_multiobjective_optimization as q3  # noqa: E402
import q45_preference_and_robustness as q45  # noqa: E402


OUTPUT = ROOT / "03_data" / "processed" / "q3"
REFERENCE = OUTPUT / "q3_pareto_reference_merged.csv"
REOPTIMIZED = ROOT / "03_data" / "processed" / "validation" / "q3" / "q3_model_reoptimization.csv"
RESPONSES = ("R", "P", "U")
N_LEVELS = (2.0, 4.0, 6.0, 8.0, 10.0)
RHO = 1e-4
SEED = 20260730


def simplex(resolution: int) -> np.ndarray:
    return np.array(
        [(i / resolution, j / resolution, (resolution - i - j) / resolution) for i in range(resolution + 1) for j in range(resolution + 1 - i)],
        dtype=float,
    )


def score(values: np.ndarray, weights: np.ndarray, span_scale: np.ndarray | None = None) -> np.ndarray:
    values = np.asarray(values, float)
    weights = np.asarray(weights, float)
    scale = np.ones(3) if span_scale is None else np.asarray(span_scale, float)
    z = (values - q45.IDEAL) / (q45.SPAN * scale)
    weighted = z * (3.0 * weights)
    return np.max(weighted, axis=-1) + RHO * np.sum(weighted, axis=-1)


def build_models(pin: pd.DataFrame, base: pd.DataFrame):
    x = pin[["a", "b", "N"]].to_numpy(float)
    models: dict[str, dict[str, object]] = {"current_ridge": {}, "cubic_ols": {}, "matern_gp": {}}
    current, _ = q3.build_surrogate(pin, base)
    models["current_ridge"] = current
    for response in RESPONSES:
        y = pin[response].to_numpy(float)
        models["cubic_ols"][response] = make_pipeline(
            StandardScaler(), PolynomialFeatures(3, include_bias=False), StandardScaler(), LinearRegression()
        ).fit(x, y)
        kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(np.ones(3), (1e-2, 1e2), nu=2.5) + WhiteKernel(1e-6, (1e-10, 1e-2))
        models["matern_gp"][response] = make_pipeline(
            StandardScaler(),
            GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=1, random_state=SEED),
        ).fit(x, y)
    return models


def predict_model(x: np.ndarray, model: dict[str, object]) -> np.ndarray:
    return np.column_stack([model[response].predict(x) for response in RESPONSES])


def front_for_model(model: dict[str, object], grid_size: int = 101) -> tuple[np.ndarray, np.ndarray]:
    a = np.linspace(0.10, 0.30, grid_size)
    b = np.linspace(3.0, 4.5, grid_size)
    aa, bb = np.meshgrid(a, b, indexing="ij")
    designs = []
    values = []
    for n_value in N_LEVELS:
        x = np.column_stack([aa.ravel(), bb.ravel(), np.full(aa.size, n_value)])
        f = predict_model(x, model)
        keep = q3.nondominated(f)
        designs.append(x[keep])
        values.append(f[keep])
    x_all, f_all = np.vstack(designs), np.vstack(values)
    keep = q3.nondominated(f_all)
    return x_all[keep], f_all[keep]


def surrogate_front_comparison(models) -> tuple[pd.DataFrame, pd.DataFrame]:
    fronts: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, model in models.items():
        fronts[name] = front_for_model(model)
    union_f = np.vstack([front[1] for front in fronts.values()])
    union_f = union_f[q3.nondominated(union_f)]
    union_z = (union_f - q45.IDEAL) / q45.SPAN
    metrics = []
    for name, (x, f) in fronts.items():
        z = (f - q45.IDEAL) / q45.SPAN
        distances = np.sqrt(np.square(union_z[:, None, :] - z[None, :, :]).sum(axis=2))
        metrics.append(
            {
                "model": name,
                "pareto_points": len(f),
                "hypervolume": q3.hypervolume3(z),
                "union_igd": float(np.mean(np.min(distances, axis=1))),
                "best_equal_weight_score": float(np.min(score(f, np.full(3, 1 / 3)))),
            }
        )

    candidates = pd.read_csv(REOPTIMIZED)
    cross_rows = []
    for candidate in candidates.itertuples(index=False):
        design = np.array([[float(candidate.a), float(candidate.b), float(candidate.N)]])
        for model_name, model in models.items():
            prediction = predict_model(design, model)[0]
            cross_rows.append(
                {
                    "candidate_source_model": candidate.模型,
                    "evaluation_model": model_name,
                    "a": design[0, 0],
                    "b": design[0, 1],
                    "N": design[0, 2],
                    "R": prediction[0],
                    "P": prediction[1],
                    "U": prediction[2],
                    "equal_weight_score": float(score(prediction, np.full(3, 1 / 3))),
                }
            )
    return pd.DataFrame(metrics), pd.DataFrame(cross_rows)


def refine_weighted_front(ridge) -> tuple[pd.DataFrame, pd.DataFrame]:
    reference = pd.read_csv(REFERENCE)
    weights = simplex(20)
    refined_rows = []
    for weight_id, weight in enumerate(weights):
        best = None
        for n_value in N_LEVELS:
            layer = reference[np.isclose(reference.N, n_value)]
            if layer.empty:
                continue
            layer_values = layer[list(RESPONSES)].to_numpy(float)
            start_row = layer.iloc[int(np.argmin(score(layer_values, weight)))]

            def objective(ab: np.ndarray) -> float:
                value = q3.predict(np.array([[ab[0], ab[1], n_value]]), ridge, {})[0]
                return float(score(value, weight))

            result = minimize(
                objective,
                np.array([start_row.a, start_row.b], dtype=float),
                method="SLSQP",
                bounds=((0.10, 0.30), (3.0, 4.5)),
                options={"ftol": 1e-12, "maxiter": 200},
            )
            method = "SLSQP"
            if not result.success:
                retry = minimize(
                    objective,
                    np.asarray(result.x, dtype=float),
                    method="Powell",
                    bounds=((0.10, 0.30), (3.0, 4.5)),
                    options={"xtol": 1e-10, "ftol": 1e-12, "maxiter": 400},
                )
                if retry.success or retry.fun < result.fun:
                    result = retry
                    method = "Powell_retry"
            design = np.array([[result.x[0], result.x[1], n_value]])
            values = q3.predict(design, ridge, {})[0]
            row = {
                "weight_id": weight_id,
                "w_R": weight[0],
                "w_P": weight[1],
                "w_U": weight[2],
                "a": design[0, 0],
                "b": design[0, 1],
                "N": n_value,
                "R": values[0],
                "P": values[1],
                "U": values[2],
                "score": float(score(values, weight)),
                "optimizer_success": bool(result.success),
                "optimizer_method": method,
            }
            if best is None or row["score"] < best["score"]:
                best = row
        if best is not None:
            refined_rows.append(best)

    refined = pd.DataFrame(refined_rows)
    reference_values = reference[list(RESPONSES)].to_numpy(float)
    refined_values = refined[list(RESPONSES)].to_numpy(float)
    merged_values = np.vstack([reference_values, refined_values])
    keep = q3.nondominated(merged_values)
    new_kept = int(keep[len(reference_values) :].sum())
    base_hv = q3.hypervolume3((reference_values - q45.IDEAL) / q45.SPAN)
    merged_hv = q3.hypervolume3((merged_values[keep] - q45.IDEAL) / q45.SPAN)
    convergence = pd.DataFrame(
        [
            {
                "method": "reference_merged",
                "points": len(reference_values),
                "hypervolume": base_hv,
                "new_refined_points_kept": 0,
            },
            {
                "method": "reference_plus_weight_refinement_b",
                "points": int(keep.sum()),
                "hypervolume": merged_hv,
                "new_refined_points_kept": new_kept,
            },
        ]
    )
    return refined, convergence


def decision_sensitivity(refined: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = refined[list(RESPONSES)].to_numpy(float)
    z = (values - q45.IDEAL) / q45.SPAN
    criteria = {
        "augmented_tchebycheff": np.max(z, axis=1) + RHO * z.sum(axis=1),
        "euclidean_to_ideal": np.sqrt(np.mean(np.square(z), axis=1)),
        "mean_normalized_loss": z.mean(axis=1),
    }
    rows = []
    for criterion, criterion_values in criteria.items():
        index = int(np.argmin(criterion_values))
        record = refined.iloc[index]
        rows.append(
            {
                "criterion": criterion,
                "a": record.a,
                "b": record.b,
                "N": record.N,
                "R": record.R,
                "P": record.P,
                "U": record.U,
                "criterion_value": float(criterion_values[index]),
            }
        )

    scale_rows = []
    equal = np.full(3, 1 / 3)
    for scale_r in (0.95, 1.0, 1.05):
        for scale_p in (0.95, 1.0, 1.05):
            for scale_u in (0.95, 1.0, 1.05):
                scales = np.array([scale_r, scale_p, scale_u])
                candidate_scores = score(values, equal, scales)
                index = int(np.argmin(candidate_scores))
                record = refined.iloc[index]
                scale_rows.append(
                    {
                        "scale_R": scale_r,
                        "scale_P": scale_p,
                        "scale_U": scale_u,
                        "a": record.a,
                        "b": record.b,
                        "N": record.N,
                        "R": record.R,
                        "P": record.P,
                        "U": record.U,
                        "score": float(candidate_scores[index]),
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(scale_rows)


def main() -> None:
    pin, base = q3.read_data()
    ridge, _ = q3.build_surrogate(pin, base)
    models = build_models(pin, base)
    front_metrics, cross_scores = surrogate_front_comparison(models)
    refined, convergence = refine_weighted_front(ridge)
    decisions, normalization = decision_sensitivity(refined)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT / "q3_surrogate_front_comparison_b.csv": front_metrics,
        OUTPUT / "q3_cross_model_candidate_scores_b.csv": cross_scores,
        OUTPUT / "q3_adaptive_pareto_b.csv": refined,
        OUTPUT / "q3_grid_convergence_b.csv": convergence,
        OUTPUT / "q3_decision_criteria_comparison_b.csv": decisions,
        OUTPUT / "q3_normalization_sensitivity_b.csv": normalization,
    }
    for path, frame in outputs.items():
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"wrote {len(frame)} rows to {path}")


if __name__ == "__main__":
    main()
