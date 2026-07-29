"""问题3定稿计算：合并参考集、精确三维HV、连续精化与定稿绘图。"""
from __future__ import annotations

import bisect
import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize, minimize_scalar

import q3_multiobjective_optimization as q3
import q3_candidate_algorithm_comparison as cmp

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "03_data" / "processed" / "q3"
FIG = ROOT / "05_figures" / "q3"
LOG = ROOT / "00_progress" / ".working" / "logs" / "q3"
REF_POINT = np.array([1.1, 1.1, 1.1])


def exact_hv3(points, ref=REF_POINT):
    """精确三维超体积：沿第一目标扫描，二维截面作矩形并集。"""
    p = np.asarray(points, float)
    p = p[np.all(p < ref, axis=1)]
    if not len(p): return 0.0
    p = p[q3.nondominated(p)]
    order = np.argsort(p[:, 0], kind="mergesort"); p = p[order]
    ys, zs = [], []

    def insert(y, z):
        pos = bisect.bisect_left(ys, y)
        if pos > 0 and zs[pos-1] <= z + 1e-14: return
        if pos < len(ys) and abs(ys[pos]-y) < 1e-14:
            if zs[pos] <= z + 1e-14: return
            ys.pop(pos); zs.pop(pos)
        while pos < len(ys) and zs[pos] >= z - 1e-14:
            ys.pop(pos); zs.pop(pos)
        ys.insert(pos, y); zs.insert(pos, z)

    def area2():
        if not ys: return 0.0
        return sum(((ys[i+1] if i+1 < len(ys) else ref[1]) - ys[i]) *
                   (ref[2] - zs[i]) for i in range(len(ys)))

    hv = 0.0; i = 0
    while i < len(p):
        x = p[i, 0]
        while i < len(p) and abs(p[i, 0] - x) < 1e-14:
            insert(p[i, 1], p[i, 2]); i += 1
        nx = p[i, 0] if i < len(p) else ref[0]
        hv += max(0.0, nx-x) * area2()
    return float(hv)


def igd_plus(ref, approx):
    """完整合并参考集到候选集的IGD+，分块避免大矩阵驻留内存。"""
    total = 0.0
    for i in range(0, len(ref), 80):
        rr = ref[i:i+80]
        best = np.full(len(rr), np.inf)
        for j in range(0, len(approx), 1500):
            d = np.sqrt(np.sum(np.maximum(approx[None, j:j+1500, :] - rr[:, None, :], 0)**2, axis=2))
            best = np.minimum(best, np.min(d, axis=1))
        total += best.sum()
    return float(total / len(ref))


def spacing(z):
    if len(z) < 2: return 0.0
    d = []
    for i in range(0, len(z), 100):
        best=np.full(min(100,len(z)-i),np.inf)
        for j in range(0,len(z),1500):
            dd=np.sqrt(np.sum((z[i:i+100,None,:]-z[None,j:j+1500,:])**2,axis=2))
            dd[dd<1e-14]=np.inf; best=np.minimum(best,np.min(dd,axis=1))
        d.extend(best)
    return float(np.std(d,ddof=1))


def score_f(f, ideal, nadir):
    z=(np.asarray(f)-ideal)/(nadir-ideal)
    return np.max(z,axis=-1)+1e-4*np.sum(z,axis=-1)


def continuous_refinement(ridge,pchip,ideal,nadir,grid,nsga):
    rows=[]
    for n in q3.N_LEVELS:
        candidates=[]
        for source in [grid,nsga]:
            d=source[np.isclose(source.N,n)]
            if len(d):
                f=d[q3.RESP].to_numpy(); candidates.append(d.iloc[np.argmin(score_f(f,ideal,nadir))][["a","b"]].to_numpy(float))
        def obj(v): return float(score_f(q3.predict(np.array([[v[0],v[1],n]]),ridge,pchip)[0],ideal,nadir))
        de=differential_evolution(obj,[(.1,.3),(3,4.5)],seed=7300+int(n),tol=1e-11,popsize=12,maxiter=220,polish=False)
        starts=candidates+[de.x,np.array([.2,3.75]),np.array([.225,4.5])]
        sols=[minimize(obj,s,method="SLSQP",bounds=[(.1,.3),(3,4.5)],options={"ftol":1e-14,"maxiter":1000}) for s in starts]
        best=min(sols,key=lambda r:r.fun); x=np.array([best.x[0],best.x[1],n]); f=q3.predict(x[None,:],ridge,pchip)[0]
        rows.append([f"N={int(n)}连续精化",*x,*f,float(best.fun)])
    def obj0(b): return float(score_f(q3.predict(np.array([[0,float(b),0]]),ridge,pchip)[0],ideal,nadir))
    b0=minimize_scalar(obj0,bounds=(3,4.5),method="bounded",options={"xatol":1e-13}).x
    x=np.array([0,b0,0]); f=q3.predict(x[None,:],ridge,pchip)[0]
    rows.append(["无针肋连续精化",*x,*f,obj0(b0)])
    return pd.DataFrame(rows,columns=["方案","a","b","N","R","P","U","C_AT"])


