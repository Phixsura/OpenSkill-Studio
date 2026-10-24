from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_multi_reg import fleet_ai_multi_region
def test_mr():
    r = fleet_ai_multi_region([{"active": True, "regions": ["us-east", "eu-west", "ap-south", "us-west"], "rps": 500000, "failover_ok": True}])
    assert r["regions"] == 4
    assert r["global"]
