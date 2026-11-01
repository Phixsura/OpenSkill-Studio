from app.services.app_developer_app_health_overview import build_health_overview

def test_overview():
    apps = [{"name": "A", "health_score": 98}, {"name": "B", "health_score": 85}, {"name": "C", "health_score": 60}]
    o = build_health_overview(apps)
    assert o["healthy"] == 1
    assert o["degraded"] == 1
    assert o["critical"] == 1
    assert o["worst_app"]["name"] == "C"

def test_empty():
    o = build_health_overview([])
    assert o["total"] == 0
    assert o["avg_score"] == 100
