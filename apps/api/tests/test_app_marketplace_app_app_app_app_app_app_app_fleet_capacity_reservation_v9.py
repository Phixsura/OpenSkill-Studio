from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_capacity_reservation_v9 import fleet_capacity_reservation_v9
def test_cr4_v9():
    r = fleet_capacity_reservation_v9([{"active": True, "utilized_pct": 85, "monthly_savings": 10000}])
    assert r["avg_utilized_pct"] == 85.0
    assert r["healthy"]
