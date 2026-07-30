"""Q2 的 [B] 平行审计：嵌套交叉验证、阶数选择和无针肋插值检查。"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, KFold, RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "03_data" / "processed" / "q1" / "q1_response_data.csv"
PARETO = ROOT / "03_data" / "processed" / "q3" / "q3_pareto_global.csv"
OUTPUT = ROOT / "03_data" / "processed" / "q2"
RESPONSES = ("R", "P", "U")
DEGREES = (2, 3, 4)
ALPHAS = np.logspace(-8, 2, 11)
OUTER_SPLITS = 5
OUTER_REPEATS = 10
SEED = 20260730


def read_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(INPUT)
    return data[data.N > 0].copy(), data[data.N == 0].sort_values("b").copy()


def pipeline(degree: int) -> Pipeline:
    return Pipeline(
        [
            ("input_scale", StandardScaler()),
            ("poly", PolynomialFeatures(degree, include_bias=False)),
            ("feature_scale", StandardScaler()),
            ("ridge", Ridge()),
        ]
    )


def nested_cv(pin: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    x = pin[["a", "b", "N"]].to_numpy(float)
    outer = RepeatedKFold(n_splits=OUTER_SPLITS, n_repeats=OUTER_REPEATS, random_state=SEED)
    splits = list(outer.split(x))
    fold_rows: list[dict[str, float | int | str]] = []
    for response in RESPONSES:
        y = pin[response].to_numpy(float)
        response_range = float(np.ptp(y))
        for degree in DEGREES:
            for fold, (train, test) in enumerate(splits):
                inner = KFold(n_splits=5, shuffle=True, random_state=SEED + fold)
                search = GridSearchCV(
                    pipeline(degree),
                    {"ridge__alpha": ALPHAS},
                    scoring="neg_mean_squared_error",
                    cv=inner,
                    n_jobs=1,
                    refit=True,
                )
                search.fit(x[train], y[train])
                prediction = search.predict(x[test])
                error = y[test] - prediction
                fold_rows.append(
                    {
                        "response": response,
                        "degree": degree,
                        "outer_fold": fold,
                        "outer_repeat": fold // OUTER_SPLITS,
                        "test_size": len(test),
                        "selected_alpha": float(search.best_params_["ridge__alpha"]),
                        "rmse": float(np.sqrt(np.mean(np.square(error)))),
                        "nrmse": float(np.sqrt(np.mean(np.square(error))) / response_range),
                        "max_absolute_error": float(np.max(np.abs(error))),
                    }
                )
    folds = pd.DataFrame(fold_rows)
    summary = (
        folds.groupby(["response", "degree"], as_index=False)
        .agg(
            nrmse_mean=("nrmse", "mean"),
            nrmse_std=("nrmse", "std"),
            nrmse_max=("nrmse", "max"),
            max_absolute_error=("max_absolute_error", "max"),
            alpha_median=("selected_alpha", "median"),
            alpha_min=("selected_alpha", "min"),
            alpha_max=("selected_alpha", "max"),
        )
        .sort_values(["response", "nrmse_mean"])
    )
    alpha_rows: list[dict[str, float | int | str]] = []
    for (response, degree), group in folds.groupby(["response", "degree"]):
        counts = Counter(group.selected_alpha)
        for alpha, count in sorted(counts.items()):
            alpha_rows.append(
                {
                    "response": response,
                    "degree": int(degree),
                    "alpha": float(alpha),
                    "selection_count": int(count),
                    "selection_share": float(count / len(group)),
                }
            )
    return folds, summary, pd.DataFrame(alpha_rows)


def baseline_interpolation_audit(base: pd.DataFrame) -> pd.DataFrame:
    pareto = pd.read_csv(PARETO)[["R", "P", "U"]].to_numpy(float)
    b_dense = np.linspace(float(base.b.min()), float(base.b.max()), 2001)
    rows: list[dict[str, float | int | str | bool]] = []
    methods = {
        "discrete_nodes": (base.b.to_numpy(float), base[list(RESPONSES)].to_numpy(float)),
        "linear": (
            b_dense,
            np.column_stack([np.interp(b_dense, base.b, base[response]) for response in RESPONSES]),
        ),
        "pchip": (
            b_dense,
            np.column_stack([PchipInterpolator(base.b, base[response])(b_dense) for response in RESPONSES]),
        ),
    }
    for method, (b_values, values) in methods.items():
        dominated_count = 0
        minimum_margin = np.inf
        for b_value, candidate in zip(b_values, values):
            differences = candidate[None, :] - pareto
            dominated = np.all(differences >= -1e-12, axis=1) & np.any(differences > 1e-12, axis=1)
            if dominated.any():
                dominated_count += 1
                minimum_margin = min(minimum_margin, float(np.max(np.min(differences[dominated], axis=1))))
            rows.append(
                {
                    "method": method,
                    "b": float(b_value),
                    "R": float(candidate[0]),
                    "P": float(candidate[1]),
                    "U": float(candidate[2]),
                    "dominated_by_pin_pareto": bool(dominated.any()),
                }
            )
        rows.append(
            {
                "method": f"{method}_summary",
                "b": np.nan,
                "R": np.nan,
                "P": np.nan,
                "U": np.nan,
                "dominated_by_pin_pareto": bool(dominated_count == len(values)),
                "points": int(len(values)),
                "dominated_points": int(dominated_count),
                "minimum_dominance_margin": float(minimum_margin if np.isfinite(minimum_margin) else np.nan),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    pin, base = read_data()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    folds, summary, alpha = nested_cv(pin)
    baseline = baseline_interpolation_audit(base)
    outputs = {
        OUTPUT / "q2_nested_cv_folds_b.csv": folds,
        OUTPUT / "q2_nested_model_comparison_b.csv": summary,
        OUTPUT / "q2_alpha_stability_b.csv": alpha,
        OUTPUT / "q2_baseline_interpolation_audit_b.csv": baseline,
    }
    for path, frame in outputs.items():
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"wrote {len(frame)} rows to {path}")


if __name__ == "__main__":
    main()
