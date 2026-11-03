"""Synthetic UPI transaction generator: normal traffic, merchant hubs, benign forwarding
(hard negatives), mule-ring layering/cash-out, collect-request scams and account takeover."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
DAY = 86400
SPAN_DAYS = 30
N_USERS, N_MERCH, N_RINGS = 20000, 200, 110
N_NORMAL_TXN = 260_000

# ---------- accounts ----------
users = pd.DataFrame({
    "acct": np.arange(N_USERS),
    "age_days": np.where(rng.random(N_USERS) < 0.12, rng.integers(3, 90, N_USERS), np.clip(rng.lognormal(6.0, 0.9, N_USERS), 20, 4000)).astype(int),
    "mean_amt": np.clip(rng.lognormal(6.0, 0.9, N_USERS), 30, 20000),
    "device": np.arange(N_USERS),           # one device per user initially
    "is_mule": 0,
})
merch = pd.DataFrame({
    "acct": N_USERS + np.arange(N_MERCH),
    "age_days": rng.integers(200, 3000, N_MERCH),
    "mean_amt": np.clip(rng.lognormal(6.2, 0.8, N_MERCH), 50, 8000),
    "device": 10**6 + np.arange(N_MERCH), "is_mule": 0})
# mules: new accounts, devices shared inside a ring
mule_rows, rings = [], []
nxt = N_USERS + N_MERCH
for r in range(N_RINGS):
    size = rng.integers(4, 9)
    ids = list(range(nxt, nxt + size)); nxt += size
    shared_dev = 2 * 10**6 + r
    for a in ids:
        d = shared_dev if rng.random() < 0.25 else 3 * 10**6 + a
        mule_rows.append((a, rng.integers(3, 60) if rng.random() < 0.55 else rng.integers(60, 500), rng.lognormal(6.8, 0.7), d, 1))
    rings.append(ids)
mules = pd.DataFrame(mule_rows, columns=["acct", "age_days", "mean_amt", "device", "is_mule"])
accts = pd.concat([users, merch, mules], ignore_index=True).set_index("acct")

# ---------- normal traffic ----------
contacts = {u: rng.choice(N_USERS, 8, replace=False) for u in range(N_USERS)}
ev = []  # (ts, sender, receiver, amount, collect, new_dev, dev_age_hrs, sim_chg, label, kind)
def normal(n):
    s = rng.integers(0, N_USERS, n)
    ts = rng.uniform(0, SPAN_DAYS * DAY, n)
    # daytime-weighted
    hr = rng.choice(24, n, p=np.array([1,1,1,1,1,2,3,5,6,7,7,7,7,7,7,7,7,8,8,8,7,5,3,2], float) /
                    np.array([1,1,1,1,1,2,3,5,6,7,7,7,7,7,7,7,7,8,8,8,7,5,3,2]).sum())
    ts = (ts // DAY) * DAY + hr * 3600 + rng.uniform(0, 3600, n)
    kind = rng.choice(3, n, p=[0.50, 0.40, 0.10])      # p2p contact / merchant / random user
    r = np.where(kind == 0, [contacts[x][rng.integers(8)] for x in s],
         np.where(kind == 1, N_USERS + rng.integers(0, N_MERCH, n), rng.integers(0, N_USERS, n)))
    amt = np.clip(accts.loc[s, "mean_amt"].values * rng.lognormal(0, 0.8, n) * np.where(rng.random(n) < 0.05, rng.lognormal(1.8, 0.6, n), 1), 5, 100000)
    collect = (rng.random(n) < np.where(kind == 1, 0.35, 0.04)).astype(int)
    new_dev = rng.random(n) < 0.03                    # genuine phone upgrades
    dev_age = np.where(new_dev, rng.uniform(0, 48, n), rng.uniform(24 * 20, 24 * 400, n))
    sim = (rng.random(n) < 0.01).astype(int)
    ok = s != r
    return list(zip(ts[ok], s[ok], r[ok], amt[ok], collect[ok], new_dev[ok].astype(int), dev_age[ok], sim[ok],
                    [0] * ok.sum(), ["normal"] * ok.sum()))
ev += normal(N_NORMAL_TXN)

# benign forwarding (rent split, shared bills): hard negatives that look like layering
for _ in range(4000):
    a, b, c = rng.choice(N_USERS, 3, replace=False)
    t = rng.uniform(1 * DAY, SPAN_DAYS * DAY - 3600); amt = rng.lognormal(7.0, 0.7)
    ev.append((t, a, b, amt, 0, 0, 500.0, 0, 0, "benign_fwd"))
    ev.append((t + rng.uniform(300, 7200), b, c, amt * rng.uniform(0.5, 1.0), 0, 0, 500.0, 0, 0, "benign_fwd"))
# benign txns to young merchant-like accounts (so receiver age alone is not a giveaway)
for m in mules.acct.sample(400, random_state=1):         # sleeper mules behave normally pre-activation
    for _ in range(rng.integers(2, 10)):
        s = rng.integers(0, N_USERS)
        ev.append((rng.uniform(0, SPAN_DAYS * DAY), s, m, rng.lognormal(5.5, 0.6), 0, 0, 500.0, 0, 0, "benign_to_new"))

# ---------- fraud episodes ----------
def episode(ring, t0, kind):
    chain = list(rng.permutation(ring)); hops = rng.integers(2, min(7, len(chain)) + 1); chain = chain[:hops]
    victim = rng.integers(0, N_USERS)
    amt = float(np.clip(accts.loc[victim, "mean_amt"] * rng.lognormal(1.0, 0.9), 100, 90000))
    out = []
    if kind == "collect":
        out.append((t0, victim, chain[0], amt, 1, 0, 500.0, 0, 1, "collect_scam"))
    elif kind == "ato":                                   # cloned profile on rogue device
        out.append((t0, victim, chain[0], amt, 0, int(rng.random() < 0.7), rng.uniform(0, 30), int(rng.random() < 0.3), 1, "ato"))
    else:                                                 # coerced pay via remote-access app
        out.append((t0, victim, chain[0], amt, 0, int(rng.random() < 0.08), rng.uniform(0, 400), 0, 1, "coerced"))
    t = t0
    for i in range(len(chain) - 1):                       # rapid layering, ~2-8% skim
        t += rng.uniform(20, 1500) if rng.random() < 0.6 else rng.uniform(1500, 20000); amt *= rng.uniform(0.85, 0.99)
        out.append((t, chain[i], chain[i + 1], amt, 0, int(rng.random() < 0.12), rng.uniform(0, 400), 0, 1, "layering"))
    t += rng.uniform(30, 1800)                            # cash-out to merchant/wallet hub
    out.append((t, chain[-1], N_USERS + rng.integers(0, N_MERCH) if rng.random() < 0.6 else rng.integers(0, N_USERS), amt * rng.uniform(0.9, 0.99), 0, 0, rng.uniform(0, 300), 0, 1, "cashout"))
    return out
for ring in rings:
    for _ in range(rng.integers(4, 9)):
        t0 = rng.uniform(2 * DAY, SPAN_DAYS * DAY - 6 * 3600)
        # fraud skews toward off-hours but with heavy overlap
        t0 = (t0 // DAY) * DAY + rng.choice(24, p=np.r_[np.full(6, .06), np.full(12, .025), np.full(6, .06)] / (np.r_[np.full(6, .06), np.full(12, .025), np.full(6, .06)].sum())) * 3600 + rng.uniform(0, 3600)
        ev += episode(ring, t0, rng.choice(["collect", "ato", "coerced"], p=[.4, .25, .35]))

cols = ["ts", "sender", "receiver", "amount", "is_collect", "sender_new_device", "sender_dev_age_hrs", "sim_changed", "label", "kind"]
df = pd.DataFrame(ev, columns=cols).sort_values("ts").reset_index(drop=True)
# device age must depend only on the new-device flag (avoid generator leakage)
nd = df.sender_new_device.values == 1
df["sender_dev_age_hrs"] = np.where(nd, rng.uniform(0, 48, len(df)), rng.uniform(480, 9600, len(df)))
df["txn_id"] = np.arange(len(df))
df.to_csv("/home/claude/upi_fraud/transactions.csv", index=False)
accts.reset_index().to_csv("/home/claude/upi_fraud/accounts.csv", index=False)
print(df.shape, "fraud rate: %.3f%%" % (100 * df.label.mean()))
print(df.groupby("kind").label.agg(["count", "mean"]))
