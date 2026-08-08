"""读取 Q1 结果数据并生成统一编号的分析图。"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data"
FIGURE = PACKAGE / "figures"
RESPONSES = ("R", "P", "U")
FACTORS = ("a", "b", "N")


def configure() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "font.size": 9,
        }
    )


def save_both(figure: plt.Figure, stem: str) -> None:
    for extension in ("pdf", "png"):
        figure.savefig(FIGURE / f"{stem}.{extension}", bbox_inches="tight", dpi=220)
    plt.close(figure)


def plot_main_effects(main_effects: pd.DataFrame) -> None:
    figure, axes = plt.subplots(3, 3, figsize=(10.6, 8.3), sharey="row")
    for row, response in enumerate(RESPONSES):
        for column, factor in enumerate(FACTORS):
            axis = axes[row, column]
            subset = main_effects[(main_effects.response == response) & (main_effects.factor == factor)].sort_values("level")
            axis.plot(subset.level, subset.relative_deviation_pct, "o-", color="#2563eb", linewidth=1.6)
            axis.axhline(0.0, color="#6b7280", linewidth=0.8)
            axis.set(xlabel=factor, ylabel=f"{response} 相对偏差 (%)")
            axis.grid(alpha=0.24)
    figure.suptitle("结构变量对三项响应的主效应（相对总体均值）")
    figure.tight_layout()
    save_both(figure, "fig_q1_01_main_effects")


def plot_tradeoffs(response_data: pd.DataFrame) -> None:
    pin = response_data[response_data.N > 0].copy()
    baseline = response_data[response_data.N == 0].copy()
    pairs = (("R", "P"), ("R", "U"), ("P", "U"))
    figure, axes = plt.subplots(1, 3, figsize=(10.8, 3.55))
    scatter = None
    for axis, (first, second) in zip(axes, pairs):
        scatter = axis.scatter(pin[first], pin[second], c=pin.N, cmap="viridis", s=27, alpha=0.82, label="有针肋")
        axis.scatter(
            baseline[first],
            baseline[second],
            marker="*",
            s=115,
            color="#dc2626",
            edgecolor="white",
            linewidth=0.7,
            label="无针肋基线",
            zorder=4,
        )
        for record in baseline.itertuples(index=False):
            axis.annotate(f"b={record.b:g}", (getattr(record, first), getattr(record, second)), xytext=(4, 3), textcoords="offset points", fontsize=7)
        axis.set(xlabel=first, ylabel=second)
        axis.grid(alpha=0.22)
    if scatter is not None:
        figure.colorbar(scatter, ax=axes, label="N", fraction=0.025, pad=0.025)
    axes[0].legend(loc="best", fontsize=8)
    figure.suptitle("有针肋样本与无针肋退化基线的性能权衡")
    figure.subplots_adjust(left=0.065, right=0.90, bottom=0.17, top=0.84, wspace=0.30)
    save_both(figure, "fig_q1_02_performance_tradeoff")


def plot_contributions(contributions: pd.DataFrame) -> None:
    order = ("a", "b", "N", "axb", "axN", "bxN", "axbxNremainder")
    labels = {"a": "a", "b": "b", "N": "N", "axb": "a×b", "axN": "a×N", "bxN": "b×N", "axbxNremainder": "三阶余项"}
    figure, axes = plt.subplots(1, 3, figsize=(11.0, 3.8), sharey=True)
    for axis, response in zip(axes, RESPONSES):
        subset = contributions[contributions.response == response].set_index("effect").reindex(order)
        values = 100.0 * subset.contribution_ratio.to_numpy(float)
        axis.bar(np.arange(len(order)), values, color="#2a9d8f")
        axis.set_xticks(np.arange(len(order)), [labels[item] for item in order], rotation=35, ha="right")
        axis.set(title=response, ylabel="描述性平方和贡献 (%)")
        axis.grid(axis="y", alpha=0.22)
    figure.suptitle("无重复全因子设计的描述性效应贡献（不作显著性检验）")
    figure.tight_layout()
    save_both(figure, "fig_q1_03_effect_contributions")


def plot_interactions(interactions: pd.DataFrame) -> None:
    panels = (("R", "a", "N"), ("R", "b", "N"), ("P", "a", "N"), ("U", "a", "b"))
    figure, axes = plt.subplots(2, 2, figsize=(9.5, 7.2))
    for axis, (response, first, second) in zip(axes.ravel(), panels):
        subset = interactions[
            (interactions.response == response)
            & (interactions.factor_first == first)
            & (interactions.factor_second == second)
        ]
        for level, group in subset.groupby("level_second", sort=True):
            group = group.sort_values("level_first")
            axis.plot(group.level_first, group.cell_mean, marker="o", linewidth=1.4, label=f"{second}={level:g}")
        axis.set(xlabel=first, ylabel=f"条件均值 {response}", title=f"{response}: {first}×{second}")
        axis.grid(alpha=0.22)
        axis.legend(fontsize=7, ncol=2)
    figure.suptitle("关键二阶交互的条件均值曲线")
    figure.tight_layout()
    save_both(figure, "fig_q1_04_interaction_effects")


def main() -> None:
    configure()
    FIGURE.mkdir(parents=True, exist_ok=True)
    main_effects = pd.read_csv(DATA / "q1_main_effects.csv")
    interactions = pd.read_csv(DATA / "q1_interaction_effects.csv")
    contributions = pd.read_csv(DATA / "q1_effect_contributions.csv")
    response_data = pd.read_csv(DATA / "q1_response_data.csv")
    plot_main_effects(main_effects)
    plot_tradeoffs(response_data)
    plot_contributions(contributions)
    plot_interactions(interactions)
    print("wrote Q1 PDF and PNG figures")


if __name__ == "__main__":
    main()
