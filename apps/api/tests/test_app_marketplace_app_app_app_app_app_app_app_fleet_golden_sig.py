from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_golden_sig import fleet_golden_signals
def test_healthy():
    r = fleet_golden_signals(100, 1000, 0.5, 60)
    assert r["status"] == "healthy"
def test_critical():
    r = fleet_golden_signals(200, 500, 6, 50)
    assert r["status"] == "critical"
