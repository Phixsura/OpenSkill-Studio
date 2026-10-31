from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_innovation import fleet_innovation_index
def test_innovation():
    r = fleet_innovation_index({"new_features_30d": 20, "experiments_30d": 10, "feature_adoption_pct": 80})
    assert r["index"] == 32.5  # (40+10+80)/4
    assert not r["innovative"]
