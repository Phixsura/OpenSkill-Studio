from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_onboard_v7 import fleet_ai_onboarding_v7
def test_ov7():
    r = fleet_ai_onboarding_v7([{"active": True, "completions_30d": 50000, "ttfv_min": 5, "drop_pct": 10}])
    assert r["completions"] == 50000
    assert r["smooth"]
