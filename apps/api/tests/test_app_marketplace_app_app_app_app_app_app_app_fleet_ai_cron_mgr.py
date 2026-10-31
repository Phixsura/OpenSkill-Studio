from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cron_mgr import fleet_ai_cron_manager
def test_cm():
    r = fleet_ai_cron_manager([{"active": True, "jobs": 200, "runs_24h": 5000, "missed": 0}])
    assert r["jobs"] == 200
    assert r["punctual"]
