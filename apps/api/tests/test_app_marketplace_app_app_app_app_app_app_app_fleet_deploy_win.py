from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deploy_win import fleet_deploy_window
def test_window():
    r = fleet_deploy_window([{"in_maintenance_window": True}, {"in_maintenance_window": False}])
    assert r["out_window"] == 1
    assert not r["compliant"]
