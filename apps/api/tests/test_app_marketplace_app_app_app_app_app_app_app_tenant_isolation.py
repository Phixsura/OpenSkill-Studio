from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_isolation import check_isolation, generate_isolation_report

def test_isolated():
    resources = [
        {"tenant_id": "t1", "resource_id": "r1", "accessible_by": ["t1"]},
        {"tenant_id": "t2", "resource_id": "r2", "accessible_by": ["t2"]},
    ]
    r = check_isolation(resources)
    assert r["isolated"]
    assert r["status"] == "secure"
    report = generate_isolation_report(r)
    assert "properly isolated" in report["verdict"]

def test_violation():
    resources = [
        {"tenant_id": "t1", "resource_id": "r1", "accessible_by": ["t1", "t2"]},
    ]
    r = check_isolation(resources)
    assert not r["isolated"]
    assert r["violation_count"] == 1
    assert r["violations"][0]["accessed_by"] == "t2"
