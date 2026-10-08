import os
import re
import random
import tarfile
import urllib.request
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import Dataset

# ==========================================
# 0. GLOBAL SETUP & REPRODUCIBILITY
# ==========================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

# ==========================================
# 1. DATASET DOWNLOAD & EXTRACTION
# ==========================================
print("--- Step 1: Downloading & Extracting Datasets ---")

DATASET_URLS = {
    "spamassassin_easy_ham": "https://spamassassin.apache.org/old/publiccorpus/20030228_easy_ham.tar.bz2",
    "spamassassin_spam": "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2",
}

def download_and_extract(url, extract_path):
    archive_path = os.path.join(extract_path, os.path.basename(url))
    if not os.path.exists(archive_path):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, archive_path)
    
    print(f"Extracting {archive_path}...")
    if archive_path.endswith(".tar.bz2") or archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:*") as tar:
            tar.extractall(path=extract_path)

for name, url in DATASET_URLS.items():
    download_and_extract(url, DATA_DIR)

# Parsing functions for raw SpamAssassin email files
def parse_email_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return "", "", ""

    parts = content.split("\n\n", 1)
    header = parts[0] if len(parts) > 0 else ""
    body = parts[1] if len(parts) > 1 else ""

    # Extract Subject
    subject_match = re.search(r"^Subject:\s*(.*)$", header, re.IGNORECASE | re.MULTILINE)
    subject = subject_match.group(1).strip() if subject_match else ""

    # Extract From / Domain
    from_match = re.search(r"^From:\s*(.*)$", header, re.IGNORECASE | re.MULTILINE)
    from_line = from_match.group(1).strip() if from_match else ""
    domain_match = re.search(r"@([\w\.-]+)", from_line)
    domain = domain_match.group(1).lower() if domain_match else "unknown"

    return domain, subject, body

def load_spamassassin_folder(folder_path, label):
    records = []
    if not os.path.exists(folder_path):
        return records
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath) and fname != "cmds":
            domain, subject, body = parse_email_file(fpath)
            records.append({
                "domain": domain,
                "subject": subject,
                "body": body,
                "label": label
            })
    return records

# Load parsed datasets
easy_ham_path = os.path.join(DATA_DIR, "easy_ham")
spam_path = os.path.join(DATA_DIR, "spam")

ham_records = load_spamassassin_folder(easy_ham_path, label=0)
spam_records = load_spamassassin_folder(spam_path, label=1)

raw_df = pd.DataFrame(ham_records + spam_records)
print(f"Total raw emails loaded: {len(raw_df)}")

# ==========================================
# 2. TEXT CLEANING & FORMATTING
# ==========================================
print("\n--- Step 2: Cleaning & Formatting Text ---")

def clean_email_text(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize URLs
    text = re.sub(r'http[s]?://\S+', ' [URL] ', text)
    # Normalize Whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_email_input(row):
    domain = str(row.get('domain', '')).strip()
    subject = str(row.get('subject', '')).strip()
    body = clean_email_text(row.get('body', ''))
    return f"from: {domain} | subject: {subject} | body: {body}"

raw_df['text'] = raw_df.apply(format_email_input, axis=1)

# ==========================================
# 3. DEDUPLICATION & LABEL CONFLICT RESOLUTION
# ==========================================
print("\n--- Step 3: Resolving Label Conflicts & Deduplicating ---")

# FIX: Check label uniqueness FIRST before calling drop_duplicates
label_counts = raw_df.groupby("text")["label"].nunique()
conflicting_texts = label_counts[label_counts > 1].index

if len(conflicting_texts) > 0:
    print(f"Found {len(conflicting_texts)} conflicting texts. Removing them...")
    raw_df = raw_df[~raw_df["text"].isin(conflicting_texts)]
else:
    print("No conflicting labels found across identical texts.")

# Safe deduplication after removing conflicts
raw_df = raw_df.drop_duplicates(subset=["text"]).reset_index(drop=True)
print(f"Cleaned dataset size: {len(raw_df)} records")

# ==========================================
# 4. STRATIFIED TRAIN / VAL / TEST SPLIT
# ==========================================
print("\n--- Step 4: Splitting Data ---")

train_val_df, test_df = train_test_split(
    raw_df, test_size=0.15, random_state=SEED, stratify=raw_df['label']
)

train_df, val_df = train_test_split(
    train_val_df, test_size=0.1765, random_state=SEED, stratify=train_val_df['label']
)

print(f"Train size: {len(train_df)} | Val size: {len(val_df)} | Test size: {len(test_df)}")

# ==========================================
# 5. BASELINE MODEL (TF-IDF + LOGISTIC REGRESSION)
# ==========================================
print("\n--- Step 5: Training Baseline Model ---")

vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1, 2))
X_train = vectorizer.fit_transform(train_df['text'])
X_val = vectorizer.transform(val_df['text'])

baseline = LogisticRegression(max_iter=1000)
baseline.fit(X_train, train_df['label'])

val_preds = baseline.predict(X_val)
print("Logistic Regression Validation Results:")
print(classification_report(val_df['label'], val_preds))

# ==========================================
# 6. TRANSFORMER FINE-TUNING (DistilBERT)
# ==========================================
print("\n--- Step 6: Fine-Tuning DistilBERT ---")

MODEL_NAME = "distilbert-base-uncased"
MAXLEN = 256  # Increased to capture email headers + body context

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=MAXLEN
    )

ds_train = Dataset.from_pandas(train_df[['text', 'label']])
ds_val = Dataset.from_pandas(val_df[['text', 'label']])
ds_test = Dataset.from_pandas(test_df[['text', 'label']])

ds_train = ds_train.map(tokenize_function, batched=True)
ds_val = ds_val.map(tokenize_function, batched=True)
ds_test = ds_test.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=3,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=torch.cuda.is_available(),
    logging_steps=100,
    seed=SEED
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=ds_train,
    eval_dataset=ds_val,
    processing_class=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()

# Final evaluation
print("\n--- Final DistilBERT Evaluation on Test Set ---")
test_results = trainer.evaluate(ds_test)
print(test_results)

# Save final artifacts
SAVE_DIR = "./saved_distilbert_email_model"
model.save_pretrained(SAVE_DIR)
tokenizer.save_pretrained(SAVE_DIR)
print(f"\nModel and tokenizer successfully saved to {SAVE_DIR}")
