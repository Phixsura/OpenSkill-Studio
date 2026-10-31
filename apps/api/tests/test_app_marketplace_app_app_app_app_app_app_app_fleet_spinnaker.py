from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spinnaker import fleet_spinnaker_status
def test_spin():
    r = fleet_spinnaker_status([{"status": "SUCCEEDED"}, {"status": "SUCCEEDED"}, {"status": "TERMINAL"}])
    assert r["succeeded"] == 2
    assert r["success_rate"] == 66.7
