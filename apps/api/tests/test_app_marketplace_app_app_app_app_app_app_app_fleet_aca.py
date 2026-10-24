from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_aca import fleet_aca_status
def test_aca():
    r = fleet_aca_status([{"running_status": "Running", "replicas": 5, "revisions": 10}])
    assert r["replicas"] == 5
    assert r["all_running"]
