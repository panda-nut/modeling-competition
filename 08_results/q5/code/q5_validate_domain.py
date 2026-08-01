"""问题4--5证据边界检查：不以越域 Ridge 外推生成风险结论。"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import qmc

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
OUT=ROOT/'08_results'/'q5'/'drafts'
sys.path[:0]=[str(HERE),str(ROOT/'08_results'/'q3'/'code')]
import q5_optimize_robustness as q
import q3_optimize_pareto as q3

def src_r2(x,y):
    xs=(x-x.mean(0))/x.std(0,ddof=1); ys=(y-y.mean(0))/y.std(0,ddof=1)
    design=np.c_[np.ones(len(xs)),xs]; coef=np.linalg.lstsq(design,ys,rcond=None)[0]
    fit=design@coef; r2=1-((ys-fit)**2).sum(0)/(ys**2).sum(0)
    return coef[1:],r2

def texrows(df,cols,fmts):
    return '\n'.join(' & '.join(f.format(r[c]) for c,f in zip(cols,fmts))+r' \\' for _,r in df.iterrows())

def main():
    data=q.DATA; figs=q.FIG
    pin,base=q3.read_data(); ridge,pchip=q3.build_surrogate(pin,base)
    # 已由20k样本优化得到的域内设计；只在鲁棒可行域内报告正式风险。
    summary=json.loads((data/'q45_robustness_summary.json').read_text(encoding='utf-8'))
    sx=np.array([summary['struct']['a'],summary['struct']['b'],summary['struct']['N']])
    proj=np.array([.2249317396262705,4.4625,6.])
    eps=q.lhs_struct(20000,seed=20260720)
    formal=[]
    for name,x in [('名义可行投影',proj),('问题5结构鲁棒',sx)]:
        f0=q3.predict(x[None,:],ridge,pchip)[0]; vals=q.structure_samples(x,eps,ridge,pchip); c=q.score(vals)
        formal.append([name,*x,q.score(f0),c.mean(),c.std(ddof=1),np.quantile(c,.95),q.cvar(c)])
    formal=pd.DataFrame(formal,columns=['方案','a','b','N','名义评分','均值','标准差','Q95','CVaR95'])
    # 带符号SRC及R2：A类（20k）和B类S2-A（12k，实为原程序情景复核样本）。
    va=q.structure_samples(sx,eps,ridge,pchip); ca=q.score(va); ba,r2a=src_r2(eps,np.c_[va,ca])
    u=qmc.LatinHypercube(4,seed=20260721).random(12000)
    ee=qmc.scale(u[:,:2],[-.025,-.025],[.025,.025]); sm=qmc.scale(u[:,[2]],[.95],[1.05]).ravel(); sq=qmc.scale(u[:,[3]],[.95],[1.05]).ravel()
    vb=q.operation_values(sx,ee,sm,sq,ridge,pchip,(.5,.5,.5,.5),'A'); cb=q.score(vb); bb,r2b=src_r2(np.c_[ee,sm,sq],np.c_[vb,cb])
    signed=pd.DataFrame(np.vstack([ba,bb]),index=[r'$\varepsilon_a^{str}$',r'$\varepsilon_b^{str}$',r'$\varepsilon_a^{op}$',r'$\varepsilon_b^{op}$',r'$s_m^{op}$',r'$s_q^{op}$'],columns=['热目标','P','U','综合评分'])
    r2=pd.DataFrame([['加工误差SRC',*r2a],['S2-A工况SRC',*r2b]],columns=['模型','热目标','P','U','综合评分'])
    formal.to_csv(data/'q5_formal_domain_risk.csv',index=False,encoding='utf-8-sig'); signed.to_csv(data/'q5_signed_src.csv',encoding='utf-8-sig'); r2.to_csv(data/'q5_src_r2.csv',index=False,encoding='utf-8-sig')
    scen=pd.read_csv(data/'q4_representative_scenarios_corrected.csv'); regret=pd.read_csv(data/'q4_regret_comparison.csv'); conv=pd.read_csv(data/'q4_convergence_corrected.csv'); ops=pd.read_csv(data/'q5_operation_design_comparison.csv')
    ops['相对风险增幅']=(ops['结构鲁棒CVaR']/ops['最优CVaR']-1)
    ops.to_csv(data/'q5_operation_design_comparison.csv',index=False,encoding='utf-8-sig')
    # 使用与总论文一致的无数字小节标题，避免“2 问题5A”。
    tex=rf'''\documentclass[UTF8,a4paper,10pt]{{ctexart}}
\usepackage{{geometry,booktabs,float,graphicx,amsmath}}\geometry{{margin=1.9cm}}\setlength{{\parskip}}{{.2em}}
\title{{APMCM B题问题4--5：偏好及扰动鲁棒性（最终修订）}}\author{{}}\date{{}}\begin{{document}}\maketitle
\section*{{问题4：权重变化与偏好鲁棒设计}}
固定问题3的理想点与Nadir点，定义
\[z_k(x)=\frac{{F_k(x)-F_k^I}}{{F_k^N-F_k^I}},\quad
G(x;w)=\max_k\{{3w_kz_k(x)\}}+10^{{-4}}\sum_k3w_kz_k(x),\quad
w_k\ge0,\ \sum_kw_k=1.\]
对每组权重令$G^*(w)=\min_{{x\in\mathcal P_{{ref}}}}G(x;w)$，偏好机会损失为$r_{{pref}}(x,w)=G(x;w)-G^*(w)$，最终模型为
\[x_{{pref}}^{{rob}}=\arg\min_{{x\in\mathcal P_{{ref}}}}\max_{{w\in\mathcal W_H}}r_{{pref}}(x,w).\]
由于$G$对三个最小化目标单调不减，被支配方案不可能优于支配它的方案，故可在问题3全局Pareto参考集上搜索。等权$w=(1/3,1/3,1/3)$下$(a,b,N)=(.224932,4.500000,6)$且$G=.386383$，与问题3严格闭合。$H=25,50,100$均给出同一最小最大遗憾方案；$\max r_{{pref}}=1.15896>1$并非概率异常：极端权重下$\lambda_k=3w_k$可达3，评分损失不受$[0,1]$限制。
\begin{{table}}[H]\centering\scriptsize\caption{{精确代表权重下的专属最优解（各行评分不能横向比较）}}\begin{{tabular}}{{lrrrrrrr}}\toprule 场景&a&b&N&R&P&U&G\\\midrule
{texrows(scen,['场景','a','b','N','R','P','U','G'],['{}','{:.4f}','{:.4f}','{:.0f}','{:.6f}','{:.6f}','{:.6f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
\begin{{table}}[H]\centering\scriptsize\caption{{偏好遗憾与网格收敛}}\begin{{tabular}}{{lrrr}}\toprule 方案&最大遗憾&平均遗憾&P95遗憾\\\midrule
{texrows(regret,['方案','最大遗憾','平均遗憾','P95遗憾'],['{}','{:.5f}','{:.5f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\quad\begin{{tabular}}{{rrrrrr}}\toprule H&权重数&a&b&N&最大遗憾\\\midrule
{texrows(conv,['H','权重数','a','b','N','最大遗憾'],['{:.0f}','{:.0f}','{:.4f}','{:.4f}','{:.0f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
无针肋在1326个$H=50$权重下从未成为最优；$N=2,4,6,8,10$的区域占比分别为3.8%、55.8%、22.7%、2.6%、15.0%。$N=4$覆盖权重区域最多，而$N=6$最小化最坏机会损失；前者衡量场景出现区域，后者衡量跨场景最坏损失，二者标准不同并不矛盾。\begin{{figure}}[H]\centering\includegraphics[width=.86\linewidth]{{../../05_figures/q4/fig_q4_01_weight_mapping.pdf}}\caption{{权重到最优设计的映射；右图颜色表示$b^*$}}\end{{figure}}
\section*{{问题5：加工误差与工况波动}}
题目未给出真实制造公差和工况波动统计，以下均为参数化中等扰动情景，只用于方案相对比较，不解释为设备实际失效概率或真实公差标准。$\varepsilon_a,\varepsilon_b\in[-.025,.025]$分别对应$|\Delta a|\le.005$和$|\Delta b|\le.0375$。
\subsection*{{A类：代理模型域内的加工鲁棒结论}}
中等公差为独立均匀$\varepsilon_a,\varepsilon_b\sim U[-.025,.025]$，实际尺寸$a^r=a+.20\varepsilon_a,b^r=b+1.50\varepsilon_b$。正式CVaR使用种子20260720的$L=20000$个LHS样本，40,000样本复核。$C_{{str}}=\max_kz_k(\widehat F(x^r))+10^{{-4}}\sum_kz_k(\widehat F(x^r))$，$\mathrm{{CVaR}}_{{.95}}=E[C\mid C\ge\mathrm{{VaR}}_{{.95}}]$。
问题3名义、问题4偏好鲁棒和最佳原始样本均有$b=4.5$；在对称公差下约50%的实现值满足$b^r>4.5$，超出代理模型支持域，故\textbf{{不计算正式均值、分位数或CVaR}}。定义名义可行投影$x_{{proj}}=(.224932,4.4625,6)$，仅将名义$b$内移至鲁棒边界。
\begin{{table}}[H]\centering\scriptsize\caption{{鲁棒可行域内的正式加工风险比较}}\begin{{tabular}}{{lrrrrrrrr}}\toprule 方案&a&b&N&名义评分&均值&标准差&Q95&CVaR95\\\midrule
{texrows(formal,['方案','a','b','N','名义评分','均值','标准差','Q95','CVaR95'],['{}','{:.6f}','{:.4f}','{:.0f}','{:.5f}','{:.5f}','{:.5f}','{:.5f}','{:.5f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
正式加工鲁棒推荐为$\boxed{{(a,b,N)=(.224006,4.4625,6)}}$。相对$x_{{proj}}$，其CVaR仅下降{(formal.iloc[0].CVaR95-formal.iloc[1].CVaR95)/formal.iloc[0].CVaR95:.2%}：主要风险改善来自可行域收缩将$b$移离名义边界，进一步优化只微调$a$。
\subsection*{{敏感性方向与稳定性}}
带符号SRC由$\mathrm{{SRC}}_{{kj}}=\hat\beta_{{kj}}\sigma_{{X_j}}/\sigma_{{Y_k}}$计算；表中$R^2$为相应标准化线性回归的解释度。加工误差中$\varepsilon_b$主导综合评分；S2-A中$s_q$主要正向放大热目标与综合风险，$s_m$使压降正向增加而使热目标和$U$下降。加工分析的热目标为$R$，工况分析的热目标为$\Theta_R$。\begin{{figure}}[H]\centering\includegraphics[width=.86\linewidth]{{../../05_figures/q5/fig_q5_04_signed_sensitivity.pdf}}\caption{{带符号SRC；第一列在加工分析中为$R$、工况分析中为$\Theta_R$}}\end{{figure}}
\begin{{table}}[H]\centering\scriptsize\caption{{SRC线性近似的$R^2$}}\begin{{tabular}}{{lrrrr}}\toprule 模型&热目标&P&U&综合评分\\\midrule
{texrows(r2,['模型','热目标','P','U','综合评分'],['{}','{:.3f}','{:.3f}','{:.3f}','{:.3f}'])}\\\bottomrule\end{{tabular}}\end{{table}}
S2-A下三个单项性能的$R^2$接近1，而综合评分$R^2=.787$，说明增强切比雪夫评分的最大值算子引入分段非线性；SRC仅用于识别方向和主要影响因素，不解释为严格方差贡献率。
\subsection*{{B类：工况机理情景，不替代A类结论}}
工况修正定义为
\[P^{{op}}=\widehat P(x^r)[\alpha_Ps_m+(1-\alpha_P)s_m^2],\quad
R^{{op}}=\widehat R(x^r)[\theta_R+(1-\theta_R)s_m^{{-m_R}}],\quad \Theta_R=s_qR^{{op}},\]
\[U_A^{{op}}=\widehat U(x^r)s_m^{{-m_U}},\qquad U_B^{{op}}=\widehat U(x^r)s_qs_m^{{-m_U}}.\]
\begin{{table}}[H]\centering\scriptsize\caption{{机理参数情景}}\begin{{tabular}}{{lrrrrl}}\toprule 情景&$\alpha_P$&$\theta_R$&$m_R$&$m_U$&解释\\\midrule
S1&.80&.75&.25&.25&弱流量敏感\\S2&.50&.50&.50&.50&中等混合机制\\S3&.20&.25&.80&.80&强流量敏感\\\bottomrule\end{{tabular}}\end{{table}}
优化阶段对所有候选共用种子20260721生成的固定$L=3000$点LHS情景，以降低候选间Monte Carlo噪声；确定候选后，重新生成$L=12000$点LHS集作后验CVaR评价，未声称已完成24,000点收敛验证。六类结果均同时包含中等加工公差$\varepsilon_a,\varepsilon_b\sim U[-.025,.025]$与独立均匀$s_m,s_q\sim U[.95,1.05]$。评分为$C_{{op}}$，以$(\Theta_R,P^{{op}},U^{{op}})$按问题3固定尺度组成。
\begin{{table}}[H]\centering\scriptsize\caption{{中等加工公差与±5%运行波动共同作用下的机理情景结果}}\begin{{tabular}}{{llrrrrrr}}\toprule 情景&U模型&a&b&N&最优CVaR&结构鲁棒CVaR&相对增幅\\\midrule
{texrows(ops,['情景','U模型','a','b','N','最优CVaR','结构鲁棒CVaR','相对风险增幅'],['{}','{}','{:.4f}','{:.4f}','{:.0f}','{:.5f}','{:.5f}','{:.1%}'])}\\\bottomrule\end{{tabular}}\end{{table}}
U模型A的低风险解集中于$N=10$，模型B集中于$N=4$，且$a\approx.22-.24,b\approx3.08-3.48$；排数对$U$的尺度定义敏感。故B类结果不能唯一确定工况专用结构。
结构鲁棒方案在六类工况下的CVaR均高于情景专属最优，说明加工鲁棒并不等同于工况鲁棒，机理形式会实质改变排数选择。在物性常数与线性传热近似下，入口温度主要平移绝对芯片温度基线；因缺少无量纲指标反归一化关系而不进入综合评分。外侧自然对流同样缺少变工况样本，保持名义值。
\begin{{table}}[H]\centering\scriptsize\caption{{问题4--5的最终工程推荐}}\begin{{tabular}}{{p{{2.3cm}}p{{3.0cm}}p{{2.5cm}}p{{4.2cm}}}}\toprule 使用条件&推荐方案&结果性质&主要结论\\\midrule
名义等权&$(.224932,4.5,6)$&域内代理优化&名义综合最优\\
权重不确定&$(.224932,4.5,6)$&偏好鲁棒&最大偏好遗憾最小\\
中等加工公差&$(.224006,4.4625,6)$&A类数据支持&避开$b=4.5$边界\\
工况模型A&$N=10$附近&B类机理情景&偏重降低热风险\\
工况模型B&$N=4$附近&B类机理情景&受热负荷缩放定义影响\\
最终工程推荐&$(.224006,4.4625,6)$&保守推荐&有数据支撑且具公差安全裕度\\\bottomrule\end{{tabular}}\end{{table}}
因此，在附件现有数据下正式采用加工鲁棒方案；待获得不同流量、热负荷下的CFD或实验数据后，再判定采用$N=4$或$N=10$的工况专用方案。\end{{document}}'''
    tex=tex.replace('%',r'\%')
    # 演示稿仅在确认的写作流程中更新；本入口只复现数据和证据边界。
if __name__=='__main__':main()
