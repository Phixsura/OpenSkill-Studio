from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kv_store_v9 import fleet_kv_store_v9
def test_kv_v9():
    r = fleet_kv_store_v9([{"ops_per_sec": 100000, "latency_us": 200, "total_keys": 5000000}])
    assert r["ops_per_sec"] == 100000
    assert r["healthy"]
