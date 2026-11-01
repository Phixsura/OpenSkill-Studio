from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_woodpecker import fleet_woodpecker_status
def test_wp():
    r = fleet_woodpecker_status([{"status": "success", "duration_sec": 120}, {"status": "failure"}])
    assert r["success"] == 1
    assert r["failed"] == 1
