from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pool_eff import fleet_pool_efficiency
def test_efficiency():
    r = fleet_pool_efficiency([{"active": 20, "idle": 80}, {"active": 30, "idle": 70}])
    assert r["active"] == 50
    assert r["efficiency_pct"] == 25.0
    assert r["wasteful"]
