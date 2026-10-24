from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_redis import fleet_redis_status
def test_redis():
    r = fleet_redis_status([{"role": "master", "keys": 1000000, "memory_pct": 60}, {"role": "replica", "keys": 1000000, "memory_pct": 55}])
    assert r["masters"] == 1
    assert r["total_keys"] == 2000000
    assert r["healthy"]
