from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hygraph import fleet_hygraph_status
def test_hg():
    r = fleet_hygraph_status([{"active": True, "models": 30, "entries": 50000}])
    assert r["models"] == 30
    assert r["all_active"]
