from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bicep import fleet_bicep_status
def test_bicep():
    r = fleet_bicep_status([{"status": "Succeeded"}, {"status": "Failed"}])
    assert r["succeeded"] == 1
    assert not r["healthy"]
