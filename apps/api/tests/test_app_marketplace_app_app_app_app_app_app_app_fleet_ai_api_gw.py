from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_api_gw import fleet_ai_api_gateway
def test_aagw():
    r = fleet_ai_api_gateway([{"active": True, "providers": 10, "requests_24h": 20000000, "cost_24h": 100000}])
    assert r["providers"] == 10
    assert r["cost_24h"] == 100000
