from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_isolate import validate_isolation, check_namespace

def test_isolated():
    r = validate_isolation([
        {"tenant_id": "t1", "resource_id": "r1"},
        {"tenant_id": "t2", "resource_id": "r2"},
    ])
    assert r["valid"]
    assert r["tenants_checked"] == 2

def test_violation():
    r = validate_isolation([
        {"tenant_id": "t1", "resource_id": "shared-r"},
        {"tenant_id": "t2", "resource_id": "shared-r"},
    ])
    assert not r["valid"]
    assert r["violations"][0]["severity"] == "critical"

def test_namespace():
    assert check_namespace("abc", "t-abc-prod")["valid"]
    assert not check_namespace("abc", "t-xyz-prod")["valid"]
