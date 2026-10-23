from app.services.app_marketplace_app_api_health_score import compute_api_health_score

def test_excellent():
    r = compute_api_health_score(uptime_pct=99.99, avg_response_ms=80, error_rate=0.1,
                                  documentation_coverage=95, deprecation_count=0)
    assert r["grade"] in ("A+", "A")

def test_poor():
    r = compute_api_health_score(uptime_pct=90, avg_response_ms=2000, error_rate=10,
                                  documentation_coverage=20, deprecation_count=5)
    assert r["grade"] in ("D", "F")

def test_breakdown():
    r = compute_api_health_score(uptime_pct=99.9, avg_response_ms=150, error_rate=1,
                                  documentation_coverage=80, deprecation_count=1)
    assert "availability" in r["breakdown"]
    assert "performance" in r["breakdown"]
