from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_clerk import fleet_clerk_status
def test_clerk():
    r = fleet_clerk_status([{"active": True, "users": 50000, "sessions_24h": 100000}])
    assert r["users"] == 50000
    assert r["all_active"]
