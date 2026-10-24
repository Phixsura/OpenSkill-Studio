from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_feast import fleet_feast_status
def test_feast():
    r = fleet_feast_status([{"active": True, "feature_views": 50, "entities": 20}])
    assert r["feature_views"] == 50
    assert r["all_active"]
