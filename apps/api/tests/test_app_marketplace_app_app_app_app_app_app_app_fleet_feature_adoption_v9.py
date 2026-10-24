from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_feature_adoption_v9 import fleet_feature_adoption_v9
def test_fa_v9():
    r = fleet_feature_adoption_v9([{"launched": True, "adoption_pct": 85}])
    assert r["widely_adopted"] == 1
    assert r["healthy"]
