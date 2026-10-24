from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_neondb import fleet_neondb_status
def test_neon():
    r = fleet_neondb_status([{"active": True, "compute_hours_24h": 10, "branches": 5}])
    assert r["compute_hours_24h"] == 10
    assert r["serverless"]
