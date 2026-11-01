from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ab_test import fleet_ai_ab_test
def test_ab():
    r = fleet_ai_ab_test([{"status": "concluded", "impressions": 1000000, "winner": True}])
    assert r["concluded"] == 1
    assert r["winners"] == 1
