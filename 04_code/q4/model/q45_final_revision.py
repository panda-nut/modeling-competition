"""问题4--5定稿补充：评分闭环、遗憾比较、灵敏度及工况设计判定。"""
from __future__ import annotations

import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import qmc

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE)); import q45_preference_and_robustness as q
sys.path.insert(0,str(ROOT/'04_code'/'q3'/'model')); import q3_multiobjective_optimization as q3

OUT,DATA=ROOT/'06_drafts'/'q4',q.DATA

def exact_scenario(w, ref_x, ref_f, ridge, pchip):
    i=int(np.argmin(q.score(ref_f,w)))
    d=pd.DataFrame([[*w,*ref_x[i],*ref_f[i],q.score(ref_f[i],w)]],columns=['w_R','w_P','w_U','a','b','N','R','P','U','G'])
    return q.refine_weight_selections(d,ridge,pchip).iloc[0]

def regret_matrix(cand_f, weights, best_g):
    """候选×权重遗憾，按批处理以控制内存。"""
    ans=[]
    for f in np.array_split(cand_f, max(1,len(cand_f)//300)):
        z=(f-q.IDEAL)/q.SPAN
        g=np.max(z[:,None,:]*(3*weights)[None,:,:],axis=2)+q.RHO*np.sum(z[:,None,:]*(3*weights)[None,:,:],axis=2)
        r=g-best_g[None,:]
        ans.append(np.c_[r.max(1),r.mean(1),np.quantile(r,.95,axis=1)])
    return np.vstack(ans)

def local_sensitivity(x,ridge,pchip):
    # 对归一化变量 a_tilde,b_tilde 的中心差分绝对导数。
    h=1e-4; out=[]
    for j,scale in enumerate([.2,1.5]):
        xp=x.copy();xm=x.copy();xp[j]+=h*scale;xm[j]-=h*scale
        out.append(np.abs((q3.predict(xp[None,:],ridge,pchip)[0]-q3.predict(xm[None,:],ridge,pchip)[0])/(2*h*q.SPAN)))
    return np.array(out).T

def src(x,y):
    xx=(x-x.mean(0))/x.std(0,ddof=1); yy=(y-y.mean(0))/y.std(0,ddof=1)
    return np.linalg.lstsq(np.c_[np.ones(len(xx)),xx],yy,rcond=None)[0][1:]

def fmt(df,cols,fmts):
    return '\n'.join(' & '.join(f.format(r[c]) for c,f in zip(cols,fmts))+r' \\' for _,r in df.iterrows())

def main():
    pin,base=q3.read_data();ridge,pchip=q3.build_surrogate(pin,base)
    ref=pd.read_csv(ROOT/'03_data'/'processed'/'q3'/'q3_pareto_reference_merged.csv'); rx=ref[['a','b','N']].to_numpy(float); rf=ref[['R','P','U']].to_numpy(float)
    # 问题4：每个H上的最小最大遗憾，代表场景使用精确而非最近网格权重。
    conv=[]; hdata={}
    for H in (25,50,100):
        w=q.simplex(H); d=q.best_on_ref(rx,rf,w); rr=regret_matrix(rf,w,d.G.to_numpy()); ix=np.lexsort((rr[:,1],rr[:,0]))[0]
        hdata[H]=(w,d,rr,ix); conv.append([H,len(w),rx[ix,0],rx[ix,1],int(rx[ix,2]),*rr[ix]])
    w,d,rr,ix=hdata[50]; pref=ref.iloc[int(ix)].copy(); pref['max_regret'],pref['mean_regret'],pref['q95_regret']=rr[ix]
    named_w={'均衡':(1/3,1/3,1/3),'散热优先':(.6,.2,.2),'能耗优先':(.2,.6,.2),'均匀性优先':(.2,.2,.6),'热可靠性优先':(.45,.1,.45)}
    scen=pd.DataFrame([exact_scenario(np.array(v),rx,rf,ridge,pchip).to_dict()|{'场景':k} for k,v in named_w.items()])
    # 显式核验均衡评分与问题3闭环。
    nominal=np.array([.2249317396262705,4.5,6.]); orig=np.array([.2,4.5,6.]); f_nom=q3.predict(nominal[None,:],ridge,pchip)[0]
    assert abs(q.score(f_nom,(1/3,1/3,1/3))-0.38638274667145095)<1e-8
    # 偏好比较：名义/偏好/原始/两个代表方案/无针肋。
    no=np.array([0.,4.000005465,0.]); compare={'问题3名义':nominal,'问题4偏好鲁棒':pref[['a','b','N']].to_numpy(float),'最佳原始样本':orig,
             '散热优先方案':scen[scen.场景=='散热优先'][['a','b','N']].iloc[0].to_numpy(float),'能耗优先方案':scen[scen.场景=='能耗优先'][['a','b','N']].iloc[0].to_numpy(float),'无针肋最佳':no}
    rows=[]
    for name,x in compare.items():
        f=q3.predict(x[None,:],ridge,pchip)[0]; r=regret_matrix(f[None,:],w,d.G.to_numpy())[0];rows.append([name,*x,*f,*r])
    regret=pd.DataFrame(rows,columns=['方案','a','b','N','R','P','U','最大遗憾','平均遗憾','P95遗憾'])
    pis=pd.DataFrame({'N':q.N_LEVELS.astype(int),'权重区域占比':[(d.N==n).mean() for n in q.N_LEVELS]})
    convdf=pd.DataFrame(conv,columns=['H','权重数','a','b','N','最大遗憾','平均遗憾','P95遗憾'])
    for name,df in {'q4_representative_scenarios_corrected.csv':scen,'q4_regret_comparison.csv':regret,'q4_convergence_corrected.csv':convdf,'q4_weight_share.csv':pis}.items(): df.to_csv(DATA/name,index=False,encoding='utf-8-sig')
    # 问题5 A类：2万个独立均匀LHS样本，外加4万个样本收敛复核。
    eps20=q.lhs_struct(20000,seed=20260720); eps40=q.lhs_struct(40000,seed=20260722)
    # 用主统计样本直接求解，避免小样本筛选使CVaR排名反转。
    structural,_=q.optimize_structure(ridge,pchip,eps20); sx=structural[['a','b','N']].to_numpy(float)
    # b=4.5 的名义点无法承受正向b公差；其双侧传播只能作越域诊断。
    safe_nom=np.array([nominal[0],4.4625,6.])
    schemes={'问题3名义（越域诊断）':nominal,'名义可行投影':safe_nom,'问题4偏好鲁棒（越域诊断）':pref[['a','b','N']].to_numpy(float),'问题5结构鲁棒':sx,'最佳原始样本（越域诊断）':orig}
    risk=[]
    for name,x in schemes.items():
        f0=q3.predict(x[None,:],ridge,pchip)[0]; vv=q.structure_samples(x,eps20,ridge,pchip); cc=q.score(vv)
        cc40=q.score(q.structure_samples(x,eps40,ridge,pchip))
        risk.append([name,*x,q.score(f0),cc.mean(),cc.std(ddof=1),np.quantile(cc,.95),q.cvar(cc),q.cvar(cc40),q.cvar(cc40)-q.cvar(cc)])
    risk=pd.DataFrame(risk,columns=['方案','a','b','N','C_nom','均值','标准差','Q95','CVaR95_L20000','CVaR95_L40000','收敛差'])
    nomc=float(risk.iloc[1]['C_nom']);nomr=float(risk.iloc[1]['CVaR95_L20000']);strr=float(risk.iloc[3]['CVaR95_L20000'])
    # 局部灵敏度（名义和结构鲁棒）及全局标准化回归系数（加工误差）。
    loc=[]
    for name,x in [('问题3名义',nominal),('结构鲁棒',sx)]:
        ss=local_sensitivity(x.copy(),ridge,pchip)
        for metric,row in zip(['R','P','U'],ss):loc.append([name,metric,*row])
    local=pd.DataFrame(loc,columns=['设计','响应','|dz/dã|','|dz/db̃|'])
    vals=q.structure_samples(sx,eps20,ridge,pchip); scr=q.score(vals)
    beta_struct=src(eps20,np.c_[vals,scr]); sens_struct=pd.DataFrame(beta_struct,index=['ε_a','ε_b'],columns=['R','P','U','C_str']).reset_index(names='扰动因素')
    risk.to_csv(DATA/'q5_structure_risk_comparison.csv',index=False,encoding='utf-8-sig');local.to_csv(DATA/'q5_local_sensitivity.csv',index=False,encoding='utf-8-sig');sens_struct.to_csv(DATA/'q5_structure_src.csv',index=False,encoding='utf-8-sig')
    # B类：S1--S3与A/B下的设计及“结构鲁棒设计”对照；S2-A上的四因素统计敏感性。
    u=qmc.LatinHypercube(4,seed=20260721).random(12000); ee=qmc.scale(u[:,:2],[-.025,-.025],[.025,.025]);sm=qmc.scale(u[:,[2]],[.95],[1.05]).ravel();sq=qmc.scale(u[:,[3]],[.95],[1.05]).ravel()
    packs={'S1':(.8,.75,.25,.25),'S2':(.5,.5,.5,.5),'S3':(.2,.25,.8,.8)}
    old=pd.read_csv(DATA/'q5_operation_scenarios.csv'); ops=[]
    for _,r in old.iterrows():
        pars=packs[r.机制]; um=r['U模型'];x=r[['a','b','N']].to_numpy(float)
        bestc=q.cvar(q.score(q.operation_values(x,ee,sm,sq,ridge,pchip,pars,um)))
        strc=q.cvar(q.score(q.operation_values(sx,ee,sm,sq,ridge,pchip,pars,um)))
        ops.append([r.机制,um,*pars,.95,1.05,.95,1.05,*x,bestc,strc,strc-bestc])
    ops=pd.DataFrame(ops,columns=['情景','U模型','alpha_P','theta_R','m_R','m_U','sm_lo','sm_hi','sq_lo','sq_hi','a','b','N','最优CVaR','结构鲁棒CVaR','差额'])
    valop=q.operation_values(sx,ee,sm,sq,ridge,pchip,packs['S2'],'A');cop=q.score(valop); beta_op=src(np.c_[ee,sm,sq],np.c_[valop,cop]); sens_op=pd.DataFrame(beta_op,index=['ε_a','ε_b','s_m','s_q'],columns=['Theta_R','P','U','C_op']).reset_index(names='扰动因素')
    ops.to_csv(DATA/'q5_operation_design_comparison.csv',index=False,encoding='utf-8-sig');sens_op.to_csv(DATA/'q5_operation_src_S2A.csv',index=False,encoding='utf-8-sig')
    sens=pd.concat([sens_struct.assign(类别='加工误差')[['扰动因素','类别','R','P','U','C_str']].rename(columns={'C_str':'综合评分'}),sens_op.assign(类别='工况S2-A')[['扰动因素','类别','Theta_R','P','U','C_op']].rename(columns={'Theta_R':'R','C_op':'综合评分'})],ignore_index=True)
    # 扩充Tex。
    tex=rf'''\documentclass[UTF8,a4paper,10.5pt]{{ctexart}}
\usepackage{{geometry,booktabs,float,graphicx,amsmath,array}}\geometry{{margin=1.9cm}}\setlength{{\parskip}}{{.2em}}
\title{{APMCM B题问题4--5：偏好与扰动鲁棒性（修订定稿）}}\author{{}}\date{{}}\begin{{document}}\maketitle
\section{{问题4：评分闭环、权重变化与偏好鲁棒性}} 固定$F^I=({q.IDEAL[0]:.6f},{q.IDEAL[1]:.6f},{q.IDEAL[2]:.6f})$、$F^N=({q.NADIR[0]:.6f},{q.NADIR[1]:.6f},{q.NADIR[2]:.6f})$，令$\lambda_k=3w_k$，故$w=(1/3,1/3,1/3)$严格退化为问题3的$C_{{AT}}$。精确均衡权重下的连续最优方案为$(.224932,4.500000,6)$，$G={q.score(f_nom,(1/3,1/3,1/3)):.6f}$，已与问题3闭合。各行$G$对应不同权重，仅可作场景内部比较。
\begin{{table}}[H]\centering\scriptsize\caption{{精确代表权重下的专属最优方案}}\begin{{tabular}}{{lrrrrrrr}}\toprule 场景&a&b&N&R&P&U&G\\\midrule
{fmt(scen,['场景','a','b','N','R','P','U','G'],['{}','{:.4f}','{:.4f}','{:.0f}','{:.6f}','{:.6f}','{:.6f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
\begin{{table}}[H]\centering\scriptsize\caption{{偏好遗憾比较（H=50）}}\begin{{tabular}}{{lrrr}}\toprule 方案&最大遗憾&平均遗憾&P95遗憾\\\midrule
{fmt(regret,['方案','最大遗憾','平均遗憾','P95遗憾'],['{}','{:.5f}','{:.5f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
\begin{{table}}[H]\centering\scriptsize\caption{{权重网格收敛与鲁棒方案}}\begin{{tabular}}{{rrrrrr}}\toprule H&权重数&a&b&N&最大遗憾\\\midrule
{fmt(convdf,['H','权重数','a','b','N','最大遗憾'],['{:.0f}','{:.0f}','{:.4f}','{:.4f}','{:.0f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
H=50下$N=2,4,6,8,10$的权重区域占比分别为{', '.join(f'{v:.1%}' for v in pis['权重区域占比'])}；$a^*$范围为[{d.a.min():.4f},{d.a.max():.4f}]，$b^*$范围为[{d.b.min():.4f},{d.b.max():.4f}]。无针肋从未成为最优，说明其压降优势不足以抵消热阻和非均匀性损失。\begin{{figure}}[H]\centering\includegraphics[width=.88\linewidth]{{../../05_figures/q4/fig_q4_01_weight_mapping.pdf}}\caption{{权重到最优设计的映射；右图颜色表示$b^*$}}\end{{figure}}
\section{{问题5A：加工误差传播、稳定性与灵敏度}} 实际尺寸为$a^r=a+.20\varepsilon_a,b^r=b+1.50\varepsilon_b$；本节取独立均匀$\varepsilon_a,\varepsilon_b\sim U[-.025,.025]$，种子20260720，$L=20000$个LHS样本，并以$L=40000$复核。$C_{{str}}=\max_kz_k(\widehat F(x^r))+10^{{-4}}\sum_kz_k(\widehat F(x^r))$，$\mathrm{{CVaR}}_{{.95}}(C)=E[C\mid C\ge\mathrm{{VaR}}_{{.95}}(C)]$。鲁棒可行域为$a\in[.105,.295],b\in[3.0375,4.4625]$。
\begin{{table}}[H]\centering\scriptsize\caption{{加工误差下的定量风险比较}}\begin{{tabular}}{{lrrrrr}}\toprule 方案&$C_{{nom}}$&均值&标准差&Q95&CVaR95\\\midrule
{fmt(risk,['方案','C_nom','均值','标准差','Q95','CVaR95_L20000'],['{}','{:.5f}','{:.5f}','{:.5f}','{:.5f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
结构鲁棒方案为$({sx[0]:.6f},{sx[1]:.6f},{int(sx[2])})$；相对\emph{{名义可行投影}}的名义代价为{(risk.iloc[3].C_nom/nomc-1):.2%}，CVaR降幅为{(nomr-strr)/nomr:.2%}；样本量加倍后CVaR变化为{risk.iloc[3]['收敛差']:.2e}。问题3名义点位于$b=4.5$边界，不能接受对称正向公差，表中仅将其作为越域诊断，不将其CVaR与鲁棒可行设计作正式比较。\begin{{figure}}[H]\centering\includegraphics[width=.86\linewidth]{{../../05_figures/q5/fig_q5_03_sensitivity.pdf}}\caption{{结构鲁棒方案的统计敏感性：加工误差与S2-A工况情景分别计算}}\end{{figure}}
局部导数和标准化回归系数见数据表；按绝对标准化回归系数，结构误差中对综合评分最敏感的因素为\textbf{{{sens_struct.loc[np.abs(sens_struct['C_str']).idxmax(),'扰动因素']}}}，S2-A工况中为\textbf{{{sens_op.loc[np.abs(sens_op['C_op']).idxmax(),'扰动因素']}}}。
\section{{问题5B：工况情景设计与边界}} 对$\omega=(\varepsilon_a,\varepsilon_b,s_m,s_q)$取独立LHS，$s_m,s_q\in[.95,1.05]$。采用$P^{{op}}=\widehat P[\alpha_Ps_m+(1-\alpha_P)s_m^2]$，$R^{{op}}=\widehat R[\theta_R+(1-\theta_R)s_m^{{-m_R}}]$，$\Theta_R=s_qR^{{op}}$，以及$U_A=\widehat U s_m^{{-m_U}},U_B=\widehat U s_qs_m^{{-m_U}}$。\begin{{table}}[H]\centering\scriptsize\caption{{六个机理情景下的最优设计及结构鲁棒方案对照}}\begin{{tabular}}{{llrrrrr}}\toprule 情景&U&a&b&N&最优CVaR&结构鲁棒CVaR\\\midrule
{fmt(ops,['情景','U模型','a','b','N','最优CVaR','结构鲁棒CVaR'],['{}','{}','{:.4f}','{:.4f}','{:.0f}','{:.5f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
S1=(.80,.75,.25,.25)$，S2=(.50,.50,.50,.50)$，S3=(.20,.25,.80,.80)$，元组顺序为$(\alpha_P,\theta_R,m_R,m_U)$。六个情景的最优设计在$N=4$与$N=10$间分裂，故缺少变工况数据时不能给出唯一的物理鲁棒设计；应按U的尺度解释分别选择表中方案。工况结论仅为B类机理包络，不与A类结构鲁棒结果混同。\end{{document}}'''
    # 数值百分号、希腊变量和输出目录下的图路径作LaTeX安全处理。
    tex=tex.replace('%', r'\%')
    tex=tex.replace(r'\textbf{ε_a}', r'\textbf{$\varepsilon_a$}').replace(r'\textbf{ε_b}', r'\textbf{$\varepsilon_b$}')
    tex=tex.replace(r'\textbf{s_m}', r'\textbf{$s_m$}').replace(r'\textbf{s_q}', r'\textbf{$s_q$}')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'q4-q5_demo.tex').write_text(tex,encoding='utf-8')
    summary={'pref':pref.to_dict(),'struct':{'a':float(sx[0]),'b':float(sx[1]),'N':float(sx[2])},'risk_improvement':float((nomr-strr)/nomr)}
    (DATA/'q45_revision_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');q.write_odt(summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
