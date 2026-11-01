from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_garnet import fleet_garnet_status
def test_garnet():
    r = fleet_garnet_status([{"healthy": True, "ops_per_sec": 1000000, "p99_us": 50}])
    assert r["ops_per_sec"] == 1000000
    assert r["ultra_fast"]
