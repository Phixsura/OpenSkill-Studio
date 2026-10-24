from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_feat_adopt import fleet_feature_adoption
def test_adopt():
    r = fleet_feature_adoption([{"adoption_pct": 80}, {"adoption_pct": 30}, {"adoption_pct": 90}])
    assert r["widely_adopted"] == 2
    assert r["avg_adoption_pct"] == 66.7
    assert r["good"]
