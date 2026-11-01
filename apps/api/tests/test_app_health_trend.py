from app.services.app_health_trend import compute_health_trend

def test_improving():
    r = compute_health_trend([{"score": 80}, {"score": 90}])
    assert r["trend"] == "improving"
    assert r["change"] == 10

def test_declining():
    r = compute_health_trend([{"score": 95}, {"score": 80}])
    assert r["trend"] == "declining"

def test_stable():
    r = compute_health_trend([{"score": 95}, {"score": 96}])
    assert r["trend"] == "stable"

def test_empty():
    r = compute_health_trend([])
    assert r["trend"] == "stable"
    assert r["current"] == 100
