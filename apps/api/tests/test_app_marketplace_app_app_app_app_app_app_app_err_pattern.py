from app.services.app_marketplace_app_app_app_app_app_app_app_err_pattern import detect_patterns

def test_patterns():
    r = detect_patterns([
        {"error_type": "timeout", "service": "api", "message": "Connection timed out"},
        {"error_type": "timeout", "service": "api", "message": "Connection timed out"},
        {"error_type": "timeout", "service": "worker", "message": "Connection timed out"},
        {"error_type": "auth_failed", "service": "api", "message": "Invalid token"},
    ], min_occurrences=3)
    assert r["unique_patterns"] == 1
    assert r["patterns"][0]["pattern"] == "timeout"
    assert r["patterns"][0]["count"] == 3
    assert len(r["patterns"][0]["services"]) == 2
