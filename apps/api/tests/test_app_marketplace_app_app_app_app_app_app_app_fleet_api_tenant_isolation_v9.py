from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_tenant_isolation_v9 import fleet_api_tenant_isolation_v9
def test_ati_v9():
    r = fleet_api_tenant_isolation_v9([{"isolated": True, "violations": 0, "data_leaks": 0}])
    assert r["isolated"] == 1
    assert r["healthy"]
