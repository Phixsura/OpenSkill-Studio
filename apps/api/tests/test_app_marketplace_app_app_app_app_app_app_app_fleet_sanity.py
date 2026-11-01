from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sanity import fleet_sanity_status
def test_sanity():
    r = fleet_sanity_status([{"active": True, "documents": 100000, "datasets": 3}])
    assert r["documents"] == 100000
    assert r["all_active"]
