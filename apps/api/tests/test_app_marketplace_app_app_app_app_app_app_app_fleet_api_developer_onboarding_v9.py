from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_developer_onboarding_v9 import fleet_api_developer_onboarding_v9
def test_ado2_v9():
    r = fleet_api_developer_onboarding_v9([{"onboarded": True, "first_api_call": True, "onboarding_hours": 2}])
    assert r["onboarded"] == 1
    assert r["healthy"]
