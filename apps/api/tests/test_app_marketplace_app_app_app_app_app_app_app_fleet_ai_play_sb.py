from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_play_sb import fleet_ai_playground_sandbox
def test_ps():
    r = fleet_ai_playground_sandbox([{"active": True, "sessions_24h": 50000, "duration_min": 20, "models": 30}])
    assert r["sessions_24h"] == 50000
    assert r["engaging"]
