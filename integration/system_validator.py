import time

def scan_with_timeout_failsafe(email_data, max_timeout=2.0):
    """
    Simulates E2E scanning pipeline with hard 2s fail-safe execution.
    """
    start_time = time.perf_counter()
    
    simulated_delay = email_data.get("simulated_delay", 0.5)
    time.sleep(simulated_delay)
    
    elapsed_time = time.perf_counter() - start_time
    
    if elapsed_time > max_timeout:
        return {
            "status": "UNDER_REVIEW",
            "risk_level": "UNDER_REVIEW",
            "message": "Validation exceeded 2.0s - fail-safe triggered",
            "scan_ms": round(elapsed_time * 1000, 2),
            "fallback_triggered": True
        }
    else:
        return {
            "status": "SUCCESS",
            "risk_level": "CRITICAL" if email_data.get("is_phishing") else "LOW",
            "scan_ms": round(elapsed_time * 1000, 2),
            "fallback_triggered": False
        }

if __name__ == "__main__":
    fast_scan = {"is_phishing": True, "simulated_delay": 0.4}
    slow_scan = {"is_phishing": True, "simulated_delay": 2.3}
    
    print("⚡ Fast Scan Result:", scan_with_timeout_failsafe(fast_scan))
    print("⚠️ Slow Network Scan Result:", scan_with_timeout_failsafe(slow_scan))
