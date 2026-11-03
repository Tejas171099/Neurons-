import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, networkx as nx, time
from features import build
df = pd.read_csv("transactions.csv"); acc = pd.read_csv("accounts.csv")
t0 = time.time(); X = build(df, acc); print("feature build %.1fs" % (time.time() - t0))
X["label"] = df.label.values; X["ts"] = df.ts.values; X["kind"] = df.kind.values; X["sender"] = df.sender; X["receiver"] = df.receiver
X.to_parquet("features.parquet") if False else X.to_pickle("features.pkl")

fig, ax = plt.subplots(2, 3, figsize=(15, 8))
for lab, c in [(0, "#4c78a8"), (1, "#e45756")]:
    d = X[X.label == lab]
    ax[0, 0].hist(np.log10(d.amount), bins=50, alpha=.6, color=c, density=True, label=["legit", "fraud"][lab])
    ax[0, 1].hist(np.log10(d.recv_secs_since_last_in.clip(1)), bins=50, alpha=.6, color=c, density=True)
    ax[0, 2].hist(d.recv_age_days.clip(0, 400), bins=40, alpha=.6, color=c, density=True)
    ax[1, 0].hist(d.sender_dev_age_hrs.clip(0, 300), bins=40, alpha=.6, color=c, density=True)
ax[0, 0].set_title("log10(amount)"); ax[0, 0].legend(); ax[0, 1].set_title("log10(secs since receiver last got money)")
ax[0, 2].set_title("receiver account age (days)"); ax[1, 0].set_title("sender device age (hrs)")
h = df.assign(hr=((df.ts % 86400) // 3600).astype(int)).groupby("hr").label.mean() * 100
ax[1, 1].bar(h.index, h.values, color="#e45756"); ax[1, 1].set_title("fraud rate by hour (%)")
k = df[df.label == 1].kind.value_counts(); ax[1, 2].bar(k.index, k.values, color="#f58518"); ax[1, 2].set_title("fraud txns by type"); ax[1, 2].tick_params(axis="x", rotation=30)
plt.tight_layout(); plt.savefig("eda_distributions.png", dpi=110)

# one mule ring subgraph
f = df[df.label == 1]; comp = nx.Graph(); comp.add_edges_from(zip(f.sender, f.receiver))
big = max(nx.connected_components(comp), key=len); sub = f[f.sender.isin(big)]
G = nx.DiGraph(); [G.add_edge(a, b) for a, b in zip(sub.sender, sub.receiver)]
mules = set(acc[acc.is_mule == 1].acct)
plt.figure(figsize=(7, 6)); pos = nx.spring_layout(G, seed=3)
nx.draw(G, pos, node_color=["#e45756" if n in mules else "#9ecae1" for n in G], node_size=60, width=.6, arrowsize=7)
plt.title("Fraud subgraph: victims (blue) feed mule ring (red)"); plt.savefig("eda_mule_graph.png", dpi=110)

print("\nMedian by class"); print(X.groupby("label")[["amount", "recv_secs_since_last_in", "recv_age_days", "recv_pass_through", "recv_in_deg_24h", "sender_dev_shared_accts"]].median().round(2))
print("\nFraud rate: new device %.1f%% vs known %.2f%%" % (100*X[X.sender_new_device==1].label.mean(), 100*X[X.sender_new_device==0].label.mean()))
print("Fraud rate: collect %.2f%% vs pay %.2f%%" % (100*X[X.is_collect==1].label.mean(), 100*X[X.is_collect==0].label.mean()))
