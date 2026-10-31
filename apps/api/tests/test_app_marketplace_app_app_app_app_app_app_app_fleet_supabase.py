from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_supabase import fleet_supabase_status
def test_sb():
    r = fleet_supabase_status([{"status": "ACTIVE_HEALTHY", "db_size_gb": 50, "api_requests_24h": 1000000}])
    assert r["api_requests_24h"] == 1000000
    assert r["all_healthy"]
