from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ab_test_v9 import fleet_ab_test_v9
def test_ab_v9():
    r = fleet_ab_test_v9([{"status": "completed", "significant": True, "lift_pct": 5.2}])
    assert r["significant"] == 1
    assert r["avg_lift_pct"] == 5.2
    assert r["healthy"]
