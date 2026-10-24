from app.services.app_marketplace_app_app_app_app_app_app_app_ops_score import calculate_ops_score

def test_high():
    r = calculate_ops_score({"uptime_pct": 99.99, "p99_ms": 50, "observability_pct": 95,
                              "doc_coverage_pct": 90, "automation_pct": 85, "security_score": 95})
    assert r["grade"] == "A"
    assert r["score"] > 90

def test_low():
    r = calculate_ops_score({"uptime_pct": 95, "p99_ms": 2000, "observability_pct": 20,
                              "doc_coverage_pct": 10, "automation_pct": 5, "security_score": 30})
    assert r["grade"] == "F"
