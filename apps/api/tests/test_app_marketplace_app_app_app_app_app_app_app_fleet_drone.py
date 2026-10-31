from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_drone import fleet_drone_status
def test_drone():
    r = fleet_drone_status([{"status": "success", "steps": 5}] * 8 + [{"status": "failure", "steps": 3}] * 2)
    assert r["success_rate"] == 80.0
    assert r["avg_steps"] == 4.6
