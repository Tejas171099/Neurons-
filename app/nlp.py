"""Adapter between Vishnu's pipeline and Shruti's DistilBERT NLP evaluation model."""
from __future__ import annotations

import importlib
import os
import re
from typing import Protocol

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .models import RiskLevel, TextReport
from .risk import level_for


class TextAnalyzer(Protocol):
    def analyze(self, subject: str, body: str) -> TextReport: ...


class DistilBertTextAnalyzer:
    """Loads and evaluates Shruti's fine-tuned DistilBERT model."""

    def __init__(self, model_path: str = "./saved_distilbert_email_model"):
        self.model_path = model_path
        if os.path.exists(model_path):
            print(f"Loading trained DistilBERT model from '{model_path}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.eval()
            self.is_loaded = True
        else:
            print(f"Warning: Model directory '{model_path}' not found. Falling back to heuristic rule set.")
            self.is_loaded = False

    def analyze(self, subject: str, body: str) -> TextReport:
        if not self.is_loaded:
            return HeuristicTextAnalyzer().analyze(subject, body)

        # Match Shruti's exact token formatting logic: "from: ... | subject: ... | body: ..."
        formatted_text = f"from: unknown | subject: {subject} | body: {body}"

        inputs = self.tokenizer(
            formatted_text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=256
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
            # Assumes Index 1 corresponds to Spam / Phishing
            phishing_prob = float(probs[1].item())

        score = int(phishing_prob * 100)
        risk_level = level_for(score)

        return TextReport(
            phishing_probability=round(phishing_prob, 2),
            risk_level=risk_level,
            signals=[f"DistilBERT Confidence: {round(phishing_prob * 100, 1)}%"]
        )


_CUES = {
    r"verify (your )?(account|identity|details)": 0.25,
    r"(account|card).{0,30}(suspend|block|lock|expire)": 0.25,
    r"(update|confirm).{0,20}(kyc|password|details|pan|aadhaar)": 0.25,
    r"\b(urgent|immediately|within 24 hours|final notice)\b": 0.15,
    r"click (here|the link|below)": 0.10,
    r"\b(otp|cvv|pin)\b": 0.15,
}


class HeuristicTextAnalyzer:
    """Fallback heuristic analyzer if transformer model weights are missing."""

    def analyze(self, subject: str, body: str) -> TextReport:
        text = f"{subject}\n{body}".lower()
        hits = [(pattern, weight) for pattern, weight in _CUES.items() if re.search(pattern, text)]
        prob = min(sum(w for _, w in hits), 0.99)
        return TextReport(
            phishing_probability=round(prob, 2),
            risk_level=level_for(int(prob * 100)),
            signals=[p for p, _ in hits],
        )


def load_analyzer() -> TextAnalyzer:
    spec = os.environ.get("NLP_ANALYZER", "").strip()
    if spec:
        module_name, _, attr = spec.partition(":")
        factory = getattr(importlib.import_module(module_name), attr)
        return factory()
    
    # Default to DistilBertTextAnalyzer if saved model exists
    return DistilBertTextAnalyzer()
