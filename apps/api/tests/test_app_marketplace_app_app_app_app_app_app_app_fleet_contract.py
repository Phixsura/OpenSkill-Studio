from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_contract import fleet_contract_tests
def test_contract():
    r = fleet_contract_tests([{"status": "pass"}, {"status": "pass"}, {"status": "broken"}])
    assert r["passing"] == 2
    assert r["broken"] == 1
    assert not r["compatible"]
