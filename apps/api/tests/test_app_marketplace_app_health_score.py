from app.services.app_marketplace_app_health_score import calculate_health_score

def test_healthy():
    r = calculate_health_score(signals={
        "uptime": 99.9, "error_rate": 0.5, "latency": 5,
        "crash_free": 99.8, "user_satisfaction": 92})
    assert r["grade"] == "A"
    assert r["score"] > 90
    assert r["status"] == "healthy"

def test_degraded():
    r = calculate_health_score(signals={
        "uptime": 95, "error_rate": 10, "latency": 30,
        "crash_free": 90, "user_satisfaction": 60})
    assert r["grade"] in ("B", "C")

def test_unhealthy():
    r = calculate_health_score(signals={
        "uptime": 50, "error_rate": 50, "latency": 80,
        "crash_free": 40, "user_satisfaction": 20})
    assert r["status"] == "unhealthy"
    assert r["grade"] in ("D", "F")
