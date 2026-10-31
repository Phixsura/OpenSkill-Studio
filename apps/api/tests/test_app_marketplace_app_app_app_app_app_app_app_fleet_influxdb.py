from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_influxdb import fleet_influxdb_status
def test_idb():
    r = fleet_influxdb_status([{"healthy": True, "series": 10000000, "writes_per_sec": 500000}])
    assert r["series"] == 10000000
    assert r["all_healthy"]
