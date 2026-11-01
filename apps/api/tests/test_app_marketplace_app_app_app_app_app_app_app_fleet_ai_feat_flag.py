from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_feat_flag import fleet_ai_feature_flag
def test_ff():
    r = fleet_ai_feature_flag([{"active": True, "flags": 200, "enabled": 150, "evaluations_24h": 100000000}])
    assert r["flags"] == 200
    assert r["controlled"]
