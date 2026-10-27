from app.services.app_marketplace_extension_health_score import ExtHealthScoreService, HealthMetrics

def test_perfect_score():
    svc = ExtHealthScoreService()
    m = HealthMetrics(uptime_pct=100, error_rate_pct=0, avg_response_ms=50,
                      update_frequency_days=3, open_issues=0,
                      test_coverage_pct=95, security_score=100)
    result = svc.calculate(m)
    assert result["score"] >= 90
    assert result["grade"] == "A"

def test_poor_score():
    svc = ExtHealthScoreService()
    m = HealthMetrics(uptime_pct=95, error_rate_pct=5, avg_response_ms=800,
                      update_frequency_days=120, open_issues=20,
                      test_coverage_pct=20, security_score=30)
    result = svc.calculate(m)
    assert result["grade"] in ("D", "F")

def test_compare():
    svc = ExtHealthScoreService()
    a = HealthMetrics(uptime_pct=99.9, error_rate_pct=0.5)
    b = HealthMetrics(uptime_pct=95, error_rate_pct=3)
    cmp = svc.compare(a, b)
    assert cmp["winner"] == "a"
