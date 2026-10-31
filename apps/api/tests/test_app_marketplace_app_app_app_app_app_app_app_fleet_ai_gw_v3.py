from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gw_v3 import fleet_ai_gateway_v3
def test_gv3():
    r = fleet_ai_gateway_v3([{"active": True, "providers": 10, "requests_24h": 1000000000, "cost_saved_pct": 35}])
    assert r["providers"] == 10
    assert r["unified"]
