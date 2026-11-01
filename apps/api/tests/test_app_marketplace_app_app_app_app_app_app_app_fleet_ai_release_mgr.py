from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_release_mgr import fleet_ai_release_manager
def test_rm():
    r = fleet_ai_release_manager([{"active": True, "releases_24h": 20, "rollbacks": 1, "lead_time_min": 15}])
    assert r["releases_24h"] == 20
    assert r["fast"]
