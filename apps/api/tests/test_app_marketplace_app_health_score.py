from app.services.app_marketplace_app_health_score import compute_health_score

def test_excellent():
    r = compute_health_score(uptime_pct=99.99, error_rate=0.1, avg_response_ms=80,
                              review_avg=4.8, update_frequency_days=7)
    assert r["grade"] == "A"
    assert r["score"] > 90

def test_poor():
    r = compute_health_score(uptime_pct=90, error_rate=10, avg_response_ms=2000,
                              review_avg=2.0, update_frequency_days=365)
    assert r["grade"] in ("D", "F")

def test_breakdown():
    r = compute_health_score(uptime_pct=99.9, error_rate=1, avg_response_ms=200,
                              review_avg=4.0, update_frequency_days=30)
    assert "uptime" in r["breakdown"]
    assert "errors" in r["breakdown"]
