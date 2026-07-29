"""只读取Q1处理CSV并生成工作图。"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "03_data" / "processed" / "q1"
FIG = ROOT / "05_figures" / "q1"


def configure() -> None:
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
    })


def main() -> None:
    configure()
    FIG.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(DATA / "q1_response_data.csv")
    pin = data[data["N"] > 0].copy()

    fig, axes = plt.subplots(3, 3, figsize=(10.4, 8.2))
    for row, response in enumerate(["R", "P", "U"]):
        for col, variable in enumerate(["a", "b", "N"]):
            means = pin.groupby(variable, as_index=False)[response].mean()
            axes[row, col].plot(means[variable], means[response], "o-", color="#2563eb")
            axes[row, col].set(xlabel=variable, ylabel=response)
            axes[row, col].grid(alpha=.25)
    fig.suptitle("结构变量对三项无量纲响应的主效应")
    fig.tight_layout()
    fig.savefig(FIG / "fig_q1_01_main_effects.pdf", bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.35))
    pairs = [("R", "P"), ("R", "U"), ("P", "U")]
    scatter = None
    for ax, (x, y) in zip(axes, pairs):
        scatter = ax.scatter(pin[x], pin[y], c=pin["N"], cmap="viridis", s=28)
        ax.set(xlabel=x, ylabel=y)
        ax.grid(alpha=.22)
    fig.colorbar(scatter, ax=axes, label="N")
    fig.suptitle("三项性能之间的权衡关系")
    fig.subplots_adjust(left=.07, right=.88, bottom=.18, top=.84, wspace=.30)
    fig.savefig(FIG / "fig_q1_02_performance_tradeoff.pdf", bbox_inches="tight")
    plt.close(fig)

    anova_path = DATA / "q1_anova_contributions.csv"
    if anova_path.exists():
        anova = pd.read_csv(anova_path)
        numeric = anova.select_dtypes("number")
        labels = anova.iloc[:, 0].astype(str)
        if not numeric.empty:
            fig, ax = plt.subplots(figsize=(8.4, 4.3))
            numeric.plot(kind="bar", ax=ax)
            if len(labels) == len(numeric):
                ax.set_xticklabels(labels, rotation=25, ha="right")
            ax.set(ylabel="贡献量", title="主效应与交互项贡献")
            ax.grid(axis="y", alpha=.22)
            fig.tight_layout()
            fig.savefig(FIG / "fig_q1_03_anova_contributions.pdf", bbox_inches="tight")
            plt.close(fig)


if __name__ == "__main__":
    main()
