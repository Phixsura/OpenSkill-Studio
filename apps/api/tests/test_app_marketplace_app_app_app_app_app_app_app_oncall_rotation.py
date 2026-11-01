from app.services.app_marketplace_app_app_app_app_app_app_app_oncall_rotation import OnCallRotation

def test_rotation():
    oc = OnCallRotation()
    oc.create("platform", ["alice", "bob", "carol"], rotation_days=7)
    r = oc.current_oncall("platform", day_number=0)
    assert r["primary"] == "alice"
    assert r["secondary"] == "bob"
    r2 = oc.current_oncall("platform", day_number=7)
    assert r2["primary"] == "bob"

def test_escalation():
    oc = OnCallRotation()
    oc.create("infra", ["x", "y", "z"], rotation_days=7)
    chain = oc.escalation_chain("infra", day_number=14)
    assert chain[0] == "z"
    assert len(chain) == 3
