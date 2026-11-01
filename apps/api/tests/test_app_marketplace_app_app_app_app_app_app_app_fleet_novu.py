from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_novu import fleet_novu_status
def test_novu():
    r = fleet_novu_status([{"active": True, "notifications_24h": 1000000, "channels": 5}])
    assert r["notifications_24h"] == 1000000
    assert r["all_active"]
