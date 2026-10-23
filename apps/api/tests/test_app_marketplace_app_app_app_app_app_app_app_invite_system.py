from app.services.app_marketplace_app_app_app_app_app_app_app_invite_system import InviteSystem

def test_invite():
    sys = InviteSystem()
    inv = sys.send(email="bob@test.com", org_id="org1", role="editor", invited_by="alice")
    assert inv["status"] == "pending"
    pending = sys.pending_for_org("org1")
    assert len(pending) == 1
    r = sys.accept(inv["code"])
    assert r["accepted"]
    assert r["role"] == "editor"
    assert len(sys.pending_for_org("org1")) == 0

def test_decline():
    sys = InviteSystem()
    inv = sys.send(email="x@y.com", org_id="org2")
    sys.decline(inv["code"])
    assert len(sys.pending_for_org("org2")) == 0
