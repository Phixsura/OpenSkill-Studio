from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_timeout_v9 import fleet_api_timeout_v9
def test_ato_v9():
    r = fleet_api_timeout_v9([{"timeout_configured": True, "timeouts_today": 0, "timeout_ms": 5000}])
    assert r["timeouts_today"] == 0
    assert r["healthy"]
