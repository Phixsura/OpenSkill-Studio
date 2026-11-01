from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_feature_flags import fleet_feature_flags
def test_flags():
    r = fleet_feature_flags([{"enabled": True, "age_days": 10}, {"enabled": False, "age_days": 100}, {"enabled": True, "age_days": 5}])
    assert r["enabled"] == 2
    assert r["stale"] == 1
    assert r["needs_cleanup"]
