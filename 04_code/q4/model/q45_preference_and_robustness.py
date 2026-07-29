"""APMCM B题问题4--5：偏好变化与扰动鲁棒性分析。

复用问题3的分段代理模型和固定归一化标尺。结构加工误差（A类证据）
与运行工况的机理情景外推（B类证据）严格分开统计。
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution, minimize
from scipy.stats import qmc

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "06_drafts" / "q4"


class RoutedDirectory:
    """按文件名前缀把Q4/Q5产物送入各自目录。"""

    def __init__(self, q4: Path, q5: Path):
        self.q4, self.q5 = q4, q5

    def __truediv__(self, name: str) -> Path:
        return (self.q5 if str(name).startswith(("q5_", "fig_q5_")) else self.q4) / name

    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        self.q4.mkdir(parents=parents, exist_ok=exist_ok)
        self.q5.mkdir(parents=parents, exist_ok=exist_ok)


DATA = RoutedDirectory(
    ROOT / "03_data" / "processed" / "q4",
    ROOT / "03_data" / "processed" / "q5",
)
FIG = RoutedDirectory(
    ROOT / "05_figures" / "q4",
    ROOT / "05_figures" / "q5",
)
sys.path.insert(0, str(ROOT / "04_code" / "q3" / "model"))
import q3_multiobjective_optimization as q3  # noqa: E402

RHO = 1e-4
IDEAL = np.array([0.720227030892114, 0.076039812756808, 0.771786631558643])
NADIR = np.array([0.760176422366934, 0.158555235146874, 0.819442088245665])
SPAN = NADIR - IDEAL
N_LEVELS = np.array([2., 4., 6., 8., 10.])


def score(f, w=None):
    z = (np.asarray(f) - IDEAL) / SPAN
    lam = np.ones(3) if w is None else 3 * np.asarray(w)
    return np.max(z * lam, axis=-1) + RHO * np.sum(z * lam, axis=-1)


def cvar(x, alpha=.95):
    x = np.sort(np.asarray(x).ravel())
    return float(x[int(np.floor(alpha * len(x))):].mean())


def simplex(H):
    return np.array([(i / H, j / H, (H-i-j) / H) for i in range(H+1) for j in range(H+1-i)])


def best_on_ref(ref_x, ref_f, weights):
    out = []
    for w in weights:
        s = score(ref_f, w); i = int(np.argmin(s))
        out.append([*w, *ref_x[i], *ref_f[i], s[i]])
    return pd.DataFrame(out, columns=["w_R","w_P","w_U","a","b","N","R","P","U","G"])


def refine_weight_selections(df, ridge, pchip):
    """在参考点所属离散 N 层作有界 SLSQP 连续精化。"""
    rows = []
    for r in df.itertuples(index=False):
        w = np.array([r.w_R, r.w_P, r.w_U])
        if r.N == 0:
            rows.append(list(r)); continue
        fun = lambda v: float(score(q3.predict(np.array([[v[0], v[1], r.N]]), ridge, pchip)[0], w))
        ans = minimize(fun, [r.a, r.b], method="SLSQP", bounds=[(.1,.3),(3.,4.5)],
                       options={"ftol": 1e-12, "maxiter": 120})
        x = np.array([[ans.x[0], ans.x[1], r.N]])
        f = q3.predict(x, ridge, pchip)[0]
        rows.append([r.w_R,r.w_P,r.w_U,*x[0],*f,float(fun(ans.x))])
    return pd.DataFrame(rows, columns=df.columns)


def preference_analysis(ref_x, ref_f, ridge, pchip):
    scans = {}
    for H in [25, 50, 100]:
        scans[H] = best_on_ref(ref_x, ref_f, simplex(H))
    # H=50 的完整参考前沿扫描给出权重分区；仅对代表情景做连续精化，
    # 既避免把数值网格误差混入遗憾定义，也保持计算可复现、可审计。
    main = scans[50].copy()
    main.to_csv(DATA / "q4_weight_scan_H50.csv", index=False, encoding="utf-8-sig")
    candidates = pd.DataFrame(np.c_[ref_x, ref_f], columns=["a","b","N","R","P","U"])
    # Pareto 参考集上的最大/平均机会损失，避免再做全域联合优化。
    regrets = []
    for _, c in candidates.iterrows():
        gc = score(c[["R","P","U"]].to_numpy(float), simplex(50))
        gb = main.G.to_numpy()
        regrets.append([gc.max() * 0, np.max(gc-gb), np.mean(gc-gb)])
    rr = np.asarray(regrets)
    # 第二列为最大遗憾，第三列为平均遗憾；先最小最大，再最小平均。
    order = np.lexsort((rr[:,2], rr[:,1])); pref = candidates.iloc[int(order[0])].copy()
    pref["max_regret"], pref["mean_regret"] = rr[order[0],1], rr[order[0],2]
    scenario_w = {"均衡":(1/3,1/3,1/3), "散热优先":(.6,.2,.2), "能耗优先":(.2,.6,.2),
                  "均匀性优先":(.2,.2,.6), "热可靠性优先":(.45,.1,.45)}
    scenarios = []
    for name,w in scenario_w.items():
        j = np.argmin(np.sum((main[["w_R","w_P","w_U"]].to_numpy()-np.array(w))**2,axis=1))
        q = refine_weight_selections(main.iloc[[j]], ridge, pchip).iloc[0].copy(); q["场景"] = name; scenarios.append(q)
    scen = pd.DataFrame(scenarios)
    # 收敛摘要
    conv=[]
    for H,d in scans.items():
        conv.append([H,len(d), *[(d.N==n).mean() for n in N_LEVELS], d.G.mean()])
    pd.DataFrame(conv,columns=["H","权重数","pi_N2","pi_N4","pi_N6","pi_N8","pi_N10","mean_G"]).to_csv(DATA/"q4_convergence.csv",index=False,encoding="utf-8-sig")
    scen.to_csv(DATA/"q4_representative_scenarios.csv",index=False,encoding="utf-8-sig")
    return main, pref, scen, pd.DataFrame(conv,columns=["H","权重数","pi_N2","pi_N4","pi_N6","pi_N8","pi_N10","mean_G"])


def lhs_struct(n, tau=.025, seed=20260719):
    u = qmc.LatinHypercube(2, seed=seed).random(n)
    return qmc.scale(u, [-tau,-tau], [tau,tau])


def structure_samples(x, eps, ridge, pchip):
    xx = np.column_stack([x[0]+.2*eps[:,0], x[1]+1.5*eps[:,1], np.full(len(eps),x[2])])
    return q3.predict(xx,ridge,pchip)


def summary_metrics(vals, labels):
    d={}
    for i,k in enumerate(labels):
        a=vals[:,i]; d.update({f"mean_{k}":a.mean(),f"sd_{k}":a.std(ddof=1),f"q95_{k}":np.quantile(a,.95),f"cvar95_{k}":cvar(a),f"max_{k}":a.max()})
    return d


def optimize_structure(ridge,pchip,eps):
    # 中等公差 tau=0.025 的鲁棒可行域：a∈[.105,.295], b∈[3.0375,4.4625]
    bounds=[(.105,.295),(3.0375,4.4625)]
    rows=[]
    for n in N_LEVELS:
        def fun(v): return cvar(score(structure_samples((v[0],v[1],n),eps,ridge,pchip)))
        de=differential_evolution(fun,bounds,seed=7300+int(n),popsize=9,maxiter=55,tol=2e-6,polish=True)
        f=q3.predict(np.array([[de.x[0],de.x[1],n]]),ridge,pchip)[0]
        rows.append([de.x[0],de.x[1],n,*f,de.fun])
    out=pd.DataFrame(rows,columns=["a","b","N","R","P","U","CVaR95"])
    return out.iloc[int(out.CVaR95.argmin())],out


def operation_values(x, eps, sm, sq, ridge, pchip, pars, u_model):
    base = structure_samples(x,eps,ridge,pchip)
    alpha,theta,mr,mu=pars
    r = base[:,0] * (theta+(1-theta)*sm**(-mr))
    theta_r = sq*r
    p = base[:,1]*(alpha*sm+(1-alpha)*sm**2)
    u = base[:,2]*sm**(-mu)
    if u_model == "B": u *= sq
    return np.c_[theta_r,p,u]


def optimize_operation(ridge,pchip,eps,sm,sq,pars,u_model):
    bounds=[(.105,.295),(3.0375,4.4625)]
    rows=[]
    for n in N_LEVELS:
        def fun(v): return cvar(score(operation_values((v[0],v[1],n),eps,sm,sq,ridge,pchip,pars,u_model)))
        de=differential_evolution(fun,bounds,seed=8100+int(n),popsize=7,maxiter=42,tol=4e-6,polish=True)
        f=q3.predict(np.array([[de.x[0],de.x[1],n]]),ridge,pchip)[0]
        rows.append([de.x[0],de.x[1],n,*f,de.fun])
    z=pd.DataFrame(rows,columns=["a","b","N","R","P","U","CVaR95"])
    return z.iloc[int(z.CVaR95.argmin())]


def robust_analysis(ridge,pchip,nom,pref):
    eps_screen=lhs_struct(1600); eps_final=lhs_struct(12000,seed=20260720)
    structural, layers = optimize_structure(ridge,pchip,eps_screen)
    # 用独立大样本最终复核并输出名义/偏好/鲁棒等方案。
    orig=np.array([.2,4.5,6.])
    schemes={"问题3名义":nom, "问题4偏好鲁棒":pref[["a","b","N"]].to_numpy(float), "问题5结构鲁棒":structural[["a","b","N"]].to_numpy(float), "最佳原始样本":orig}
    rows=[]
    for name,x in schemes.items():
        f0=q3.predict(np.asarray(x)[None,:],ridge,pchip)[0]; vals=structure_samples(x,eps_final,ridge,pchip); cs=score(vals)
        row={"方案":name,"a":x[0],"b":x[1],"N":x[2],"C_nom":float(score(f0)),"CVaR95_C":cvar(cs),"C_max":cs.max()}
        row.update(summary_metrics(vals,["R","P","U"]));
        degrade=(vals.max(0)-f0)/SPAN; row.update({"D_R":degrade[0],"D_P":degrade[1],"D_U":degrade[2],"D_rms":float(np.sqrt(np.mean(degrade**2)))})
        rows.append(row)
    structural_summary=pd.DataFrame(rows)
    structural_summary.to_csv(DATA/"q5_structure_propagation.csv",index=False,encoding="utf-8-sig")
    layers.to_csv(DATA/"q5_structure_layer_optima.csv",index=False,encoding="utf-8-sig")
    # B类工况：中等压力情景，六种模型形式并列。
    u=qmc.LatinHypercube(4,seed=20260721).random(3000)
    ee=qmc.scale(u[:,:2],[-.025,-.025],[.025,.025])
    sm=qmc.scale(u[:,[2]],[.95],[1.05]).ravel(); sq=qmc.scale(u[:,[3]],[.95],[1.05]).ravel()
    packs={"S1":(.8,.75,.25,.25),"S2":(.5,.5,.5,.5),"S3":(.2,.25,.8,.8)}
    phys=[]
    for s,pars in packs.items():
        for um in "AB":
            best=optimize_operation(ridge,pchip,ee,sm,sq,pars,um)
            x=best[["a","b","N"]].to_numpy(float); vals=operation_values(x,ee,sm,sq,ridge,pchip,pars,um)
            f0=operation_values(x,np.zeros((1,2)),np.ones(1),np.ones(1),ridge,pchip,pars,um)[0]
            cs=score(vals); row={"机制":s,"U模型":um,"a":x[0],"b":x[1],"N":x[2],"CVaR95_Cop":cvar(cs),"Cmax":cs.max(),"Cnom":float(score(f0))}
            row.update(summary_metrics(vals,["Theta","P","U"])); phys.append(row)
    physical=pd.DataFrame(phys); physical.to_csv(DATA/"q5_operation_scenarios.csv",index=False,encoding="utf-8-sig")
    return structural_summary, physical, structural


def make_figures(weights, pref, struct, physical):
    plt.rcParams.update({"font.sans-serif":["Microsoft YaHei","SimHei","DejaVu Sans"],"axes.unicode_minus":False,"font.size":9})
    colors={2:"#2563eb",4:"#0891b2",6:"#16a34a",8:"#d97706",10:"#dc2626",0:"#6b7280"}
    fig,axs=plt.subplots(1,2,figsize=(10.4,4.0))
    for n in N_LEVELS:
        d=weights[weights.N==n]; axs[0].scatter(d.w_R,d.w_P,s=10,c=colors[int(n)],label=f"N={int(n)}",alpha=.75)
    axs[0].set(xlabel="$w_R$",ylabel="$w_P$",title="权重单纯形中的最优排数");axs[0].legend(ncol=2,fontsize=8);axs[0].grid(alpha=.2)
    axs[1].scatter(weights.w_R,weights.a,c=weights.b,cmap="viridis",s=11);axs[1].set(xlabel="$w_R$",ylabel="$a^*$",title="最优针肋尺寸随偏好变化（颜色为 $b^*$）");axs[1].grid(alpha=.2)
    fig.tight_layout();fig.savefig(FIG/"fig_q4_01_weight_mapping.pdf",bbox_inches="tight");plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.6,4.2)); x=np.arange(len(struct))
    ax.bar(x-.18,struct.C_nom,width=.36,label="名义评分 $C_{AT}$",color="#60a5fa");ax.bar(x+.18,struct.CVaR95_C,width=.36,label="加工误差 CVaR$_{0.95}$",color="#dc2626")
    ax.set_xticks(x,struct["方案"],rotation=15,ha="right");ax.set_ylabel("固定尺度评分");ax.set_title("结构加工误差下的风险比较");ax.legend();ax.grid(axis="y",alpha=.22);fig.tight_layout();fig.savefig(FIG/"fig_q5_01_structure_risk.pdf",bbox_inches="tight");plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.7,4.1));
    for um,mark in [("A","o"),("B","s")]:
        d=physical[physical["U模型"]==um];ax.plot(d["机制"],d.CVaR95_Cop,marker=mark,label=f"U模型{um}")
    ax.set(ylabel="CVaR$_{0.95}(C_{op})$",title="工况机理情景下的鲁棒风险");ax.grid(alpha=.22);ax.legend();fig.tight_layout();fig.savefig(FIG/"fig_q5_02_operation_envelope.pdf",bbox_inches="tight");plt.close(fig)


def latex_table(df, cols, fmts):
    lines=[]
    for _,r in df.iterrows(): lines.append(" & ".join(fmts[i].format(r[c]) for i,c in enumerate(cols))+r" \\")
    return "\n".join(lines)


def write_tex(pref, scen, conv, struct, physical, nom):
    p = pref; st=struct[struct["方案"]=="问题5结构鲁棒"].iloc[0]
    scen_show=scen[["场景","a","b","N","R","P","U","G"]]
    tex=rf'''\documentclass[UTF8,a4paper,11pt]{{ctexart}}
\usepackage{{geometry,booktabs,float,graphicx,amsmath,siunitx}}
\geometry{{margin=2.15cm}}\setlength{{\parskip}}{{0.28em}}
\title{{APMCM B题问题4--5：偏好变化与扰动鲁棒性分析}}\author{{}}\date{{}}
\begin{{document}}\maketitle
\section{{模型衔接与不确定性分层}}
沿用问题2的三次Ridge--PCHIP分段代理模型，以及问题3固定理想点$F^I=({IDEAL[0]:.6f},{IDEAL[1]:.6f},{IDEAL[2]:.6f})$和近似Nadir点$F^N=({NADIR[0]:.6f},{NADIR[1]:.6f},{NADIR[2]:.6f})$。名义等权方案为$(a,b,N)=({nom[0]:.6f},{nom[1]:.6f},{int(nom[2])})$。问题4仅改变目标关注权重；问题5则把结构加工误差（由代理模型直接支持）与变工况机理情景（缺少变工况训练数据）严格分层。
\section{{问题4：偏好变化与偏好鲁棒设计}}
令$z_k=(F_k-F_k^I)/(F_k^N-F_k^I)$，权重$w_R+w_P+w_U=1$，并取$\lambda_k=3w_k$。带权增强切比雪夫评分为
\[G(x;w)=\max_k\{{\lambda_kz_k(x)\}}+10^{{-4}}\sum_k\lambda_kz_k(x).\]
在$H=25,50,100$的权重单纯形网格上扫描；$H=50$含1326组权重，以问题3合并参考前沿计算机会损失，五个代表场景再在所属离散排数层作连续精化。偏好遗憾定义为$r_{{pref}}(x,w)=G(x;w)-G^*(w)$；最小最大遗憾的偏好鲁棒设计为
\[x_{{pref}}^{{rob}}=({p.a:.6f},{p.b:.6f},{int(p.N)}),\quad \max r_{{pref}}={p.max_regret:.6f}.\]
\begin{{table}}[H]\centering\small\caption{{代表性偏好情景的专属最优方案}}\begin{{tabular}}{{lrrrrrrr}}\toprule 情景&a&b&N&R&P&U&G\\\midrule
{latex_table(scen_show,["场景","a","b","N","R","P","U","G"],["{}","{:.4f}","{:.4f}","{:.0f}","{:.6f}","{:.6f}","{:.6f}","{:.5f}"])}\\\bottomrule\end{{tabular}}\end{{table}}
\begin{{figure}}[H]\centering\includegraphics[width=.92\linewidth]{{../../05_figures/q4/fig_q4_01_weight_mapping.pdf}}\caption{{权重变化到最优设计的映射}}\end{{figure}}
\section{{问题5：加工误差与工况波动}}
中等公差情景取$\varepsilon_a,\varepsilon_b\in[-0.025,0.025]$，从而在鲁棒可行域$a\in[0.105,0.295]$、$b\in[3.0375,4.4625]$内重新搜索。对$10^4$量级LHS实现样本，结构加工鲁棒目标为$\min_x\mathrm{{CVaR}}_{{0.95}}[C_{{str}}]$。得到A类正式结果
\[x_{{str}}^{{rob}}=({st.a:.6f},{st.b:.6f},{int(st.N)}),\quad \mathrm{{CVaR}}_{{0.95}}={st.CVaR95_C:.6f}.\]
\begin{{figure}}[H]\centering\includegraphics[width=.88\linewidth]{{../../05_figures/q5/fig_q5_01_structure_risk.pdf}}\caption{{结构加工误差传播：名义代价与上尾风险}}\end{{figure}}
对于流量、热负荷扰动，使用$\Theta_R=s_qR^{{op}}$、$P^{{op}}$、$U^{{op}}$组成评分。S1--S3只表示黏性/惯性和流量敏感度的模型形式包络；U模型A/B反映温度非均匀性是否随热负荷幅值缩放，均不被解释为附件标定参数。\begin{{figure}}[H]\centering\includegraphics[width=.78\linewidth]{{../../05_figures/q5/fig_q5_02_operation_envelope.pdf}}\caption{{工况机理情景下的风险包络（B类辅助复核）}}\end{{figure}}
\section{{工程建议与边界}}
偏好不确定时推荐$x_{{pref}}^{{rob}}$；制造公差为主导时优先采用$x_{{str}}^{{rob}}$。变工况方案仅作为机制情景的稳健性复核，不能赋予其问题2域内代理模型同等的预测精度。入口温度扰动只按绝对温度基线平移处理，不进入综合评分。无针肋支路仍保留在偏好比较中，但不参与有针肋加工公差的直接传播。\end{{document}}'''
    (OUT/"q4-q5_demo.tex").write_text(tex,encoding="utf-8")


def write_odt(summary):
    """写出最小且标准的 ODT（ODF 1.2 Zip package），用于用户要求的ODF格式。"""
    title="APMCM B题问题4--5：偏好及扰动鲁棒性分析"
    paras=[title,
           "1 模型衔接与证据分层",
           "沿用问题2的三次 Ridge--PCHIP 分段代理模型、问题3的固定理想点与近似 Nadir 点。问题4仅改变热阻、压降、温度非均匀性的关注权重；问题5严格分为结构加工误差的直接代理传播（A类）和运行工况的机理情景外推（B类）。",
           "2 偏好变化与偏好鲁棒设计",
           "权重在 H=25、50、100 的单纯形网格上扫描；H=50 含1326组权重。采用带权增强切比雪夫评分 G=max(3w_k z_k)+10^-4 sum(3w_k z_k)，并以最小最大机会损失选择偏好鲁棒方案。",
           f"偏好鲁棒方案：a={summary['pref']['a']:.6f}, b={summary['pref']['b']:.6f}, N={int(summary['pref']['N'])}；最大偏好遗憾为 {summary['pref']['max_regret']:.6f}。",
           "3 加工误差鲁棒设计（A类主结果）",
           "中等公差压力情景取 εa、εb 均在[-0.025,0.025]，并将名义可行域收缩到 a∈[0.105,0.295]、b∈[3.0375,4.4625]。以LHS样本传播加工误差，主目标为最小化综合评分的CVaR_0.95。",
           f"结构加工鲁棒方案：a={summary['struct']['a']:.6f}, b={summary['struct']['b']:.6f}, N={int(summary['struct']['N'])}。",
           "4 运行工况情景复核（B类）",
           "流量与热负荷取中等压力范围 s_m,s_q∈[0.95,1.05]。压降、热阻和温度非均匀性按照S1--S3的机理包络修正，并对温度非均匀性采用A/B两种尺度解释。该结果是机制情景复核，不是变工况训练数据支持的代理模型精度结论。",
           "5 工程建议",
           "偏好不确定时采用偏好鲁棒方案；加工公差主导时优先采用结构加工鲁棒方案。入口温度只作为绝对温度基线平移，不进入综合评分。完整公式、表格、图形和可复现Python程序见同目录的TeX、PDF、data与figures文件。"]
    content='''<?xml version="1.0" encoding="UTF-8"?><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.2"><office:body><office:text>'''+''.join(f'<text:p>{escape(x)}</text:p>' for x in paras)+'''</office:text></office:body></office:document-content>'''
    styles='''<?xml version="1.0" encoding="UTF-8"?><office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"><office:styles/></office:document-styles>'''
    manifest='''<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/></manifest:manifest>'''
    path=OUT/"q4-q5_demo.odt"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("mimetype","application/vnd.oasis.opendocument.text",compress_type=zipfile.ZIP_STORED)
        z.writestr("content.xml",content);z.writestr("styles.xml",styles);z.writestr("META-INF/manifest.xml",manifest)


def main():
    for d in (DATA,FIG): d.mkdir(parents=True,exist_ok=True)
    pin,base=q3.read_data(); ridge,pchip=q3.build_surrogate(pin,base)
    ref=pd.read_csv(ROOT/"03_data"/"processed"/"q3"/"q3_pareto_reference_merged.csv")
    ref_x=ref[["a","b","N"]].to_numpy(float);ref_f=ref[["R","P","U"]].to_numpy(float)
    weights,pref,scen,conv=preference_analysis(ref_x,ref_f,ridge,pchip)
    nom=np.array([.2249317396262705,4.5,6.])
    struct,physical,struct_x=robust_analysis(ridge,pchip,nom,pref)
    write_tex(pref,scen,conv,struct,physical,nom)
    summary={"pref":pref.to_dict(),"struct":{"a":float(struct_x.a),"b":float(struct_x.b),"N":float(struct_x.N)},"physical":physical.to_dict("records")}
    (DATA/"q45_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    write_odt(summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
