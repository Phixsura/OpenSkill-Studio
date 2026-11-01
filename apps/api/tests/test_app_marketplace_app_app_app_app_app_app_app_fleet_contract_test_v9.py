from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_contract_test_v9 import fleet_contract_test_v9
def test_ct_v9():
    r = fleet_contract_test_v9([{"verified": True, "broken": False, "consumer": "web-app"}])
    assert r["verified"] == 1
    assert r["healthy"]
