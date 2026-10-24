from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_secret_rot import fleet_secret_rotation
def test_rotation():
    r = fleet_secret_rotation([{"age_days": 30}, {"age_days": 91}, {"age_days": 10}])
    assert r["stale"] == 1
    assert r["fresh"] == 2
    assert not r["compliant"]
