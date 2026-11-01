from app.services.app_marketplace_app_app_error_recovery import select_strategy, build_recovery_report

def test_retry():
    r = select_strategy(error_type="timeout", retry_count=0, max_retries=3)
    assert r["strategy"] == "retry"
    assert r["auto_recoverable"]

def test_circuit_break():
    r = select_strategy(error_type="timeout", retry_count=3, max_retries=3)
    assert r["strategy"] == "circuit_break"

def test_fallback():
    r = select_strategy(error_type="not_found", retry_count=5, max_retries=3)
    assert r["strategy"] == "fallback"

def test_report():
    errors = [
        {"error": "timeout", "strategy": "retry", "recovered": True},
        {"error": "timeout", "strategy": "circuit_break", "recovered": True},
        {"error": "unknown", "strategy": "manual", "recovered": False},
    ]
    r = build_recovery_report(errors=errors)
    assert r["recovered"] == 2
    assert r["recovery_rate"] == 66.7
