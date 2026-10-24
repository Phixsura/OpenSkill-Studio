from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hopsworks import fleet_hopsworks_status
def test_hw():
    r = fleet_hopsworks_status([{"running": True, "feature_groups": 100, "models": 50}])
    assert r["feature_groups"] == 100
    assert r["all_running"]
