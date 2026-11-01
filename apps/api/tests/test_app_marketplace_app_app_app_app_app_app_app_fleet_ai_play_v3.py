from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_play_v3 import fleet_ai_playground_v3
def test_pv3():
    r = fleet_ai_playground_v3([{"active": True, "sessions_24h": 100000, "collaborators": 500, "notebooks": 2000}])
    assert r["collaborators"] == 500
    assert r["collaborative"]
