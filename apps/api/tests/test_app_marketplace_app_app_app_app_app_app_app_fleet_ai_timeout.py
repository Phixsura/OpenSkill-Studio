from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_timeout import fleet_ai_timeout_manager
def test_tm():
    r = fleet_ai_timeout_manager([{"active": True, "timeouts_24h": 500, "default_ms": 30000, "adaptive": True}])
    assert r["default_ms"] == 30000
    assert r["smart"]
