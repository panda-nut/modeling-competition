from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.base import clone
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import LinearRegression, Ridge, RidgeCV
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "08_results"
sys.path.insert(0, str(RESULTS / "q3" / "code"))
sys.path.insert(0, str(RESULTS / "q4" / "code"))
import q3_optimize_pareto as q3
import q4_optimize_preferences as q45

Q1_DATA = RESULTS / "q1" / "data"
Q2_VALIDATION = RESULTS / "q2" / "data" / "validation"
Q3_VALIDATION = RESULTS / "q3" / "data" / "validation"
Q4_VALIDATION = RESULTS / "q4" / "data" / "validation"
Q5_VALIDATION = RESULTS / "q5" / "data" / "validation"
for folder in (Q1_DATA, Q2_VALIDATION, Q3_VALIDATION, Q4_VALIDATION, Q5_VALIDATION):
    folder.mkdir(parents=True, exist_ok=True)
RESP = ["R", "P", "U"]
IDEAL, SPAN = q45.IDEAL, q45.SPAN
N_LEVELS = q3.N_LEVELS


def anova_contributions(pin: pd.DataFrame) -> pd.DataFrame:
    rows = []
    levels = {v: sorted(pin[v].unique()) for v in ["a", "b", "N"]}
    na, nb, nn = map(lambda v: len(levels[v]), ["a", "b", "N"])
    for y in RESP:
        grand = pin[y].mean()
        ma = pin.groupby("a")[y].mean(); mb = pin.groupby("b")[y].mean(); mn = pin.groupby("N")[y].mean()
        mab = pin.groupby(["a", "b"])[y].mean(); man = pin.groupby(["a", "N"])[y].mean(); mbn = pin.groupby(["b", "N"])[y].mean()
        ss = {}
        ss["a"] = nb * nn * sum((ma.loc[a] - grand) ** 2 for a in levels["a"])
        ss["b"] = na * nn * sum((mb.loc[b] - grand) ** 2 for b in levels["b"])
        ss["N"] = na * nb * sum((mn.loc[n] - grand) ** 2 for n in levels["N"])
        ss["a×b"] = nn * sum((mab.loc[a,b] - ma.loc[a] - mb.loc[b] + grand) ** 2 for a in levels["a"] for b in levels["b"])
        ss["a×N"] = nb * sum((man.loc[a,n] - ma.loc[a] - mn.loc[n] + grand) ** 2 for a in levels["a"] for n in levels["N"])
        ss["b×N"] = na * sum((mbn.loc[b,n] - mb.loc[b] - mn.loc[n] + grand) ** 2 for b in levels["b"] for n in levels["N"])
        residual = []
        for r in pin.itertuples(index=False):
            two = ((mab.loc[r.a,r.b] - ma.loc[r.a] - mb.loc[r.b] + grand)
                   + (man.loc[r.a,r.N] - ma.loc[r.a] - mn.loc[r.N] + grand)
                   + (mbn.loc[r.b,r.N] - mb.loc[r.b] - mn.loc[r.N] + grand))
            fitted2 = grand + (ma.loc[r.a]-grand) + (mb.loc[r.b]-grand) + (mn.loc[r.N]-grand) + two
            residual.append(getattr(r,y) - fitted2)
        ss["a×b×N"] = float(np.sum(np.square(residual)))
        total = float(np.sum((pin[y] - grand) ** 2))
        for term, value in ss.items():
            rows.append([y, term, value, value / total])
    return pd.DataFrame(rows, columns=["响应", "效应", "SS", "贡献率"])


