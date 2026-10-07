import json
import time

# Import Ruchit's detection modules
try:
    from app.spoof import detect_spoof
except ImportError:
    # Standalone fallback if running from integration/ directory
    def detect_spoof(display_name, sender_domain):
        class Result:
            is_spoofed = display_name.lower().replace(" ", "") not in sender_domain.lower()
        return Result()

def run_golden_test_suite():
    with open("benchmark_dataset.json", "r") as f:
        dataset = json.load(f)
    
    total = len(dataset)
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
    start_time = time.perf_counter()
    
    for item in dataset:
        domain = item["sender_email"].split("@")[-1] if "@" in item["sender_email"] else ""
        spoof_res = detect_spoof(item["display_name"], domain)
        
        has_urgency = any(kw in item["body"].lower() for kw in ["suspended", "24 hours", "immediate", "action required"])
        predicted_phishing = spoof_res.is_spoofed or has_urgency
        actual = item["is_phishing"]
        
        if predicted_phishing and actual:
            true_positives += 1
        elif predicted_phishing and not actual:
            false_positives += 1
        elif not predicted_phishing and not actual:
            true_negatives += 1
        elif not predicted_phishing and actual:
            false_negatives += 1

    total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    accuracy = round(((true_positives + true_negatives) / total) * 100, 2)
    
    print("=" * 50)
    print("🎯 NEURONS PROBLEM STATEMENT 2: GOLDEN TEST SUITE")
    print("=" * 50)
    print(f"Total Test Samples Evaluated: {total}")
    print(f"Overall Accuracy: {accuracy}% (Target: >99.5%)")
    print(f"True Positives (Phishing Caught): {true_positives}")
    print(f"False Positives (Clean Flagged Bad): {false_positives}")
    print(f"Total Suite Execution Time: {total_time_ms} ms")
    print("=" * 50)

if __name__ == "__main__":
    run_golden_test_suite()
