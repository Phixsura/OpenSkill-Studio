from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tenant_iso import fleet_tenant_isolation
def test_iso():
    r = fleet_tenant_isolation([{"namespace_isolated": True}, {"namespace_isolated": False}])
    assert r["isolated"] == 1
    assert r["shared"] == 1
    assert not r["fully_isolated"]
