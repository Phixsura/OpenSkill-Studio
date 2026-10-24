from app.services.app_marketplace_app_app_app_app_app_app_app_res_lifecycle import create_resource, audit_resources

def test_create():
    r = create_resource("test-vm", "compute", "alice", ttl_days=7)
    assert r["status"] == "active"
    assert r["has_ttl"]

def test_audit():
    now = 1000000.0
    resources = [
        {"name": "a", "type": "compute", "owner": "alice", "has_ttl": True, "expires_at": now - 100},
        {"name": "b", "type": "storage", "owner": "bob", "has_ttl": False, "expires_at": 0},
        {"name": "c", "type": "compute", "owner": "", "has_ttl": False, "expires_at": 0},
    ]
    r = audit_resources(resources, now=now)
    assert r["expired"] == 1
    assert r["orphaned"] == 1
    assert r["needs_cleanup"] == 2
