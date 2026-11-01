from app.services.app_marketplace_app_app_app_app_app_app_app_key_permissions import check_key_access, list_endpoint_scopes

def test_access():
    r = check_key_access(key_scopes=["read:apps", "write:apps"], method="GET", path="/api/v1/apps")
    assert r["allowed"]
    r2 = check_key_access(key_scopes=["read:apps"], method="POST", path="/api/v1/apps")
    assert not r2["allowed"]
    assert "write:apps" in r2["missing"]

def test_no_restriction():
    r = check_key_access(key_scopes=[], method="GET", path="/api/v1/health")
    assert r["allowed"]

def test_list():
    assert len(list_endpoint_scopes()) == 7
