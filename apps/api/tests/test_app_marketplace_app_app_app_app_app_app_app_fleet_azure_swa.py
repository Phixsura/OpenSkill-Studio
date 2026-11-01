from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_azure_swa import fleet_azure_swa_status
def test_swa():
    r = fleet_azure_swa_status([{"deployed": True, "api_functions": 10, "custom_domains": 2}])
    assert r["api_functions"] == 10
    assert r["all_deployed"]
