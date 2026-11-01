from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_onboarding import fleet_dev_onboarding
def test_onboard():
    r = fleet_dev_onboarding([{"onboarded": True, "onboard_days": 3}, {"onboarded": True, "onboard_days": 7}, {"onboarded": False}])
    assert r["onboarded"] == 2
    assert r["avg_days"] == 5.0
    assert r["fast"]
