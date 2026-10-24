from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_session_mgr import fleet_ai_session_manager
def test_sm():
    r = fleet_ai_session_manager([{"active": True, "sessions": 100000, "avg_duration_min": 25, "persistence_pct": 99}])
    assert r["sessions"] == 100000
    assert r["persistent"]
