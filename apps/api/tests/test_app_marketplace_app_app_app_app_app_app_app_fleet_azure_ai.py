from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_azure_ai import fleet_azure_ai
def test_aai():
    r = fleet_azure_ai([{"active": True, "calls_24h": 5000000, "deployed_models": 10}])
    assert r["calls_24h"] == 5000000
    assert r["all_active"]
