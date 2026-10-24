from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_compute_optimizer_v9 import fleet_compute_optimizer_v9
def test_copt_v9():
    r = fleet_compute_optimizer_v9([{"recommendation": "optimal", "monthly_savings": 0}])
    assert r["optimal"] == 1
    assert r["healthy"]
