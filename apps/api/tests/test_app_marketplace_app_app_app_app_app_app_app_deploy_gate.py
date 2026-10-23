from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_gate import DeploymentGate

def test_approval_flow():
    gate = DeploymentGate(required_approvals=2)
    gate.create_gate("d1", version="2.0", env="production", requester="alice")
    r1 = gate.approve("d1", approver="bob", comment="LGTM")
    assert r1["status"] == "pending"
    r2 = gate.approve("d1", approver="carol")
    assert r2["status"] == "approved"
    assert gate.can_deploy("d1")["allowed"]

def test_self_approve():
    gate = DeploymentGate()
    gate.create_gate("d2", version="1.0", env="prod", requester="alice")
    r = gate.approve("d2", approver="alice")
    assert "error" in r

def test_rejection():
    gate = DeploymentGate()
    gate.create_gate("d3", version="1.0", env="prod", requester="alice")
    gate.reject("d3", reviewer="bob", reason="Tests failing")
    assert not gate.can_deploy("d3")["allowed"]
