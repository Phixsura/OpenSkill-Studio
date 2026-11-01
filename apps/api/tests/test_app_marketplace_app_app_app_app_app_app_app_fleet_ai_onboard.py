from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_onboard import fleet_ai_onboarding
def test_ob():
    r = fleet_ai_onboarding([{"active": True, "completions_24h": 5000, "avg_min": 10, "drop_off_pct": 12}])
    assert r["completions_24h"] == 5000
    assert r["smooth"]
