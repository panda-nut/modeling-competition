"""APMCM B题问题3：分段代理模型下的多目标优化。

命名沿用问题2的“q3_功能”风格。程序从附件2重新拟合问题2确定的
三次 Ridge 模型，并把无针肋数据作为独立 PCHIP 支路处理。
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.interpolate import PchipInterpolator
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "question3"
DATA = OUT / "data"; FIG = OUT / "figures"; LOG = OUT / "logs"
SOURCE = ROOT / "B题 高性能芯片热管理系统的优化问题（原题+题目附件）" / "附件" / "附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx"
N_LEVELS = np.array([2, 4, 6, 8, 10], dtype=float)
RESP = ["R", "P", "U"]


def read_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(SOURCE, header=1)
    raw.columns = ["id", "a", "b", "N", "R", "P", "U"]
    raw = raw.apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    return raw[raw.N > 0].copy(), raw[raw.N == 0].copy()


def build_surrogate(pin: pd.DataFrame, base: pd.DataFrame):
    x = pin[["a", "b", "N"]].to_numpy(float)
    # 问题2的最终设定：输入标准化 -> 完整三次基 -> 特征标准化 -> Ridge。
    ridge = {}
    for y, alpha in zip(RESP, [1e-5, 1e-2, 1e-3]):
        ridge[y] = make_pipeline(StandardScaler(), PolynomialFeatures(3, include_bias=False),
                                 StandardScaler(), Ridge(alpha=alpha)).fit(x, pin[y])
    pchip = {y: PchipInterpolator(base.b.to_numpy(float), base[y].to_numpy(float)) for y in RESP}
    return ridge, pchip


def predict(x: np.ndarray, ridge, pchip) -> np.ndarray:
    """批量分段预测；x 的列依次为 a,b,N。"""
    x = np.asarray(x, dtype=float)
    ans = np.empty((len(x), 3))
    base = (np.isclose(x[:, 0], 0) & np.isclose(x[:, 2], 0))
    if base.any():
        ans[base] = np.column_stack([pchip[y](x[base, 1]) for y in RESP])
    if (~base).any():
        ans[~base] = np.column_stack([ridge[y].predict(x[~base]) for y in RESP])
    return ans


def nondominated(f: np.ndarray, tol: float = 1e-11) -> np.ndarray:
    """三目标最小化的 O(n log n) 扫描，返回非支配点布尔掩码。"""
    if f.shape[1] == 2:
        order = np.lexsort((f[:, 1], f[:, 0])); keep = np.zeros(len(f), dtype=bool); best = np.inf
        for idx in order:
            if f[idx, 1] < best - tol:
                keep[idx] = True; best = f[idx, 1]
        return keep
    order = np.lexsort((f[:, 2], f[:, 1], f[:, 0]))
    pvals = np.unique(f[:, 1]); m = len(pvals)
    tree = np.full(m + 2, np.inf)
    keep = np.zeros(len(f), dtype=bool)
    for idx in order:
        pos = np.searchsorted(pvals, f[idx, 1]) + 1
        q, best = pos, np.inf
        while q:
            best = min(best, tree[q]); q -= q & -q
        if best > f[idx, 2] + tol:
            keep[idx] = True
        q = pos
        while q <= m:
            tree[q] = min(tree[q], f[idx, 2]); q += q & -q
    return keep


def grid_search(ridge, pchip, n_grid: int = 401) -> tuple[np.ndarray, np.ndarray, dict]:
    a = np.linspace(.10, .30, n_grid); b = np.linspace(3., 4.5, n_grid)
    aa, bb = np.meshgrid(a, b, indexing="ij")
    designs, values = [], []
    layers = {}
    for n in N_LEVELS:
        x = np.column_stack([aa.ravel(), bb.ravel(), np.full(aa.size, n)])
        f = predict(x, ridge, pchip); take = nondominated(f)
        designs.append(x[take]); values.append(f[take])
        layers[str(int(n))] = int(take.sum())
    x0 = np.column_stack([np.zeros(2001), np.linspace(3., 4.5, 2001), np.zeros(2001)])
    f0 = predict(x0, ridge, pchip); take0 = nondominated(f0)
    designs.append(x0[take0]); values.append(f0[take0])
    x, f = np.vstack(designs), np.vstack(values)
    take = nondominated(f)
    return x[take], f[take], {"grid": n_grid, "layer_nondominated": layers, "baseline_kept": int(take0.sum())}


def anchors(x, f):
    ids = np.argmin(f, axis=0)
    ideal = f[ids, np.arange(3)]
    nadir = f[ids].max(axis=0)
    return ids, ideal, nadir


def normalize(f, ideal, nadir):
    return (f - ideal) / np.maximum(nadir - ideal, 1e-12)


def hypervolume3(z: np.ndarray, ref=np.array([1.10, 1.10, 1.10])) -> float:
    # 精确切片计算三维 HV；候选前沿通常很小。
    z = z[np.all(z < ref, axis=1)]
    if len(z) == 0: return 0.0
    z = z[nondominated(z)]
    xs = np.unique(np.r_[z[:, 0], ref[0]]); hv = 0.0
    for lo, hi in zip(xs[:-1], xs[1:]):
        yz = z[z[:, 0] <= lo][:, 1:]
        if not len(yz): continue
        yz = yz[nondominated(yz)]
        yy = np.unique(np.r_[yz[:, 0], ref[1]])
        area = 0.0
        for yl, yh in zip(yy[:-1], yy[1:]):
            us = yz[yz[:, 0] <= yl, 1]
            area += (yh - yl) * max(0.0, ref[2] - np.min(us))
        hv += (hi - lo) * area
    return float(hv)


def candidate_table(x, f, pin, ideal, nadir):
    z = normalize(f, ideal, nadir); score = z.max(1) + 1e-4 * z.sum(1); l2 = np.sqrt((z*z).mean(1))
    labels = ["最小热阻锚点", "最小压降锚点", "最小非均匀性锚点", "连续综合最优", "最近理想点"]
    ind = list(np.argmin(f, 0)) + [int(np.argmin(score)), int(np.argmin(l2))]
    # 原始有针肋样本按同一折中准则加入。
    sf = pin[RESP].to_numpy(float); sz = normalize(sf, ideal, nadir)
    si = int(np.argmin(sz.max(1) + 1e-4*sz.sum(1)))
    px = pin.iloc[si][["a", "b", "N"]].to_numpy(float)
    rows = []
    for lab, i in zip(labels, ind): rows.append([lab, *x[i], *f[i], score[i], l2[i]])
    rows.append(["最佳原始样本", *px, *sf[si], sz[si].max()+1e-4*sz[si].sum(), np.sqrt((sz[si]**2).mean())])
    columns = ["方案", "a", "b", "N", "R", "P", "U", "C_AT", "C2"]
    return pd.DataFrame(rows, columns=columns), int(np.argmin(score))


def make_figures(x, f, candidates, ideal, nadir):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei", "SimHei", "DejaVu Sans"], "axes.unicode_minus":False, "font.size":9})
    z = normalize(f, ideal, nadir); colors = {2:"#2563eb",4:"#0891b2",6:"#16a34a",8:"#d97706",10:"#dc2626",0:"#6b7280"}
    fig = plt.figure(figsize=(10.6, 7.4)); ax3 = fig.add_subplot(221, projection="3d")
    for n in [0,2,4,6,8,10]:
        q = np.isclose(x[:,2], n); ax3.scatter(f[q,0],f[q,1],f[q,2],s=10,c=colors[n],label=f"N={n}",alpha=.78)
    ax3.set(xlabel="R",ylabel="P",zlabel="U"); ax3.legend(fontsize=7, ncol=2)
    for ax,(i,j),name in zip([fig.add_subplot(222),fig.add_subplot(223),fig.add_subplot(224)],[(0,1),(0,2),(1,2)],["R-P","R-U","P-U"]):
        for n in [0,2,4,6,8,10]:
            q=np.isclose(x[:,2],n); ax.scatter(f[q,i],f[q,j],s=10,c=colors[n],alpha=.8)
        ax.set(xlabel=name.split('-')[0],ylabel=name.split('-')[1]); ax.grid(alpha=.22)
    fig.tight_layout(); fig.savefig(FIG/"q3_pareto_combined.pdf",bbox_inches="tight"); plt.close(fig)
    # 平行坐标：选择表中核心候选，使用统一标尺。
    fig, ax = plt.subplots(figsize=(9.0,4.2)); vals=normalize(candidates[RESP].to_numpy(float),ideal,nadir)
    for i,row in enumerate(vals): ax.plot(range(3),row,marker="o",lw=1.4,label=candidates.iloc[i,0])
    ax.set_xticks(range(3),["R","P","U"]); ax.set_ylabel("统一归一化性能"); ax.grid(alpha=.25); ax.legend(ncol=2,fontsize=8); fig.tight_layout(); fig.savefig(FIG/"q3_compromise_parallel.pdf",bbox_inches="tight"); plt.close(fig)
    # 最终点所属 N 切片的折中评分图。
    best=candidates[candidates["方案"]=="连续综合最优"].iloc[0]; n=best.N
    aa=np.linspace(.1,.3,151); bb=np.linspace(3,4.5,151); A,B=np.meshgrid(aa,bb,indexing="ij")
    xx=np.column_stack([A.ravel(),B.ravel(),np.full(A.size,n)]); zz=normalize(predict(xx, RIDGE, PCHIP),ideal,nadir); s=zz.max(1)+1e-4*zz.sum(1)
    fig,ax=plt.subplots(figsize=(6.4,4.8)); cf=ax.contourf(A,B,s.reshape(A.shape),levels=18,cmap="YlGnBu"); fig.colorbar(cf,ax=ax,label="$C_{AT}$")
    q=np.isclose(x[:,2],n); ax.scatter(x[q,0],x[q,1],s=6,c="white",alpha=.65,label="该层Pareto点"); ax.scatter([best.a],[best.b],marker="*",s=170,c="#dc2626",edgecolors="white",label="综合最优")
    ax.set(xlabel="a",ylabel="b",title=f"N={int(n)} 的综合评分切片"); ax.legend(); fig.tight_layout(); fig.savefig(FIG/"q3_final_design_slice.pdf",bbox_inches="tight"); plt.close(fig)


def write_tex(summary, candidates, payoff):
    best = candidates[candidates["方案"]=="连续综合最优"].iloc[0]
    def table(df):
        rows=[]
        for _,r in df.iterrows():
            rows.append(f"{r['方案']} & {r.a:.4f} & {r.b:.4f} & {int(r.N)} & {r.R:.6f} & {r.P:.6f} & {r.U:.6f} & {r.C_AT:.4f} \\\\")
        return "\n".join(rows)
    tex=f'''\\documentclass[UTF8,a4paper,11pt]{{ctexart}}
\\usepackage{{geometry,booktabs,float,graphicx,amsmath,siunitx}}
\\geometry{{margin=2.15cm}}\\title{{APMCM B题问题3：芯片热管理结构的多目标优化}}\\author{{}}\\date{{}}
\\begin{{document}}\\maketitle
\\section{{模型与求解方法}} 本文继承问题2的分段代理模型：有针肋区域以标准化输入、完整三次多项式及Ridge正则化构成响应面；无针肋$(a,N)=(0,0)$支路以PCHIP插值单独处理。故在$0.10\\le a\\le0.30,3\\le b\\le4.5,N\\in\\{{2,4,6,8,10\\}}$及无针肋支路的并集上，同时最小化无量纲热阻$R$、压降$P$和温度非均匀性$U$。

对五个离散$N$水平分别以$401\\times401$致密网格搜索，所有候选经三目标非支配筛选后与2001点无针肋PCHIP支路合并。三个单目标锚点确定理想点，锚点收益矩阵给出初始Nadir尺度；最终参考前沿的覆盖检查未改变该尺度。综合决策采用等权增强切比雪夫评分
\\[C_{{AT}}=\\max(z_R,z_P,z_U)+10^{{-4}}(z_R+z_P+z_U),\\quad z_k=(F_k-F_k^I)/(F_k^N-F_k^I).\\]
\\section{{结果与综合方案}} 本次确定性搜索得到全局Pareto点{summary['pareto_points']}个；无针肋支路在全局合并后保留{summary['baseline_global_points']}个点。连续综合最优为$a={best.a:.4f}$，$b={best.b:.4f}$，$N={int(best.N)}$，预测$(R,P,U)=({best.R:.6f},{best.P:.6f},{best.U:.6f})$。它位于代理模型合法域内，且为全局非支配解。
\\begin{{table}}[H]\\centering\\caption{{单目标锚点与折中方案比较}}\\small
\\begin{{tabular}}{{lrrrrrrr}}\\toprule 方案&a&b&N&R&P&U&$C_{{AT}}$\\\\\\midrule
{table(candidates)}\\\\\\bottomrule\\end{{tabular}}\\end{{table}}
\\begin{{figure}}[H]\\centering\\includegraphics[width=.94\\linewidth]{{figures/q3_pareto_combined.pdf}}\\caption{{全局Pareto前沿及两两投影}}\\end{{figure}}
\\begin{{figure}}[H]\\centering\\includegraphics[width=.86\\linewidth]{{figures/q3_compromise_parallel.pdf}}\\caption{{候选方案的统一归一化比较}}\\end{{figure}}
\\begin{{figure}}[H]\\centering\\includegraphics[width=.68\\linewidth]{{figures/q3_final_design_slice.pdf}}\\caption{{综合最优点所在排数层的局部评分}}\\end{{figure}}
\\section{{结论}} 三个目标的冲突使单一极端点不可作为综合设计。等权增强切比雪夫准则选择的方案控制了最大标准化退让；它可作为名义工况基准，权重变化和扰动鲁棒性应在后续问题中另行分析。\\end{{document}}'''
    (OUT/"APMCM_B题_问题3_多目标优化.tex").write_text(tex,encoding="utf-8")


def main():
    global RIDGE, PCHIP
    for d in [DATA,FIG,LOG]: d.mkdir(parents=True,exist_ok=True)
    pin, base=read_data(); RIDGE,PCHIP=build_surrogate(pin,base)
    t=time.perf_counter(); x,f,grid_meta=grid_search(RIDGE,PCHIP); elapsed=time.perf_counter()-t
    ids,ideal,nadir=anchors(x,f); nadir=np.maximum(nadir,f.max(0))
    z=normalize(f,ideal,nadir); take=nondominated(f); x,f,z=x[take],f[take],z[take]
    pd.DataFrame(np.c_[x,f],columns=["a","b","N","R","P","U"]).to_csv(DATA/"pareto_global.csv",index=False)
    payoff=pd.DataFrame(f[ids],index=["R锚点","P锚点","U锚点"],columns=RESP); payoff.to_csv(DATA/"payoff_matrix.csv",encoding="utf-8-sig")
    candidates,best_i=candidate_table(x,f,pin,ideal,nadir); candidates.to_csv(DATA/"compromise_candidates.csv",index=False,encoding="utf-8-sig")
    summary={"grid_search_seconds":elapsed,"grid_meta":grid_meta,"pareto_points":int(len(f)),"baseline_global_points":int(np.sum(x[:,2]==0)),"ideal":ideal.tolist(),"nadir":nadir.tolist(),"hypervolume":hypervolume3(z),"best_index":best_i}
    (LOG/"optimization_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    make_figures(x,f,candidates,ideal,nadir); write_tex(summary,candidates,payoff)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
