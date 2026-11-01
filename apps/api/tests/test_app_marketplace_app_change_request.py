from app.services.app_marketplace_app_change_request import create_change_request, approve_change

def test_create():
    r = create_change_request(title="Deploy v3", description="Major version", risk="high",
        requester="alice", approvers=["bob", "carol"])
    assert r["cr_id"].startswith("CR-")
    assert r["min_approvals"] == 2

def test_create_low():
    r = create_change_request(title="Typo fix", description="Fix typo", risk="low",
        requester="alice", approvers=["bob"])
    assert r["min_approvals"] == 1

def test_approve():
    cr = {"cr_id": "CR-1", "approvers": ["bob"], "current_approvals": 0, "min_approvals": 1}
    r = approve_change(cr=cr, approver="bob")
    assert r["fully_approved"]
    assert r["status"] == "approved"

def test_unauthorized():
    cr = {"cr_id": "CR-1", "approvers": ["bob"], "current_approvals": 0, "min_approvals": 1}
    r = approve_change(cr=cr, approver="eve")
    assert "error" in r
