from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deepnote import fleet_deepnote_status
def test_dn():
    r = fleet_deepnote_status([{"active": True, "projects": 100, "integrations": 15}])
    assert r["projects"] == 100
    assert r["all_active"]
