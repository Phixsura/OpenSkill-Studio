from app.services.app_marketplace_app_tenant_isolation import validate_tenant_access, build_tenant_context, check_data_boundary

def test_same_org():
    r = validate_tenant_access(org_id="org1", resource_org_id="org1")
    assert r["allowed"]

def test_cross_tenant():
    r = validate_tenant_access(org_id="org1", resource_org_id="org2")
    assert not r["allowed"]

def test_context():
    c = build_tenant_context(org_id="org1", user_id="u1", app_id="a1", installation_id="i1")
    assert c["namespace"] == "org_org1_app_a1"
    assert c["data_prefix"] == "data/org1/a1/"

def test_boundary_ok():
    r = check_data_boundary(requested_path="data/org1/a1/file.json", allowed_prefix="data/org1/a1/")
    assert r["allowed"]

def test_boundary_violation():
    r = check_data_boundary(requested_path="data/org2/a1/file.json", allowed_prefix="data/org1/a1/")
    assert not r["allowed"]

def test_path_traversal():
    r = check_data_boundary(requested_path="data/org1/a1/../../../etc/passwd", allowed_prefix="data/org1/a1/")
    assert not r["allowed"]
