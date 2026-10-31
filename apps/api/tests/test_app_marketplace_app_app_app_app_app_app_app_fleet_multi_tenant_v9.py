from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_multi_tenant_v9 import fleet_multi_tenant_v9
def test_mt2_v9():
    r = fleet_multi_tenant_v9([{"active": True, "resource_pct": 10}, {"active": True, "resource_pct": 15}])
    assert r["noisy_neighbors"] == 0
    assert r["healthy"]
