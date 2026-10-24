from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ab import fleet_ai_ab_testing
def test_ab():
    r = fleet_ai_ab_testing([{"active": True, "users": 100000, "winner_determined": True}])
    assert r["users_enrolled"] == 100000
    assert r["data_driven"]