def make_nsga_runs(ridge,pchip):
    all_rows=[]
    for seed in range(202601,202621):
        rng=np.random.default_rng(seed); xs=[];fs=[]
        for n in q3.N_LEVELS:
            x,f,_=cmp.nsga_slice(rng,n,ridge,pchip); xs.append(x);fs.append(f)
        x=np.vstack(xs);f=np.vstack(fs);take=q3.nondominated(f)
        for row in np.c_[x[take],f[take]]: all_rows.append([seed,*row])
    ans=pd.DataFrame(all_rows,columns=["seed","a","b","N","R","P","U"])
    ans.to_csv(DATA/"q3_nsga2_runs.csv",index=False); return ans


def plot_pareto(ref_df, base_df, anchors, final):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","SimHei","DejaVu Sans"],"axes.unicode_minus":False,"font.size":9})
    colors={2:"#2563eb",4:"#0891b2",6:"#16a34a",8:"#d97706",10:"#dc2626"}
    f=ref_df[q3.RESP].to_numpy(); x=ref_df[["a","b","N"]].to_numpy()
    fig=plt.figure(figsize=(10.6,7.4)); ax3=fig.add_subplot(221,projection="3d")
    for n in q3.N_LEVELS:
        m=np.isclose(x[:,2],n); ax3.scatter(f[m,0],f[m,1],f[m,2],s=8,c=colors[int(n)],label=f"N={int(n)}",alpha=.72)
    af=anchors[q3.RESP].to_numpy(); ff=final[q3.RESP].to_numpy(float)
    for row,c,lab in zip(af,["#111827","#7c3aed","#e11d48"],["最小R锚点","最小P锚点","最小U锚点"]):
        ax3.scatter(*row,marker="*",s=90,c=c,edgecolors="white",label=lab)
    ax3.scatter(*ff,marker="*",s=150,c="#facc15",edgecolors="#111827",label="综合方案")
    bf=base_df[q3.RESP].to_numpy()[::25]
    ax3.scatter(bf[:,0],bf[:,1],bf[:,2],s=13,c="#6b7280",marker="x",alpha=.45,label="被支配无针肋")
    ax3.set(xlabel="R",ylabel="P",zlabel="U"); ax3.legend(fontsize=7,ncol=2)
    pairs=[(0,1),(0,2),(1,2)]; names=[("R","P"),("R","U"),("P","U")]
    for ax,(i,j),(lx,ly) in zip([fig.add_subplot(222),fig.add_subplot(223),fig.add_subplot(224)],pairs,names):
        for n in q3.N_LEVELS:
            m=np.isclose(x[:,2],n);ax.scatter(f[m,i],f[m,j],s=8,c=colors[int(n)],alpha=.72)
        # 被支配无针肋支路用灰叉单独展示，不进入Pareto图例的N层。
        bf=base_df[q3.RESP].to_numpy()[::10];ax.scatter(bf[:,i],bf[:,j],s=10,c="#6b7280",marker="x",alpha=.32)
        ax.scatter(af[:,i],af[:,j],marker="*",s=85,c=["#111827","#7c3aed","#e11d48"],edgecolors="white",linewidths=.5)
        ax.scatter(ff[i],ff[j],marker="*",s=145,c="#facc15",edgecolors="#111827",linewidths=.7)
        ax.set(xlabel=lx,ylabel=ly);ax.grid(alpha=.22)
    fig.tight_layout();fig.savefig(FIG/"fig_q3_01_pareto_front.pdf",bbox_inches="tight");plt.close(fig)


def plot_slice(ridge,pchip,ideal,nadir,ref_df,final):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","SimHei","DejaVu Sans"],"axes.unicode_minus":False,"font.size":9})
    a=np.linspace(.1,.3,181);b=np.linspace(3,4.5,181);A,B=np.meshgrid(a,b,indexing="ij")
    x=np.c_[A.ravel(),B.ravel(),np.full(A.size,final.N)];f=q3.predict(x,ridge,pchip);s=score_f(f,ideal,nadir).reshape(A.shape)
    fig,ax=plt.subplots(figsize=(6.4,4.8));cf=ax.contourf(A,B,s,levels=22,cmap="YlGnBu");fig.colorbar(cf,ax=ax,label="$C_{AT}$")
    d=ref_df[np.isclose(ref_df.N,final.N)].sort_values(["a","b"]).iloc[::20]
    ax.scatter(d.a,d.b,s=7,facecolors="none",edgecolors="#111827",linewidths=.35,alpha=.24,label="该层Pareto点（稀疏显示）")
    ax.scatter([final.a],[final.b],marker="*",s=190,c="#dc2626",edgecolors="white",linewidths=.8,clip_on=False,zorder=10,label="连续精化最优")
    ax.set(xlabel="a",ylabel="b",title=f"N={int(final.N)} 的综合评分切片",xlim=(.1,.3),ylim=(3,4.5));ax.margins(y=.025);ax.legend()
    fig.tight_layout();fig.savefig(FIG/"fig_q3_03_design_slice.pdf",bbox_inches="tight");plt.close(fig)


