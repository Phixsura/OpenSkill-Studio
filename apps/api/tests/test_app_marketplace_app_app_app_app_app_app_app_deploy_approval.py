from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_approval import DeploymentApproval

def test_approval_flow():
    da = DeploymentApproval(required_approvers=2)
    da.create("d1", "2.0.0", "prod")
    r1 = da.approve("d1", "alice")
    assert r1["status"] == "pending"
    assert r1["needed"] == 1
    r2 = da.approve("d1", "bob")
    assert r2["status"] == "approved"

def test_reject():
    da = DeploymentApproval()
    da.create("d2", "3.0.0", "prod")
    r = da.reject("d2", "charlie", "failing tests")
    assert r["status"] == "rejected"
    assert da.get("d2")["status"] == "rejected"
