from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_opt import fleet_cloud_optimization
def test_opt():
    r = fleet_cloud_optimization([{"monthly_savings_usd": 3000, "implemented": True}, {"monthly_savings_usd": 2000, "implemented": False}])
    assert r["total_monthly_savings"] == 5000
    assert r["realized_savings"] == 3000
    assert r["pending"] == 1
