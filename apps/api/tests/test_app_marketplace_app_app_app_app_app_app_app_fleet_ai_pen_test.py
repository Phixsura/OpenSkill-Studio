from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_pen_test import fleet_ai_pen_testing
def test_pt():
    r = fleet_ai_pen_testing([{"active": True, "tests_24h": 500, "findings": 15, "critical": 0}])
    assert r["findings"] == 15
    assert r["secure"]
