"""Q4 偏好敏感性分析：权重域、绝对遗憾与相对遗憾比较。"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RESULTS = Path(__file__).resolve().parents[2]
INPUT = RESULTS / "q3" / "data" / "q3_pareto_reference_merged.csv"
OUTPUT = RESULTS / "q4" / "data"
IDEAL = np.array([0.720227030892114, 0.076039812756808, 0.771786631558643])
NADIR = np.array([0.760176422366934, 0.158555235146874, 0.819442088245665])
SPAN = NADIR - IDEAL
RHO = 1e-4


def simplex(resolution: int) -> np.ndarray:
    return np.array(
        [(i / resolution, j / resolution, (resolution - i - j) / resolution) for i in range(resolution + 1) for j in range(resolution + 1 - i)],
        dtype=float,
    )


def weighted_scores(z: np.ndarray, weight: np.ndarray) -> np.ndarray:
    weighted = z * (3.0 * weight)
    return np.max(weighted, axis=1) + RHO * np.sum(weighted, axis=1)


def domains(weights: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "complete_simplex": weights,
        "balanced_w_ge_0p1": weights[np.all(weights >= 0.1 - 1e-12, axis=1)],
        "thermal_priority_wR_ge_0p5": weights[weights[:, 0] >= 0.5 - 1e-12],
    }


def evaluate_domain(reference: pd.DataFrame, weights: np.ndarray, domain_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    values = reference[["R", "P", "U"]].to_numpy(float)
    designs = reference[["a", "b", "N"]].to_numpy(float)
    z = (values - IDEAL) / SPAN
    n_candidates = len(reference)
    max_abs = np.full(n_candidates, -np.inf)
    max_rel = np.full(n_candidates, -np.inf)
    sum_abs = np.zeros(n_candidates)
    sum_rel = np.zeros(n_candidates)
    mapping_rows = []
    score_ranges = []

    for weight_id, weight in enumerate(weights):
        candidate_scores = weighted_scores(z, weight)
        optimum_index = int(np.argmin(candidate_scores))
        lower = float(candidate_scores[optimum_index])
        upper = float(np.max(candidate_scores))
        score_range = upper - lower
        absolute = candidate_scores - lower
        relative = absolute / (score_range + 1e-12)
        max_abs = np.maximum(max_abs, absolute)
        max_rel = np.maximum(max_rel, relative)
        sum_abs += absolute
        sum_rel += relative
        score_ranges.append(score_range)
        mapping_rows.append(
            {
                "weight_domain": domain_name,
                "weight_id": weight_id,
                "w_R": weight[0],
                "w_P": weight[1],
                "w_U": weight[2],
                "a": designs[optimum_index, 0],
                "b": designs[optimum_index, 1],
                "N": designs[optimum_index, 2],
                "optimal_score": lower,
                "score_range": score_range,
            }
        )

    summaries = []
    for definition, maximum, total in (
        ("absolute", max_abs, sum_abs),
        ("relative", max_rel, sum_rel),
    ):
        mean = total / len(weights)
        selected = int(np.lexsort((mean, maximum))[0])
        selected_regrets = []
        for weight in weights:
            candidate_scores = weighted_scores(z, weight)
            lower = float(np.min(candidate_scores))
            absolute = float(candidate_scores[selected] - lower)
            if definition == "absolute":
                selected_regrets.append(absolute)
            else:
                selected_regrets.append(absolute / (float(np.max(candidate_scores)) - lower + 1e-12))
        summaries.append(
            {
                "weight_domain": domain_name,
                "regret_definition": definition,
                "weight_count": len(weights),
                "a": designs[selected, 0],
                "b": designs[selected, 1],
                "N": designs[selected, 2],
                "R": values[selected, 0],
                "P": values[selected, 1],
                "U": values[selected, 2],
                "max_regret": maximum[selected],
                "mean_regret": mean[selected],
                "p95_regret": float(np.quantile(selected_regrets, 0.95)),
                "minimum_weight_score_range": float(np.min(score_ranges)),
                "near_zero_range_weights": int(np.sum(np.asarray(score_ranges) < 1e-8)),
            }
        )

    mapping = pd.DataFrame(mapping_rows)
    shares = (
        mapping.groupby("N", as_index=False)
        .size()
        .rename(columns={"size": "winning_weight_count"})
    )
    shares["weight_domain"] = domain_name
    shares["winning_weight_share"] = shares.winning_weight_count / len(mapping)
    return pd.DataFrame(summaries), mapping, shares


def main() -> None:
    reference = pd.read_csv(INPUT)
    all_weights = simplex(50)
    summary_frames = []
    mapping_frames = []
    share_frames = []
    for domain_name, weights in domains(all_weights).items():
        summary, mapping, shares = evaluate_domain(reference, weights, domain_name)
        summary_frames.append(summary)
        mapping_frames.append(mapping)
        share_frames.append(shares)

    summaries = pd.concat(summary_frames, ignore_index=True)
    mappings = pd.concat(mapping_frames, ignore_index=True)
    shares = pd.concat(share_frames, ignore_index=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT / "q4_weight_domain_comparison.csv": summaries[summaries.regret_definition == "absolute"].copy(),
        OUTPUT / "q4_regret_definition_comparison.csv": summaries,
        OUTPUT / "q4_weight_mapping.csv": mappings,
        OUTPUT / "q4_weight_share.csv": shares,
    }
    for path, frame in outputs.items():
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"wrote {len(frame)} rows to {path}")


if __name__ == "__main__":
    main()
