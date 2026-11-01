from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_istio import fleet_istio_status
def test_istio():
    r = fleet_istio_status([{"config_synced": True, "version": "1.20"}, {"config_synced": False, "version": "1.19"}])
    assert r["synced"] == 1
    assert r["version_mismatch"] == 1
    assert not r["healthy"]
