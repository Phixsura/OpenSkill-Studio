from app.services.app_marketplace_app_audit_trail import create_audit_entry, verify_chain

def test_create():
    r = create_audit_entry(actor="admin", action="delete_app", resource="app_123")
    assert r["entry_id"].startswith("audit_")
    assert r["immutable"]
    assert len(r["hash"]) == 64

def test_chain():
    e1 = create_audit_entry(actor="a", action="create", resource="r1")
    e2 = create_audit_entry(actor="b", action="update", resource="r1", previous_hash=e1["hash"])
    r = verify_chain(entries=[e1, e2])
    assert r["valid"]
    assert r["entries_checked"] == 2

def test_broken_chain():
    e1 = create_audit_entry(actor="a", action="x", resource="r")
    e2 = create_audit_entry(actor="b", action="y", resource="r", previous_hash="fake_hash")
    r = verify_chain(entries=[e1, e2])
    assert not r["valid"]
    assert "tampering" in r["error"]