def categorical_design(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    poly = PolynomialFeatures(3, include_bias=False).fit_transform(x[:, :2])
    d = np.column_stack([(x[:, 2] == n).astype(float) for n in N_LEVELS[1:]])
    return np.column_stack([poly, d] + [poly * d[:, [j]] for j in range(d.shape[1])])


def mech_design(x: np.ndarray) -> np.ndarray:
    a, b, n = np.asarray(x, float).T
    return np.column_stack([a*n, a*a*n, 1/b, 1/(b*b), a*n/b])


def fit_encoding_models(pin: pd.DataFrame):
    x = pin[["a","b","N"]].to_numpy(float)
    ranges = np.ptp(pin[RESP].to_numpy(float), axis=0)
    schemes = ["数值三次", "类别交互", "分层响应面", "机理特征"]
    sq = {s: np.zeros(3) for s in schemes}; count = {s: 0 for s in schemes}
    for rep in range(10):
        kf = KFold(5, shuffle=True, random_state=20260730 + rep)
        for tr, te in kf.split(x):
            for k, yname in enumerate(RESP):
                y = pin[yname].to_numpy(float)
                numeric = make_pipeline(StandardScaler(), PolynomialFeatures(3, include_bias=False), StandardScaler(), Ridge(alpha=[1e-5,1e-2,1e-3][k]))
                categorical = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-6,1,24)))
                mechanism = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-6,2,30)))
                pred_num = numeric.fit(x[tr], y[tr]).predict(x[te])
                pred_cat = categorical.fit(categorical_design(x[tr]), y[tr]).predict(categorical_design(x[te]))
                pred_mech = mechanism.fit(mech_design(x[tr]), y[tr]).predict(mech_design(x[te]))
                pred_layer = np.empty(len(te))
                for n in N_LEVELS:
                    trn = tr[x[tr,2] == n]; ten_pos = np.flatnonzero(x[te,2] == n)
                    if len(ten_pos):
                        model = make_pipeline(PolynomialFeatures(3, include_bias=False), StandardScaler(), RidgeCV(alphas=np.logspace(-6,1,24)))
                        model.fit(x[trn,:2], y[trn]); pred_layer[ten_pos] = model.predict(x[te[ten_pos],:2])
                for s, pred in zip(schemes, [pred_num,pred_cat,pred_layer,pred_mech]):
                    sq[s][k] += np.sum((y[te]-pred)**2)
            for s in schemes: count[s] += len(te)
    rows=[]
    for s in schemes:
        rmse=np.sqrt(sq[s]/count[s]); rows.append([s,*list(rmse/ranges)])

    full = {"数值三次":{},"类别交互":{},"分层响应面":{},"机理特征":{}}
    for k,yname in enumerate(RESP):
        y=pin[yname].to_numpy(float)
        full["数值三次"][yname]=make_pipeline(StandardScaler(),PolynomialFeatures(3,include_bias=False),StandardScaler(),Ridge(alpha=[1e-5,1e-2,1e-3][k])).fit(x,y)
        full["类别交互"][yname]=make_pipeline(StandardScaler(),RidgeCV(alphas=np.logspace(-6,1,24))).fit(categorical_design(x),y)
        full["机理特征"][yname]=make_pipeline(StandardScaler(),RidgeCV(alphas=np.logspace(-6,2,30))).fit(mech_design(x),y)
        full["分层响应面"][yname]={}
        for n in N_LEVELS:
            take=x[:,2]==n
            full["分层响应面"][yname][n]=make_pipeline(PolynomialFeatures(3,include_bias=False),StandardScaler(),RidgeCV(alphas=np.logspace(-6,1,24))).fit(x[take,:2],y[take])
    return pd.DataFrame(rows,columns=["编码","R_NRMSE","P_NRMSE","U_NRMSE"]), full


def predict_scheme(x: np.ndarray, models, scheme: str) -> np.ndarray:
    x=np.asarray(x,float); ans=[]
    for y in RESP:
        if scheme=="类别交互": pred=models[scheme][y].predict(categorical_design(x))
        elif scheme=="机理特征": pred=models[scheme][y].predict(mech_design(x))
        elif scheme=="数值三次": pred=models[scheme][y].predict(x)
        else:
            pred=np.empty(len(x))
            for n in N_LEVELS:
                take=x[:,2]==n
                if take.any(): pred[take]=models[scheme][y][n].predict(x[take,:2])
        ans.append(pred)
    return np.column_stack(ans)


