from app.services.app_marketplace_app_app_app_app_app_app_app_golden_signals import calculate_golden_signals

def test_healthy():
    r = calculate_golden_signals(50, 1000, 0.1, 45)
    assert r["status"] == "healthy"
    assert r["score"] == 4

def test_degraded():
    r = calculate_golden_signals(300, 1000, 3, 45)
    assert r["status"] == "degraded"
