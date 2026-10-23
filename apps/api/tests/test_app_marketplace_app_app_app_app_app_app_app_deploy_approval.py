from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_approval import (
    create_approval_request, approve, reject,
)

def test_approval_flow():
    req = create_approval_request("d1", "alice", "production", ["bob", "carol"])
    r = approve(req, "alice")
    assert not r["approved"]  # self-approve blocked
    r2 = approve(req, "bob")
    assert r2["approved"]
    assert not r2["all_approved"]
    r3 = approve(req, "carol")
    assert r3["all_approved"]
    assert req["status"] == "approved"

def test_reject():
    req = create_approval_request("d2", "alice", "staging", ["bob"])
    r = reject(req, "bob", "not ready")
    assert r["rejected"]
    assert req["status"] == "rejected"
