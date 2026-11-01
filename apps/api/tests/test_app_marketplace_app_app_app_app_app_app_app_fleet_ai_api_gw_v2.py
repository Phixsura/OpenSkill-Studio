from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_api_gw_v2 import fleet_ai_api_gateway_v2
def test_agv2():
    r = fleet_ai_api_gateway_v2([{"active": True, "routes": 500, "requests_24h": 1000000000, "auth_methods": 5}])
    assert r["routes"] == 500
    assert r["secure"]
