from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_prismic import fleet_prismic_status
def test_pr():
    r = fleet_prismic_status([{"active": True, "documents": 10000, "slices": 200}])
    assert r["documents"] == 10000
    assert r["all_active"]
