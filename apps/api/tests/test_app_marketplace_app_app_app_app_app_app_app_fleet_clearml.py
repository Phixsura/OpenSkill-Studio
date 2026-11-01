from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_clearml import fleet_clearml_status
def test_cml():
    r = fleet_clearml_status([{"running": True, "tasks_24h": 5000, "workers": 20}])
    assert r["tasks_24h"] == 5000
    assert r["all_running"]
