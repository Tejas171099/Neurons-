import os, sys, time, json, numpy as np, pandas as pd, psutil, subprocess
from features import FEATS, FeatureStore

# --- memory in a clean subprocess: import xgboost, then load model, then score ---
probe = '''
import psutil, os, numpy as np
p = psutil.Process(os.getpid()); r0 = p.memory_info().rss / 2**20
import xgboost as xgb; r1 = p.memory_info().rss / 2**20
b = xgb.Booster(); b.load_model("model.ubj"); b.set_param({"nthread": 1})
x = xgb.DMatrix(np.zeros((1, %d), dtype=np.float32)); b.predict(x, validate_features=False); r2 = p.memory_info().rss / 2**20
print(r0, r1, r2)''' % len(FEATS)
r0, r1, r2 = map(float, subprocess.check_output([sys.executable, "-c", probe]).split())

# --- latency: end-to-end (stateful feature extraction + inference) on the held-out tail ---
import xgboost as xgb
df = pd.read_csv("transactions.csv"); acc = pd.read_csv("accounts.csv"); n = len(df); cut = int(.75 * n)
fs = FeatureStore(acc)
for t in df.iloc[:cut].itertuples(index=False): fs.update(t.ts, t.sender, t.receiver, t.amount)   # warm the 24h window state
b = xgb.Booster(); b.load_model("model.ubj"); b.set_param({"nthread": 1})
fe, inf = [], []
for t in df.iloc[cut:cut + 6000].itertuples(index=False):
    a = time.perf_counter()
    f = fs.features(t.ts, t.sender, t.receiver, t.amount, t.is_collect, t.sender_new_device, t.sender_dev_age_hrs, t.sim_changed)
    m = time.perf_counter()
    b.inplace_predict(np.asarray([f], dtype=np.float32), validate_features=False)
    z = time.perf_counter(); fe.append((m - a) * 1e3); inf.append((z - m) * 1e3); fs.update(t.ts, t.sender, t.receiver, t.amount)
fe, inf = np.array(fe[200:]), np.array(inf[200:]); tot = fe + inf
q = lambda v: {"p50": round(float(np.percentile(v, 50)), 3), "p95": round(float(np.percentile(v, 95)), 3), "p99": round(float(np.percentile(v, 99)), 3)}
# batch throughput
Xb = np.random.rand(10000, len(FEATS)).astype(np.float32); a = time.perf_counter(); b.inplace_predict(Xb, validate_features=False); thr = 10000 / (time.perf_counter() - a)
bst = json.loads(b.save_raw("json")); ntrees = len(bst["learner"]["gradient_booster"]["model"]["trees"])
out = dict(model_file_kb=round(os.path.getsize("model.ubj") / 1024, 1), model_json_kb=round(os.path.getsize("model.json") / 1024, 1), n_trees=ntrees,
           rss_baseline_mb=r0, rss_after_import_mb=r1, rss_after_model_mb=r2, model_load_delta_mb=round(r2 - r1, 2), xgb_import_delta_mb=round(r1 - r0, 1),
           feature_ms=q(fe), inference_ms=q(inf), end_to_end_ms=q(tot), batch_throughput_per_s=int(thr))
json.dump(out, open("benchmark.json", "w"), indent=1); print(json.dumps(out, indent=1))
