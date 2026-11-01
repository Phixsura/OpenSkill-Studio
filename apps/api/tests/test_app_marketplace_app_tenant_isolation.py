from app.services.app_marketplace_app_tenant_isolation import get_isolation_config, verify_tenant_access

def test_shared():
    r = get_isolation_config(org_id="org1", level="shared")
    assert r["cost_multiplier"] == 1.0
    assert not r["encryption"]

def test_isolated():
    r = get_isolation_config(org_id="org1", level="isolated")
    assert r["cost_multiplier"] == 5.0
    assert r["cross_tenant_blocked"]
    assert "compliance_cert" in r["features"]

def test_same_org():
    r = verify_tenant_access(requesting_org="org1", target_org="org1", resource_type="data")
    assert r["allowed"]

def test_cross_denied():
    r = verify_tenant_access(requesting_org="org1", target_org="org2", resource_type="data")
    assert not r["allowed"]

def test_shared_resource():
    r = verify_tenant_access(requesting_org="org1", target_org="org2", resource_type="public_apps")
    assert r["allowed"]
