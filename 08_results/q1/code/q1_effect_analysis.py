"""Q1 效应分析：计算主效应、交互效应和描述性平方和分解。"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
INPUT = PACKAGE / "data" / "q1_response_data.csv"
OUTPUT = PACKAGE / "data"
FACTORS = ("a", "b", "N")
RESPONSES = ("R", "P", "U")


def read_pin_data() -> pd.DataFrame:
    data = pd.read_csv(INPUT)
    required = {"a", "b", "N", *RESPONSES}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Q1 input is missing columns: {sorted(missing)}")
    pin = data.loc[data["N"] > 0, [*FACTORS, *RESPONSES]].copy()
    expected = int(np.prod([pin[f].nunique() for f in FACTORS]))
    if len(pin) != expected or pin.duplicated(list(FACTORS)).any():
        raise ValueError("The pin-fin data must be a complete, unreplicated factorial design")
    return pin


def main_effects(pin: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for response in RESPONSES:
        overall = float(pin[response].mean())
        for factor in FACTORS:
            for level, values in pin.groupby(factor, sort=True)[response]:
                marginal = float(values.mean())
                rows.append(
                    {
                        "response": response,
                        "factor": factor,
                        "level": float(level),
                        "marginal_mean": marginal,
                        "overall_mean": overall,
                        "relative_deviation_pct": 100.0 * (marginal - overall) / overall,
                        "sample_count": int(values.size),
                    }
                )
    return pd.DataFrame(rows)


def interaction_effects(pin: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for response in RESPONSES:
        overall = float(pin[response].mean())
        one_way = {factor: pin.groupby(factor)[response].mean() for factor in FACTORS}
        for first, second in combinations(FACTORS, 2):
            grouped = pin.groupby([first, second], sort=True)[response]
            for (level_first, level_second), values in grouped:
                cell_mean = float(values.mean())
                interaction = (
                    cell_mean
                    - float(one_way[first].loc[level_first])
                    - float(one_way[second].loc[level_second])
                    + overall
                )
                rows.append(
                    {
                        "response": response,
                        "factor_first": first,
                        "factor_second": second,
                        "level_first": float(level_first),
                        "level_second": float(level_second),
                        "cell_mean": cell_mean,
                        "interaction_effect": interaction,
                        "sample_count": int(values.size),
                    }
                )
    return pd.DataFrame(rows)


def effect_contributions(pin: pd.DataFrame) -> pd.DataFrame:
    levels = {factor: sorted(pin[factor].unique()) for factor in FACTORS}
    counts = {factor: len(values) for factor, values in levels.items()}
    rows: list[dict[str, float | int | str]] = []
    for response in RESPONSES:
        grand = float(pin[response].mean())
        total_ss = float(np.square(pin[response] - grand).sum())
        means = {factor: pin.groupby(factor)[response].mean() for factor in FACTORS}
        fitted = np.full(len(pin), grand, dtype=float)

        for factor in FACTORS:
            multiplier = len(pin) // counts[factor]
            ss = multiplier * sum((float(means[factor].loc[level]) - grand) ** 2 for level in levels[factor])
            df = counts[factor] - 1
            fitted += pin[factor].map(means[factor]).to_numpy(float) - grand
            rows.append(_contribution_row(response, factor, ss, total_ss, df))

        for first, second in combinations(FACTORS, 2):
            pair_mean = pin.groupby([first, second])[response].mean()
            multiplier = len(pin) // (counts[first] * counts[second])
            ss = 0.0
            contribution = np.empty(len(pin), dtype=float)
            for pos, record in enumerate(pin[[first, second]].itertuples(index=False, name=None)):
                level_first, level_second = record
                effect = (
                    float(pair_mean.loc[level_first, level_second])
                    - float(means[first].loc[level_first])
                    - float(means[second].loc[level_second])
                    + grand
                )
                contribution[pos] = effect
            for level_first in levels[first]:
                for level_second in levels[second]:
                    effect = (
                        float(pair_mean.loc[level_first, level_second])
                        - float(means[first].loc[level_first])
                        - float(means[second].loc[level_second])
                        + grand
                    )
                    ss += multiplier * effect**2
            fitted += contribution
            df = (counts[first] - 1) * (counts[second] - 1)
            rows.append(_contribution_row(response, f"{first}x{second}", ss, total_ss, df))

        remainder = float(np.square(pin[response].to_numpy(float) - fitted).sum())
        remainder_df = int(np.prod([counts[factor] - 1 for factor in FACTORS]))
        rows.append(_contribution_row(response, "axb xN remainder".replace(" ", ""), remainder, total_ss, remainder_df))

    result = pd.DataFrame(rows)
    result["analysis_scope"] = "descriptive_unreplicated_factorial"
    result["residual_df"] = 0
    result["significance_test_allowed"] = False
    return result


def _contribution_row(response: str, effect: str, ss: float, total_ss: float, df: int) -> dict[str, float | int | str]:
    return {
        "response": response,
        "effect": effect,
        "sum_of_squares": float(ss),
        "contribution_ratio": float(ss / total_ss if total_ss else np.nan),
        "degrees_of_freedom": int(df),
    }


def main() -> None:
    pin = read_pin_data()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT / "q1_main_effects.csv": main_effects(pin),
        OUTPUT / "q1_interaction_effects.csv": interaction_effects(pin),
        OUTPUT / "q1_effect_contributions.csv": effect_contributions(pin),
    }
    for path, frame in outputs.items():
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"wrote {len(frame)} rows to {path}")


if __name__ == "__main__":
    main()
