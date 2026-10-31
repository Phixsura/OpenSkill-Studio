from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spot_instance_v9 import fleet_spot_instance_v9
def test_si2_v9():
    r = fleet_spot_instance_v9([{"status": "running", "interrupted": False, "savings_pct": 70}])
    assert r["avg_savings_pct"] == 70.0
    assert r["healthy"]
