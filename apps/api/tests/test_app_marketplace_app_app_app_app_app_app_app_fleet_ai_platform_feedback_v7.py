from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_feedback_v7 import fleet_ai_feedback_v7
def test_fv7():
    r = fleet_ai_feedback_v7([{"active": True, "feedback": 100000, "positive": 90000, "actioned": 5000}])
    assert r["feedback"] == 100000
    assert r["responsive"]
