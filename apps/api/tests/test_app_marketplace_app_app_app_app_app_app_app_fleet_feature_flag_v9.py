from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_feature_flag_v9 import fleet_feature_flag_v9
def test_ff_v9():
    r = fleet_feature_flag_v9([{"enabled": True, "rollout_pct": 100, "days_since_change": 5}])
    assert r["enabled"] == 1
    assert r["stale"] == 0
    assert r["healthy"]
