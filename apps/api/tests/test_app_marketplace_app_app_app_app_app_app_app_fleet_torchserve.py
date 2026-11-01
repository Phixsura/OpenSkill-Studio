from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_torchserve import fleet_torchserve_status
def test_ts():
    r = fleet_torchserve_status([{"healthy": True, "models": 5, "predictions_24h": 1000000}])
    assert r["models"] == 5
    assert r["all_healthy"]
