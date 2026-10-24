from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_memcached import fleet_memcached_status
def test_mc():
    r = fleet_memcached_status([{"alive": True, "items": 5000000, "hit_rate_pct": 92}])
    assert r["items"] == 5000000
    assert r["effective"]
