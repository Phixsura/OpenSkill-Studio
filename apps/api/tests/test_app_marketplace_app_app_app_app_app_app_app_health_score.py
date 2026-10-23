from app.services.app_marketplace_app_app_app_app_app_app_app_health_score import calculate_health_score, compare_scores

def test_score():
    r = calculate_health_score({"uptime": 99.9, "error_rate": 95, "latency": 85, "throughput": 90, "saturation": 80})
    assert r["grade"] in ("A", "B")
    assert r["score"] > 80
    assert r["status"] == "healthy"

def test_compare():
    c = calculate_health_score({"uptime": 99, "error_rate": 95, "latency": 90, "throughput": 85, "saturation": 80})
    p = calculate_health_score({"uptime": 80, "error_rate": 70, "latency": 60, "throughput": 50, "saturation": 40})
    r = compare_scores(c, p)
    assert r["improved"]
    assert r["delta"] > 0
