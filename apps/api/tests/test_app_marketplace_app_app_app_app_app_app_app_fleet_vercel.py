from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vercel import fleet_vercel_status
def test_vc():
    r = fleet_vercel_status([{"status": "READY", "requests_24h": 5000000, "edge_functions": 10}])
    assert r["requests_24h"] == 5000000
    assert r["all_deployed"]
