from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tfserving import fleet_tfserving_status
def test_tfs():
    r = fleet_tfserving_status([{"serving": True, "models": 10, "batches_per_sec": 5000}])
    assert r["models"] == 10
    assert r["all_serving"]
