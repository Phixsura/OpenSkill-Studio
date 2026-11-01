from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_circleci import fleet_circleci_status
def test_cci():
    r = fleet_circleci_status([{"status": "success", "credits": 100}] * 9 + [{"status": "failed", "credits": 50}])
    assert r["success_rate"] == 90.0
    assert r["credits_used"] == 950
