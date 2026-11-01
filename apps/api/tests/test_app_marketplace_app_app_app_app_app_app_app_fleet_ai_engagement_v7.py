from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_engagement_v7 import fleet_ai_engagement_v7
def test_ev7():
    r = fleet_ai_engagement_v7([{"active": True, "dau_mau": 45, "sessions": 5, "time_min": 25}])
    assert r["dau_mau"] == 45.0
    assert r["engaged"]
