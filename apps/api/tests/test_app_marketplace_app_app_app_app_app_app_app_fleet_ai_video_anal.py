from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_video_anal import fleet_ai_video_analysis
def test_va():
    r = fleet_ai_video_analysis([{"active": True, "hours_24h": 10000, "fps": 60, "events": 5000000}])
    assert r["hours_24h"] == 10000
    assert r["realtime"]
