"""问题3候选算法比较：三级分层网格与按 N 分层的 NSGA-II。"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import q3_multiobjective_optimization as q3

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "03_data" / "processed" / "q3"
FIG = ROOT / "05_figures" / "q3"
LOG = ROOT / "00_progress" / ".working" / "logs" / "q3"


def rank_and_crowding(f):
    """NSGA-II 快速排序与拥挤距离；矩阵方向 dom[i,j]=i 支配 j。"""
    dom = np.all(f[:, None, :] <= f[None, :, :] + 1e-12, axis=2) & np.any(
        f[:, None, :] < f[None, :, :] - 1e-12, axis=2)
    left = np.ones(len(f), bool); rank = np.full(len(f), len(f), int); fronts = []
    r = 0
    while left.any():
        ids = np.where(left)[0]
        front = ids[~np.any(dom[np.ix_(ids, ids)], axis=0)]
        if not len(front): front = ids[:1]
        rank[front] = r; left[front] = False; fronts.append(front); r += 1
    crowd = np.zeros(len(f))
    for front in fronts:
        if len(front) <= 2: crowd[front] = np.inf; continue
        vals = f[front]
        for j in range(f.shape[1]):
            o = np.argsort(vals[:, j]); crowd[front[o[[0, -1]]]] = np.inf
            span = vals[o[-1], j] - vals[o[0], j]
            if span > 0:
                crowd[front[o[1:-1]]] += (vals[o[2:], j] - vals[o[:-2], j]) / span
    return rank, crowd, fronts


def environmental_select(x, f, pop_size):
    rank, crowd, fronts = rank_and_crowding(f); chosen = []
    for front in fronts:
        if len(chosen) + len(front) <= pop_size: chosen.extend(front.tolist())
        else:
            need = pop_size - len(chosen)
            chosen.extend(front[np.argsort(-crowd[front])[:need]].tolist()); break
    ids = np.asarray(chosen, int)
    rank2, crowd2, _ = rank_and_crowding(f[ids])
    return x[ids], f[ids], rank2, crowd2


def tournament(rng, rank, crowd, n):
    a = rng.integers(0, len(rank), n); b = rng.integers(0, len(rank), n)
    better = (rank[a] < rank[b]) | ((rank[a] == rank[b]) & (crowd[a] > crowd[b]))
    return np.where(better, a, b)


def vary(rng, parents, lo=np.array([.1, 3.]), hi=np.array([.3, 4.5])):
    """SBX 交叉与多项式变异。"""
    n = len(parents); out = np.empty_like(parents); eta_c, eta_m = 15., 20.
    for k in range(0, n, 2):
        p1, p2 = parents[k], parents[(k + 1) % n]
        if rng.random() < .9:
            u = rng.random(2); beta = np.where(u <= .5, (2*u)**(1/(eta_c+1)), (1/(2*(1-u)))**(1/(eta_c+1)))
            out[k] = .5*((1+beta)*p1+(1-beta)*p2)
            if k+1<n: out[k+1] = .5*((1-beta)*p1+(1+beta)*p2)
        else:
            out[k] = p1
            if k+1<n: out[k+1] = p2
    for i in range(n):
        for j in range(2):
            if rng.random() < .5:
                u = rng.random(); delta = (2*u)**(1/(eta_m+1))-1 if u < .5 else 1-(2*(1-u))**(1/(eta_m+1))
                out[i,j] += delta*(hi[j]-lo[j])
    return np.clip(out, lo, hi)


def nsga_slice(rng, n_level, ridge, pchip, pop_size=60, generations=50):
    x2 = rng.uniform([.1, 3.], [.3, 4.5], size=(pop_size, 2))
    x = np.c_[x2, np.full(pop_size, n_level)]; f = q3.predict(x, ridge, pchip)
    rank, crowd, _ = rank_and_crowding(f); trace = []
    for g in range(generations):
        ids = tournament(rng, rank, crowd, pop_size)
        c2 = vary(rng, x[ids, :2]); cx = np.c_[c2, np.full(pop_size, n_level)]
        cf = q3.predict(cx, ridge, pchip)
        x, f, rank, crowd = environmental_select(np.vstack([x, cx]), np.vstack([f, cf]), pop_size)
        if g % 10 == 0 or g == generations-1: trace.append((g+1, float(np.min(f[:,0])), float(np.min(f[:,1])), float(np.min(f[:,2]))))
    take = q3.nondominated(f)
    return x[take], f[take], trace


def mc_hv(z, samples):
    z = z[np.all(z < 1.10, axis=1)]
    # 分块判断随机点是否被任一近似前沿点支配。
    hit = np.zeros(len(samples), bool)
    for i in range(0, len(z), 500):
        hit |= np.any(np.all(z[i:i+500, None, :] <= samples[None, :, :], axis=2), axis=0)
    return float(hit.mean() * 1.1**3)


def igd_plus(ref, approx):
    vals=[]
    for i in range(0, len(ref), 150):
        d=np.sqrt(np.sum(np.maximum(approx[None,:,:]-ref[i:i+150,None,:],0)**2,axis=2))
        vals.extend(np.min(d,axis=1))
    return float(np.mean(vals))


def spacing(z):
    if len(z)<2: return 0.0
    d=[]
    for i in range(0,len(z),200):
        dd=np.sqrt(np.sum((z[i:i+200,None,:]-z[None,:,:])**2,axis=2))
        dd[dd<1e-14]=np.inf; d.extend(np.min(dd,axis=1))
    return float(np.std(d,ddof=1))


def main():
    for d in [DATA, FIG, LOG]: d.mkdir(parents=True, exist_ok=True)
    pin, base=q3.read_data(); ridge,pchip=q3.build_surrogate(pin,base)
    ref_df=pd.read_csv(DATA/"q3_pareto_global.csv"); ref_x=ref_df[["a","b","N"]].to_numpy(); ref_f=ref_df[q3.RESP].to_numpy()
    _,ideal,nadir=q3.anchors(ref_x,ref_f); nadir=np.maximum(nadir,ref_f.max(0)); ref_z=q3.normalize(ref_f,ideal,nadir)
    pick=np.linspace(0,len(ref_z)-1,min(1200,len(ref_z))).astype(int); ref_eval=ref_z[pick]
    rng_mc=np.random.default_rng(314159); samples=rng_mc.uniform(0,1.1,size=(45000,3))
    rows=[]; grid_sets={}
    for ng in [101,201,401]:
        t=time.perf_counter(); x,f,meta=q3.grid_search(ridge,pchip,ng); sec=time.perf_counter()-t
        z=q3.normalize(f,ideal,nadir); grid_sets[ng]=(x,f,z)
        rows.append({"method":f"分层网格 {ng}x{ng}","run":0,"points":len(f),"HV":mc_hv(z,samples),"IGD_plus":igd_plus(ref_eval,z),"Spacing":spacing(z),"seconds":sec,"evaluations":5*ng*ng+2001})
    all_runs=[]; traces=[]
    for seed in range(202601,202621):
        rng=np.random.default_rng(seed); xs=[]; fs=[]; t=time.perf_counter()
        for n in q3.N_LEVELS:
            x,f,tr=nsga_slice(rng,n,ridge,pchip); xs.append(x); fs.append(f)
            traces.extend([[seed,int(n),*v] for v in tr])
        x=np.vstack(xs); f=np.vstack(fs); take=q3.nondominated(f); x,f=x[take],f[take]
        z=q3.normalize(f,ideal,nadir); sec=time.perf_counter()-t; all_runs.append((x,f,z))
        rows.append({"method":"分层 NSGA-II","run":seed,"points":len(f),"HV":mc_hv(z,samples),"IGD_plus":igd_plus(ref_eval,z),"Spacing":spacing(z),"seconds":sec,"evaluations":5*60*(50+1)})
    metrics=pd.DataFrame(rows); metrics.to_csv(DATA/"q3_algorithm_metrics.csv",index=False,encoding="utf-8-sig")
    pd.DataFrame(traces,columns=["seed","N","generation","min_R","min_P","min_U"]).to_csv(DATA/"q3_nsga2_trace.csv",index=False)
    nx=np.vstack([v[0] for v in all_runs]); nf=np.vstack([v[1] for v in all_runs]); take=q3.nondominated(nf)
    pd.DataFrame(np.c_[nx[take],nf[take]],columns=["a","b","N","R","P","U"]).to_csv(DATA/"q3_pareto_nsga2.csv",index=False)
    ns=metrics[metrics.method=="分层 NSGA-II"]
    summary={"settings":{"population":60,"generations":50,"seeds":20,"strata":5},"grid":metrics[metrics.run==0].to_dict("records"),"nsga2_mean":ns.select_dtypes("number").mean().to_dict(),"nsga2_std":ns.select_dtypes("number").std().to_dict()}
    (LOG/"algorithm_comparison_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
