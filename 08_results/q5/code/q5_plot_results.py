"""只读取Q5风险和灵敏度CSV生成工作图。"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data"
FIG = PACKAGE / "figures"


def configure() -> None:
    plt.rcParams.update({
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
    })


def heatmap(values: np.ndarray, rows: list[str], columns: list[str], path: Path, signed: bool) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    if signed:
        limit = max(.05, float(np.nanmax(np.abs(values))))
        image = ax.imshow(values, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    else:
        image = ax.imshow(np.abs(values), cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(columns)), columns)
    ax.set_yticks(range(len(rows)), rows)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            text = f"{values[i, j]:+.2f}" if signed else f"{abs(values[i, j]):.2f}"
            ax.text(j, i, text, ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="标准化回归系数")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure()
    FIG.mkdir(parents=True, exist_ok=True)

    risk = pd.read_csv(DATA / "q5_structure_risk_comparison.csv")
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    x = np.arange(len(risk))
    nominal = "C_nom" if "C_nom" in risk else "名义评分"
    cvar = "CVaR95_L20000" if "CVaR95_L20000" in risk else "CVaR95"
    ax.bar(x - .18, risk[nominal], width=.36, label="名义评分")
    ax.bar(x + .18, risk[cvar], width=.36, label="CVaR95")
    ax.set_xticks(x, risk["方案"], rotation=18, ha="right")
    ax.set_ylabel("固定尺度评分")
    ax.legend()
    ax.grid(axis="y", alpha=.22)
    fig.tight_layout()
    fig.savefig(FIG / "fig_q5_01_structure_risk.pdf", bbox_inches="tight")
    plt.close(fig)

    op = pd.read_csv(DATA / "q5_operation_design_comparison.csv")
    fig, ax = plt.subplots(figsize=(8.2, 4.1))
    labels = op["情景"].astype(str) + "-" + op["U模型"].astype(str)
    ax.plot(labels, op["最优CVaR"], "o-", label="情景专属最优")
    ax.plot(labels, op["结构鲁棒CVaR"], "s--", label="结构鲁棒方案")
    ax.set(ylabel="CVaR95", title="工况机理情景风险包络")
    ax.tick_params(axis="x", rotation=25)
    ax.legend()
    ax.grid(alpha=.22)
    fig.tight_layout()
    fig.savefig(FIG / "fig_q5_02_operation_envelope.pdf", bbox_inches="tight")
    plt.close(fig)

    struct = pd.read_csv(DATA / "q5_structure_src.csv")
    operation = pd.read_csv(DATA / "q5_operation_src_S2A.csv")
    values = np.vstack([
        struct[["R", "P", "U", "C_str"]].to_numpy(float),
        operation[["Theta_R", "P", "U", "C_op"]].to_numpy(float),
    ])
    rows = list(struct.iloc[:, 0].astype(str) + "（加工）") + list(operation.iloc[:, 0].astype(str) + "（工况）")
    heatmap(values, rows, ["热目标", "P", "U", "综合评分"], FIG / "fig_q5_03_sensitivity.pdf", signed=False)

    signed_path = DATA / "q5_signed_src.csv"
    if signed_path.exists():
        signed = pd.read_csv(signed_path, index_col=0)
        heatmap(signed.to_numpy(float), list(signed.index.astype(str)), list(signed.columns.astype(str)), FIG / "fig_q5_04_signed_sensitivity.pdf", signed=True)


if __name__ == "__main__":
    main()
