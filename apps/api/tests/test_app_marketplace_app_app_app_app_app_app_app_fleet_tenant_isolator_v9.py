from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tenant_isolator_v9 import fleet_tenant_isolator_v9
def test_ti_v9():
    r = fleet_tenant_isolator_v9([{"isolated": True, "violations": 0, "namespaces": 3}])
    assert r["violations"] == 0
    assert r["healthy"]
