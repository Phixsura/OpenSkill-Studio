from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_preview_env_v9 import fleet_preview_env_v9
def test_pe_v9():
    r = fleet_preview_env_v9([{"status": "running", "age_hours": 12}, {"status": "running", "age_hours": 6}])
    assert r["running"] == 2
    assert r["healthy"]
