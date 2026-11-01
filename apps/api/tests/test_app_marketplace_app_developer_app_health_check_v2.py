from app.services.app_marketplace_app_developer_app_health_check_v2 import compute_app_health_v2

def test_excellent():
    r = compute_app_health_v2(availability=99.99, performance_ms=80, error_rate=0.1, security_score=95, freshness_days=3)
    assert r["status"] == "excellent"

def test_poor():
    r = compute_app_health_v2(availability=85, performance_ms=3000, error_rate=15, security_score=20, freshness_days=180)
    assert r["status"] == "poor"

def test_dimensions():
    r = compute_app_health_v2(availability=99, performance_ms=200, error_rate=2, security_score=80, freshness_days=10)
    assert "availability" in r["dimensions"]
    assert r["composite"] > 0
