# UPI Fraud Detection: Lightweight Transaction Risk Classifier
**Neurons: AI/ML Engineering project (internal)**

## 1. Problem statement
Identify mule-account transfers and fraudulent UPI collect requests from transaction metadata and device-fingerprint changes, within 200 ms of initiation, at a false-positive rate (FPR) below 0.5%.

## 2. Approach
- **Data:** a synthetic dataset of 273,355 transactions over 30 days (1.16% fraud). It includes normal P2P and merchant traffic, merchant hubs, benign forwarding (rent splits) and "sleeper" mule accounts as hard negatives, and 110 mule rings. Fraud episodes cover collect-request scams, account takeover on a rogue device, and coerced pay via remote access, followed by rapid layering and cash-out. Layering is partly slow-burn, mule ages overlap legitimate new accounts, and device and amount signals overlap on purpose.
- **Leakage check:** the first version produced AUC = 1.0 for every model. The cause was a generator artefact (device-age distribution), which I fixed so device age depends only on the new-device flag. All reported numbers are from the corrected data.
- **Features (24, point-in-time):** every feature uses only events that happened before the transaction, with 24 h sliding windows. They fall into four groups:
  - Transaction: amount, ratio to the sender's mean, collect flag, night.
  - Device: new-device flag, device age, SIM change, accounts sharing the sender's or receiver's device.
  - Account: sender and receiver age, first-time pair.
  - Graph/velocity: receiver in/out degree, pass-through ratio, time since receiver or sender last received money, amount vs. last inbound amount, share of young senders, 1 h velocity.
- **Model:** XGBoost, 120 trees, depth 4, trained on the first 60% of time. The decision threshold is chosen on the next 15% (validation) to give FPR ≈ 0.4%, and the last 25% is the untouched test set (temporal split, no shuffling).

## 3. Results (test set, threshold fixed on validation)
| Model | ROC-AUC | PR-AUC | Recall | Precision | FPR |
|---|---|---|---|---|---|
| Logistic regression (all features) | 0.965 | 0.483 | 35.4% | 56.3% | 0.35% |
| XGBoost, txn + device only (ablation) | 0.945 | 0.361 | 29.8% | 48.9% | 0.39% |
| **XGBoost, txn + device + graph** | **0.996** | **0.911** | **89.3%** | **74.1%** | **0.40%** |

**FPR target met (0.40% < 0.5%).** Graph and velocity features account for the jump from about 30% to about 89% recall. The top features by gain are `sender_secs_since_last_in`, `amt_ratio_sender_last_in` and `recv_dev_shared_accts`. These capture money received and re-sent almost unchanged within minutes, and devices shared across ring accounts.

**Recall by fraud type:** layering 99.4%, cash-out 98.8%, collect scam 77.4%, ATO 56.8%, coerced pay 21.1%.
The weak spot is the first hop, where the victim pays a still-clean mule. Here the transfer looks like an ordinary payment, so it needs the behavioural-biometrics and remote-access signals from Strategic Problem Statements 1 and 2. The hops after it are caught reliably, so this model works best as the second layer, stopping the cash-out and the onward layering.

## 4. Benchmark (single thread, 1-vCPU container)
| Metric | Target | Measured |
|---|---|---|
| End-to-end p50 / p95 / p99 (feature extraction + inference) | < 200 ms | **0.15 / 0.33 / 0.57 ms** |
| Inference only p50 / p95 / p99 | < 50 ms | **0.12 / 0.26 / 0.38 ms** |
| Feature extraction p50 / p99 | n/a | 0.03 / 0.20 ms |
| Model size on disk | n/a | 181 KB (120 trees) |
| RAM added by loading the model | < 15 MB | **4.8 MB** |
| Batch throughput | n/a | ~850k txns/s |

Caveats:
1. The XGBoost runtime itself adds about 119 MB RSS when imported. This is fine for a backend scorer, but for true on-device use the trees should be compiled to a dependency-free form (Treelite, m2cgen or ONNX), which leaves roughly the 0.2 MB model.
2. Feature extraction reads in-memory 24 h windows. In production these would live in Redis or a feature store, so add network round-trip time (typically 1–5 ms) to the budget, which is still far inside 200 ms.

## 5. Limitations and next steps
- The data is synthetic, so absolute numbers will not transfer. Fraud patterns are simplified and the class balance is optimistic. Validate on real (anonymised) bank data before any claims. FPR must be re-measured on real traffic, where benign diversity is far greater.
- Add a shallow GNN (e.g. 2-layer GraphSAGE) to learn multi-hop ring structure, and compare it with the engineered features here.
- Fuse this model's score with the behavioural-biometrics and RASP signals to improve first-hop recall (coerced pay, ATO).
- Run the model in shadow mode, tune the threshold per segment, and add drift monitoring and periodic retraining.

## 6. Reproduce
```
python3 01_generate_data.py   # transactions.csv, accounts.csv
python3 02_features_eda.py    # features.pkl, eda_*.png
python3 03_train_eval.py      # model.ubj/.json, results.json, model_eval.png
python3 04_benchmark.py       # benchmark.json
```
Figures: `eda_distributions.png`, `eda_mule_graph.png`, `model_eval.png`.
