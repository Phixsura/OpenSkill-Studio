from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_contract_v9 import fleet_api_contract_v9
def test_apc_v9():
    r = fleet_api_contract_v9([{"verified": True, "breaking_change": False, "consumers": 10}])
    assert r["breaking_changes"] == 0
    assert r["healthy"]
