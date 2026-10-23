from app.services.app_marketplace_app_app_health_score import calculate_health_score

def test_perfect():
    r = calculate_health_score(scores={"reliability": 100, "performance": 100, "security": 100, "quality": 100})
    assert r["overall"] == 100
    assert r["grade"] == "A+"

def test_mixed():
    r = calculate_health_score(scores={"reliability": 90, "performance": 70, "security": 80, "quality": 60})
    # 90*0.3 + 70*0.25 + 80*0.25 + 60*0.2 = 27 + 17.5 + 20 + 12 = 76.5
    assert r["overall"] == 76.5
    assert r["grade"] == "C"
    assert r["status"] == "degraded"

def test_critical():
    r = calculate_health_score(scores={"reliability": 30, "performance": 40, "security": 50, "quality": 20})
    assert r["status"] == "critical"
    assert r["grade"] == "F"
