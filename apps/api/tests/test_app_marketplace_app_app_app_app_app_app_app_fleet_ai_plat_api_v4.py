from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_api_v4 import fleet_ai_api_v4
def test_av4():
    r = fleet_ai_api_v4([{"active": True, "endpoints": 1000, "requests_24h": 10000000000, "p99_ms": 20, "error_pct": 0.01}])
    assert r["endpoints"] == 1000
    assert r["healthy"]
