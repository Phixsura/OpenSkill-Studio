from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_aspire import fleet_aspire_status
def test_asp():
    r = fleet_aspire_status([{"running": True, "services": 10, "resources": 30}])
    assert r["services"] == 10
    assert r["all_running"]
