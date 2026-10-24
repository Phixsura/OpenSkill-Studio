from app.services.app_marketplace_app_change_approval import create_approval_request, approve, reject

def test_create():
    r = create_approval_request(app_id="a1", type="publish", requester_id="u1",
                                  description="Publish v2.0", changes={"version": "2.0"})
    assert r["status"] == "pending"

def test_invalid_type():
    r = create_approval_request(app_id="a1", type="magic", requester_id="u1", description="X", changes={})
    assert r["error"]

def test_approve():
    req = {"requester_id": "u1", "approvers": [], "status": "pending"}
    r = approve(request=req, approver_id="u2")
    assert r["status"] == "approved"

def test_self_approve_blocked():
    req = {"requester_id": "u1", "approvers": []}
    r = approve(request=req, approver_id="u1")
    assert r["error"]

def test_reject():
    req = {"status": "pending"}
    r = reject(request=req, rejector_id="u2", reason="Not ready")
    assert r["status"] == "rejected"
    assert r["rejection_reason"] == "Not ready"
