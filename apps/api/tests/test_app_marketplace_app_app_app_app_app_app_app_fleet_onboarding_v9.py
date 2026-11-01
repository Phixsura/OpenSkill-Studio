from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_onboarding_v9 import fleet_onboarding_v9
def test_onb_v9():
    r = fleet_onboarding_v9([{"onboarded": True, "days_to_productive": 5}])
    assert r["completed"] == 1
    assert r["avg_days_to_productive"] == 5.0
    assert r["healthy"]
