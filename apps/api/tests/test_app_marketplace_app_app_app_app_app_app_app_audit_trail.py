from app.services.app_marketplace_app_app_app_app_app_app_app_audit_trail import AuditTrail

def test_log_verify():
    at = AuditTrail()
    at.log("admin", "create", "user:1")
    at.log("admin", "update", "user:1", {"field": "name"})
    at.log("system", "delete", "user:2")
    r = at.verify_chain()
    assert r["valid"]
    assert r["entries"] == 3

def test_query():
    at = AuditTrail()
    at.log("admin", "create", "user:1")
    at.log("system", "delete", "user:2")
    at.log("admin", "update", "user:1")
    r = at.query(actor="admin")
    assert len(r) == 2
    r2 = at.query(action="delete")
    assert len(r2) == 1