def score(f):
    z=(np.asarray(f)-IDEAL)/SPAN
    return np.max(z,axis=-1)+1e-4*np.sum(z,axis=-1)


def optimize_predictor(predictor, label: str):
    candidates=[]
    a=np.linspace(.1,.3,121); b=np.linspace(3,4.5,121); aa,bb=np.meshgrid(a,b,indexing="ij")
    for n in N_LEVELS:
        x=np.column_stack([aa.ravel(),bb.ravel(),np.full(aa.size,n)])
        s=score(predictor(x)); j=int(np.argmin(s)); start=x[j,:2]
        fun=lambda v: float(score(predictor(np.array([[v[0],v[1],n]])))[0])
        opt=minimize(fun,start,method="SLSQP",bounds=[(.1,.3),(3,4.5)],options={"ftol":1e-12,"maxiter":150})
        xx=np.array([[opt.x[0],opt.x[1],n]]); ff=predictor(xx)[0]
        candidates.append([label,*xx[0],*ff,fun(opt.x)])
    return min(candidates,key=lambda r:r[-1])


def structured_holdout(pin: pd.DataFrame) -> pd.DataFrame:
    x=pin[["a","b","N"]].to_numpy(float); rows=[]
    for yname,alpha in zip(RESP,[1e-5,1e-2,1e-3]):
        y=pin[yname].to_numpy(float); pred=np.empty(len(y)); combo=[]
        for a in sorted(pin.a.unique()):
            for b in sorted(pin.b.unique()):
                te=np.isclose(x[:,0],a)&np.isclose(x[:,1],b); tr=~te
                m=make_pipeline(StandardScaler(),PolynomialFeatures(3,include_bias=False),StandardScaler(),Ridge(alpha=alpha)).fit(x[tr],y[tr])
                pred[te]=m.predict(x[te]); combo.append([a,b,np.sqrt(np.mean((y[te]-pred[te])**2))/np.ptp(y)])
        rows.append([yname,np.sqrt(np.mean((y-pred)**2))/np.ptp(y),max(z[2] for z in combo)])
    return pd.DataFrame(rows,columns=["响应","组合留出NRMSE","最差组合NRMSE"])


def fit_ols_gp(pin):
    x=pin[["a","b","N"]].to_numpy(float); models={"三次OLS":{},"Matérn GP":{}}
    for y in RESP:
        models["三次OLS"][y]=make_pipeline(StandardScaler(),PolynomialFeatures(3,include_bias=False),StandardScaler(),LinearRegression()).fit(x,pin[y])
        kernel=ConstantKernel(1.0,(1e-3,1e3))*Matern(np.ones(3),(1e-2,1e2),nu=2.5)+WhiteKernel(1e-6,(1e-10,1e-2))
        models["Matérn GP"][y]=make_pipeline(StandardScaler(),GaussianProcessRegressor(kernel=kernel,normalize_y=True,n_restarts_optimizer=1,random_state=2026)).fit(x,pin[y])
    return models


def pref_sensitivity(ref_f, ref_x):
    def g_for_w(f,w):
        z=(f-IDEAL)/SPAN; lam=3*w
        return np.max(z*lam,axis=1)+1e-4*np.sum(z*lam,axis=1)
    results=[]
    for domain,weights in [("完整单纯形",q45.simplex(50)),("w_k≥0.1",q45.simplex(50))]:
        if domain!="完整单纯形": weights=weights[np.all(weights>=.1-1e-12,axis=1)]
        max_abs=np.full(len(ref_f),-np.inf); max_rel=np.full(len(ref_f),-np.inf)
        for w in weights:
            g=g_for_w(ref_f,w); lo=g.min(); hi=g.max();
            max_abs=np.maximum(max_abs,g-lo); max_rel=np.maximum(max_rel,(g-lo)/(hi-lo+1e-12))
        for kind,arr in [("绝对遗憾",max_abs),("相对遗憾",max_rel)]:
            j=int(np.argmin(arr)); results.append([domain,kind,len(weights),*ref_x[j],arr[j]])
    return pd.DataFrame(results,columns=["权重域","判据","权重数","a","b","N","最大遗憾"])


