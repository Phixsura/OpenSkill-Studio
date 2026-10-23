from app.services.app_marketplace_app_app_app_app_app_app_app_audit_trail import AuditTrail

def test_audit():
    at = AuditTrail()
    at.log(actor="alice", action="create", resource="app/myapp", details="Created app")
    at.log(actor="bob", action="delete", resource="user/u1", ip="1.2.3.4")
    at.log(actor="alice", action="update", resource="settings/security")
    q = at.query(actor="alice")
    assert len(q) == 2
    q2 = at.query(action="delete")
    assert len(q2) == 1
    s = at.stats()
    assert s["total_events"] == 3
    assert s["unique_actors"] == 2
    assert s["by_action"]["create"] == 1
