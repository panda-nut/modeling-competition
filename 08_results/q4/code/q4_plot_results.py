"""只读取Q4权重和遗憾CSV生成偏好图。"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data"
FIG = PACKAGE / "figures"


def main() -> None:
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
    })
    FIG.mkdir(parents=True, exist_ok=True)
    weights = pd.read_csv(DATA / "q4_weight_scan_H50.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0))
    scatter = axes[0].scatter(weights.w_R, weights.w_P, c=weights.N, s=8, cmap="viridis")
    axes[0].set(xlabel="$w_R$", ylabel="$w_P$", title="权重到最优排数")
    fig.colorbar(scatter, ax=axes[0], label="N")
    color = axes[1].scatter(weights.w_R, weights.w_U, c=weights.b, s=8, cmap="plasma")
    axes[1].set(xlabel="$w_R$", ylabel="$w_U$", title="权重到最优深高比")
    fig.colorbar(color, ax=axes[1], label="$b^*$")
    fig.tight_layout()
    fig.savefig(FIG / "fig_q4_01_weight_mapping.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
