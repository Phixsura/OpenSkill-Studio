from app.services.app_marketplace_app_app_app_app_app_app_app_audit_trail import (
    append_event, get_trail, verify_chain, reset_trail,
)

def test_trail():
    reset_trail()
    e1 = append_event("alice", "create", "app/123")
    e2 = append_event("bob", "update", "app/123", "changed name")
    assert e1["seq"] == 1
    assert e2["seq"] == 2
    assert e2["prev_hash"] == e1["hash"]
    r = get_trail()
    assert r["total"] == 2
    v = verify_chain()
    assert v["valid"]
    reset_trail()

def test_escape():
    reset_trail()
    e = append_event("<script>", "delete", "x&y")
    assert "<script>" not in e["actor"]
    assert "&amp;" in e["resource"]
    reset_trail()
