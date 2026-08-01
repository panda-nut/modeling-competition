"""只读取Q3 CSV并生成Pareto、候选、切片和算法比较图。"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data"
FIG = PACKAGE / "figures"
RESP = ["R", "P", "U"]


def configure() -> None:
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
    })


def main() -> None:
    configure()
    FIG.mkdir(parents=True, exist_ok=True)
    ref_path = DATA / "q3_pareto_reference_merged.csv"
    if not ref_path.exists():
        ref_path = DATA / "q3_pareto_global.csv"
    ref = pd.read_csv(ref_path)

    fig = plt.figure(figsize=(10.6, 7.4))
    ax3 = fig.add_subplot(221, projection="3d")
    for n, group in ref.groupby("N"):
        ax3.scatter(group.R, group.P, group.U, s=8, label=f"N={int(n)}", alpha=.72)
    ax3.set(xlabel="R", ylabel="P", zlabel="U")
    ax3.legend(fontsize=7, ncol=2)
    for ax, (x, y) in zip(
        [fig.add_subplot(222), fig.add_subplot(223), fig.add_subplot(224)],
        [("R", "P"), ("R", "U"), ("P", "U")],
    ):
        for _, group in ref.groupby("N"):
            ax.scatter(group[x], group[y], s=8, alpha=.68)
        ax.set(xlabel=x, ylabel=y)
        ax.grid(alpha=.22)
    fig.tight_layout()
    fig.savefig(FIG / "fig_q3_01_pareto_front.pdf", bbox_inches="tight")
    plt.close(fig)

    candidates = pd.read_csv(DATA / "q3_compromise_candidates.csv")
    values = candidates[RESP].to_numpy(float)
    lo, hi = values.min(axis=0), values.max(axis=0)
    scaled = (values - lo) / np.where(hi > lo, hi - lo, 1)
    fig, ax = plt.subplots(figsize=(9.0, 4.2))
    for i, row in enumerate(scaled):
        ax.plot(range(3), row, marker="o", label=str(candidates.iloc[i, 0]))
    ax.set_xticks(range(3), RESP)
    ax.set_ylabel("候选集内归一化性能")
    ax.grid(alpha=.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig_q3_02_candidate_comparison.pdf", bbox_inches="tight")
    plt.close(fig)

    ideal, nadir = ref[RESP].min().to_numpy(), ref[RESP].max().to_numpy()
    span = np.where(nadir > ideal, nadir - ideal, 1)
    score = ((ref[RESP].to_numpy() - ideal) / span).max(axis=1)
    ref = ref.assign(score=score)
    best_n = int(candidates.loc[candidates["C_AT"].idxmin(), "N"]) if "C_AT" in candidates else int(ref.loc[ref.score.idxmin(), "N"])
    layer = ref[np.isclose(ref.N, best_n)]
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    points = ax.scatter(layer.a, layer.b, c=layer.score, cmap="YlGnBu", s=12)
    fig.colorbar(points, ax=ax, label="固定尺度评分")
    ax.set(xlabel="a", ylabel="b", title=f"N={best_n} 的Pareto评分分布")
    ax.grid(alpha=.18)
    fig.tight_layout()
    fig.savefig(FIG / "fig_q3_03_design_slice.pdf", bbox_inches="tight")
    plt.close(fig)

    metrics_path = DATA / "q3_algorithm_metrics_exact.csv"
    if not metrics_path.exists():
        metrics_path = DATA / "q3_algorithm_metrics.csv"
    metrics = pd.read_csv(metrics_path)
    grid = metrics[metrics["method"].astype(str).str.contains("网格")]
    nsga = metrics[metrics["method"].astype(str).str.contains("NSGA")]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.25))
    if len(grid):
        axes[0].plot(range(len(grid)), grid.HV, "o-", color="#2563eb")
        axes[0].set_xticks(range(len(grid)), grid.method, rotation=20)
    axes[0].set(ylabel="HV", title="网格收敛")
    axes[0].grid(alpha=.25)
    if len(nsga):
        axes[1].boxplot(nsga.HV)
        axes[2].boxplot(nsga.IGD_plus)
    axes[1].set(ylabel="HV", title="NSGA-II重复超体积")
    axes[2].set(ylabel="IGD+", title="NSGA-II逼近误差")
    fig.tight_layout()
    fig.savefig(FIG / "fig_q3_04_algorithm_comparison.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
