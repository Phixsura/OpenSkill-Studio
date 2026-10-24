from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dapr import fleet_dapr_status
def test_dapr():
    r = fleet_dapr_status([{"sidecar_healthy": True, "components": 5}, {"sidecar_healthy": False, "components": 3}])
    assert r["healthy"] == 1
    assert r["components"] == 8
    assert not r["all_healthy"]
