"""Streaming, point-in-time graph + device feature extractor (uses only past events)."""
import numpy as np, pandas as pd
from collections import defaultdict, deque

W = 86400
FEATS = ["amount", "log_amount", "amt_ratio_sender_mean", "is_collect", "is_night",
         "sender_new_device", "sender_dev_age_hrs", "sim_changed", "sender_dev_shared_accts", "recv_dev_shared_accts",
         "sender_age_days", "recv_age_days", "first_time_pair",
         "recv_in_deg_24h", "recv_out_deg_24h", "recv_pass_through", "recv_secs_since_last_in", "amt_ratio_recv_last_in",
         "recv_young_sender_frac", "sender_secs_since_last_in", "amt_ratio_sender_last_in", "sender_pass_through",
         "sender_txn_1h", "recv_txn_1h"]
GRAPH_FEATS = ["recv_in_deg_24h", "recv_out_deg_24h", "recv_pass_through", "recv_secs_since_last_in", "amt_ratio_recv_last_in",
               "recv_young_sender_frac", "sender_secs_since_last_in", "amt_ratio_sender_last_in", "sender_pass_through",
               "sender_txn_1h", "recv_txn_1h", "sender_dev_shared_accts", "recv_dev_shared_accts"]

class FeatureStore:
    def __init__(self, accts):
        a = accts.set_index("acct")
        self.age = a.age_days.to_dict(); self.mean = a.mean_amt.to_dict(); self.dev0 = a.device.to_dict()
        self.dev_accts = defaultdict(set)
        for ac, d in self.dev0.items(): self.dev_accts[d].add(ac)
        self.inn = defaultdict(deque); self.out = defaultdict(deque); self.pairs = set()
    def _trim(self, dq, t):
        while dq and dq[0][0] < t - W: dq.popleft()
    def features(self, ts, s, r, amt, coll, newdev, devage, sim):
        self._trim(self.inn[r], ts); self._trim(self.out[r], ts); self._trim(self.inn[s], ts); self._trim(self.out[s], ts)
        ri, ro, si, so = self.inn[r], self.out[r], self.inn[s], self.out[s]
        r_in_amt = sum(x[2] for x in ri); r_out_amt = sum(x[2] for x in ro)
        s_in_amt = sum(x[2] for x in si); s_out_amt = sum(x[2] for x in so)
        hr = (ts % W) / 3600
        young = (sum(1 for x in ri if self.age.get(x[1], 999) < 60) / len(ri)) if ri else 0.0
        return [amt, np.log1p(amt), amt / self.mean.get(s, amt), coll, int(hr < 6 or hr >= 23),
                newdev, devage, sim, len(self.dev_accts[self.dev0.get(s)]), len(self.dev_accts[self.dev0.get(r)]),
                self.age.get(s, 365), self.age.get(r, 365), int((s, r) not in self.pairs),
                len({x[1] for x in ri}), len({x[1] for x in ro}), r_out_amt / (r_in_amt + 1),
                (ts - ri[-1][0]) if ri else W, (amt / ri[-1][2]) if ri else 0.0,
                young, (ts - si[-1][0]) if si else W, (amt / si[-1][2]) if si else 0.0, s_out_amt / (s_in_amt + 1),
                sum(1 for x in so if x[0] > ts - 3600), sum(1 for x in ri if x[0] > ts - 3600)]
    def update(self, ts, s, r, amt):
        self.out[s].append((ts, r, amt)); self.inn[r].append((ts, s, amt)); self.pairs.add((s, r))

def build(df, accts):
    fs = FeatureStore(accts); rows = []
    for t in df.itertuples(index=False):
        rows.append(fs.features(t.ts, t.sender, t.receiver, t.amount, t.is_collect, t.sender_new_device, t.sender_dev_age_hrs, t.sim_changed))
        fs.update(t.ts, t.sender, t.receiver, t.amount)
    return pd.DataFrame(rows, columns=FEATS)
