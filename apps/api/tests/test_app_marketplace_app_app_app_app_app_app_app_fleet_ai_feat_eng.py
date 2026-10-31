from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_feat_eng import fleet_ai_feature_engineering
def test_fe():
    r = fleet_ai_feature_engineering([{"active": True, "features": 1000, "transforms": 5000, "impact_pct": 25}])
    assert r["features"] == 1000
    assert r["impactful"]