def worst_case_ridge(ridge,pchip):
    def pred(x): return q3.predict(x,ridge,pchip)
    da=np.linspace(-.005,.005,15); db=np.linspace(-.0375,.0375,15); daa,dbb=np.meshgrid(da,db,indexing="ij")
    perturb=np.column_stack([daa.ravel(),dbb.ravel()])
    def worst(v,n):
        xx=np.column_stack([v[0]+perturb[:,0],v[1]+perturb[:,1],np.full(len(perturb),n)])
        return float(np.max(score(pred(xx))))
    candidates=[]
    a=np.linspace(.105,.295,81); b=np.linspace(3.0375,4.4625,81); aa,bb=np.meshgrid(a,b,indexing="ij")
    for n in N_LEVELS:
        best=(np.inf,None)
        pts=np.column_stack([aa.ravel(),bb.ravel()])
        for v in pts:
            val=worst(v,n)
            if val<best[0]: best=(val,v.copy())
        opt=minimize(lambda v:worst(v,n),best[1],method="SLSQP",
                     bounds=[(.105,.295),(3.0375,4.4625)],
                     options={"ftol":1e-12,"maxiter":180})
        v=np.asarray(opt.x); refined=worst(v,n)
        if refined > best[0]:
            v=np.asarray(best[1]); refined=best[0]
        candidates.append([v[0],v[1],n,refined])
    return min(candidates,key=lambda r:r[-1])


def main():
    pin,base=q3.read_data(); ridge,pchip=q3.build_surrogate(pin,base)
    anova=anova_contributions(pin); anova.to_csv(Q1_DATA/"q1_anova_contributions.csv",index=False,encoding="utf-8-sig")
    cv,enc_models=fit_encoding_models(pin); cv.to_csv(Q2_VALIDATION/"q2_encoding_cv.csv",index=False,encoding="utf-8-sig")
    opt=[]
    for scheme in ["数值三次","类别交互","分层响应面","机理特征"]:
        opt.append(optimize_predictor(lambda x,s=scheme:predict_scheme(x,enc_models,s),scheme))
    other=fit_ols_gp(pin)
    for label in other:
        opt.append(optimize_predictor(lambda x,l=label:np.column_stack([other[l][y].predict(x) for y in RESP]),label))
    def ensemble(x):
        preds=[predict_scheme(x,enc_models,"数值三次")]
        preds += [np.column_stack([other[l][y].predict(x) for y in RESP]) for l in other]
        return np.max(np.stack(preds),axis=0)
    opt.append(optimize_predictor(ensemble,"模型集合保守"))
    pd.DataFrame(opt,columns=["模型","a","b","N","R","P","U","评分"]).to_csv(Q3_VALIDATION/"q3_model_reoptimization.csv",index=False,encoding="utf-8-sig")
    structured_holdout(pin).to_csv(Q2_VALIDATION/"q2_structured_holdout.csv",index=False,encoding="utf-8-sig")
    ref=pd.read_csv(RESULTS/"q3"/"data"/"q3_pareto_reference_merged.csv")
    ref_x=ref[["a","b","N"]].to_numpy(float); ref_f=ref[["R","P","U"]].to_numpy(float)
    pref_sensitivity(ref_f,ref_x).to_csv(Q4_VALIDATION/"q4_preference_sensitivity.csv",index=False,encoding="utf-8-sig")
    wc=worst_case_ridge(ridge,pchip)
    summary={"worst_case":{"a":wc[0],"b":wc[1],"N":wc[2],"score":wc[3]}}
    (Q5_VALIDATION/"q5_worst_case_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False)); print(anova); print(cv); print(pd.DataFrame(opt));


if __name__=="__main__":
    main()
