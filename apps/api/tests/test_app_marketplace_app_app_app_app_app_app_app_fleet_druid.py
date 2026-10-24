from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_druid import fleet_druid_status
def test_druid():
    r = fleet_druid_status([{"healthy": True, "segments": 50000, "qps": 5000}])
    assert r["segments"] == 50000
    assert r["all_healthy"]
