import pandas as pd, numpy as np, xgboost as xgb, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from features import FEATS, GRAPH_FEATS
X = pd.read_pickle("features.pkl").sort_values("ts").reset_index(drop=True)
n = len(X); tr, va, te = X.iloc[:int(.6*n)], X.iloc[int(.6*n):int(.75*n)], X.iloc[int(.75*n):]
print("split fraud rates:", [round(100*d.label.mean(), 2) for d in (tr, va, te)])
TARGET_FPR = 0.005

def thr_at_fpr(y, p, fpr):
    return np.quantile(p[y == 0], 1 - fpr)
def evaluate(name, p_val, p_te):
    t = thr_at_fpr(va.label.values, p_val, TARGET_FPR * 0.8)       # 20% safety margin chosen on validation
    pred = p_te >= t; y = te.label.values
    tp = (pred & (y == 1)).sum(); fp = (pred & (y == 0)).sum()
    r = dict(model=name, roc_auc=roc_auc_score(y, p_te), pr_auc=average_precision_score(y, p_te), threshold=float(t),
             recall=tp / (y == 1).sum(), precision=tp / max(pred.sum(), 1), fpr=fp / (y == 0).sum())
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}); return r

res = []
# baseline 1: logistic regression on all features
lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, class_weight="balanced")).fit(tr[FEATS], tr.label)
res.append(evaluate("LogReg (all feats)", lr.predict_proba(va[FEATS])[:, 1], lr.predict_proba(te[FEATS])[:, 1]))

params = dict(n_estimators=120, max_depth=4, learning_rate=0.12, subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
              scale_pos_weight=10, tree_method="hist", n_jobs=1, eval_metric="aucpr", random_state=0)
# ablation: no graph features (transaction + device only)
flat = [f for f in FEATS if f not in GRAPH_FEATS]
m0 = xgb.XGBClassifier(**params).fit(tr[flat], tr.label)
res.append(evaluate("XGB (txn+device only)", m0.predict_proba(va[flat])[:, 1], m0.predict_proba(te[flat])[:, 1]))
# full model
m = xgb.XGBClassifier(**params).fit(tr[FEATS], tr.label)
pv, pt = m.predict_proba(va[FEATS])[:, 1], m.predict_proba(te[FEATS])[:, 1]
res.append(evaluate("XGB (txn+device+graph)", pv, pt))
m.get_booster().save_model("model.json"); m.get_booster().save_model("model.ubj")
json.dump(res, open("results.json", "w"), indent=1, default=float)

# per fraud-type recall of the final model
t = res[-1]["threshold"]; te = te.assign(p=pt, hit=pt >= t)
print("\nRecall by fraud type (test):"); print(te[te.label == 1].groupby("kind").hit.agg(["mean", "count"]).round(3))
print("False positives by legit kind (test):"); print(te[(te.label == 0) & te.hit].kind.value_counts())
te[te.label == 1].groupby("kind").hit.mean().to_csv("recall_by_type.csv")

imp = pd.Series(m.feature_importances_, FEATS).sort_values()
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
imp.tail(15).plot.barh(ax=ax[0], color="#4c78a8"); ax[0].set_title("XGBoost feature importance (gain, top 15)")
for nm, p in [("LogReg", lr.predict_proba(te[FEATS])[:, 1]), ("XGB no-graph", m0.predict_proba(te[flat])[:, 1]), ("XGB full", pt)]:
    pr, rc, _ = precision_recall_curve(te.label, p); ax[1].plot(rc, pr, label=nm)
ax[1].set_xlabel("recall"); ax[1].set_ylabel("precision"); ax[1].set_title("Precision-recall (test, temporal split)"); ax[1].legend()
plt.tight_layout(); plt.savefig("model_eval.png", dpi=110)
