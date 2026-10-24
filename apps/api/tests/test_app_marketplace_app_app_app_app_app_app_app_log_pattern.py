from app.services.app_marketplace_app_app_app_app_app_app_app_log_pattern import detect_patterns

def test_patterns():
    lines = [
        "Request 123 completed in 50ms",
        "Request 456 completed in 80ms",
        "Request 789 completed in 30ms",
        "Error connecting to database",
        "Error connecting to database",
        "Error connecting to database",
    ]
    r = detect_patterns(lines, min_count=3)
    assert r["total_lines"] == 6
    assert r["recurring_count"] >= 2
    assert any("Request" in p["pattern"] for p in r["patterns"])
    assert any("Error" in p["pattern"] for p in r["patterns"])