def plot_algorithm_comparison(metrics):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","SimHei","DejaVu Sans"],"axes.unicode_minus":False,"font.size":9})
    g=metrics[metrics.run==0];ns=metrics[metrics.method=="分层 NSGA-II"]
    fig,axs=plt.subplots(1,3,figsize=(10.8,3.25))
    axs[0].plot([101,201,401],g.HV,"o-",color="#2563eb");axs[0].set(xlabel="网格边长",ylabel="精确HV",title="网格收敛");axs[0].grid(alpha=.25)
    axs[1].boxplot(ns.HV,tick_labels=["NSGA-II"]);axs[1].axhline(g.iloc[-1].HV,color="#dc2626",ls="--",label="401网格");axs[1].set(ylabel="精确HV",title="20次重复的超体积");axs[1].legend(fontsize=8)
    axs[2].boxplot(ns.IGD_plus,tick_labels=["NSGA-II"]);axs[2].axhline(g.iloc[-1].IGD_plus,color="#dc2626",ls="--",label="401网格");axs[2].set(ylabel="IGD+",title="到合并参考集的距离");axs[2].legend(fontsize=8)
    fig.tight_layout();fig.savefig(FIG/"fig_q3_04_algorithm_comparison.pdf",bbox_inches="tight");plt.close(fig)


def main():
    pin,base=q3.read_data();ridge,pchip=q3.build_surrogate(pin,base)
    grid_sets={}
    for ng in [101,201,401]:
        x,f,_=q3.grid_search(ridge,pchip,ng); grid_sets[ng]=pd.DataFrame(np.c_[x,f],columns=["a","b","N","R","P","U"])
    grid=grid_sets[401]
    ids,ideal,nadir=q3.anchors(grid[["a","b","N"]].to_numpy(),grid[q3.RESP].to_numpy());nadir=np.maximum(nadir,grid[q3.RESP].to_numpy().max(0))
    nsruns=make_nsga_runs(ridge,pchip); nsall=nsruns.drop(columns="seed")
    nstake=q3.nondominated(nsall[q3.RESP].to_numpy());nsnd=nsall[nstake].reset_index(drop=True)
    local=continuous_refinement(ridge,pchip,ideal,nadir,grid,nsnd);local.to_csv(DATA/"q3_local_refinement.csv",index=False,encoding="utf-8-sig")
    union=pd.concat([grid,nsnd,local[["a","b","N","R","P","U"]]],ignore_index=True)
    take=q3.nondominated(union[q3.RESP].to_numpy());ref=union[take].reset_index(drop=True);ref.to_csv(DATA/"q3_pareto_reference_merged.csv",index=False)
    refz=q3.normalize(ref[q3.RESP].to_numpy(),ideal,nadir)
    rows=[]
    for ng,d in grid_sets.items():
        z=q3.normalize(d[q3.RESP].to_numpy(),ideal,nadir);rows.append([f"分层网格 {ng}x{ng}",0,len(d),exact_hv3(z),igd_plus(refz,z),spacing(z),5*ng*ng+2001])
    for seed,d in nsruns.groupby("seed"):
        z=q3.normalize(d[q3.RESP].to_numpy(),ideal,nadir);rows.append(["分层 NSGA-II",seed,len(d),exact_hv3(z),igd_plus(refz,z),spacing(z),5*60*51])
    metrics=pd.DataFrame(rows,columns=["method","run","points","HV","IGD_plus","Spacing","evaluations"]);metrics.to_csv(DATA/"q3_algorithm_metrics_exact.csv",index=False,encoding="utf-8-sig")
    final=local.iloc[np.argmin(local.C_AT)]
    bgrid=np.linspace(3,4.5,2001);bx=np.c_[np.zeros(len(bgrid)),bgrid,np.zeros(len(bgrid))];bf=q3.predict(bx,ridge,pchip)
    base_curve=pd.DataFrame(np.c_[bx,bf],columns=["a","b","N","R","P","U"])
    anchors=grid.iloc[ids]
    # 查找一个明确支配无针肋最佳折中方案的有针肋点。
    no=local.iloc[-1];dom=ref[np.all(ref[q3.RESP].to_numpy()<=no[q3.RESP].to_numpy()+1e-12,axis=1)]
    dominant=dom.iloc[np.argmin(score_f(dom[q3.RESP].to_numpy(),ideal,nadir))] if len(dom) else None
    g=metrics[metrics.run==0];ns=metrics[metrics.method=="分层 NSGA-II"]
    summary={"ideal":ideal.tolist(),"nadir":nadir.tolist(),"reference_points":len(ref),"final":final.to_dict(),"no_pin":no.to_dict(),"no_pin_dominated":bool(len(dom)),"example_dominator":None if dominant is None else dominant.to_dict(),"grid":g.to_dict("records"),"nsga_mean":ns.select_dtypes("number").mean().to_dict(),"nsga_std":ns.select_dtypes("number").std().to_dict()}
    (LOG/"methodology_final_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
