from app.services.app_marketplace_app_app_app_app_app_app_app_svc_owner import ServiceOwnerRegistry

def test_register_lookup():
    reg = ServiceOwnerRegistry()
    reg.register("auth", "platform", "alice", ["alice", "bob"])
    reg.register("billing", "platform", "carol")
    r = reg.get_oncall("auth")
    assert r["found"]
    assert r["oncall"] == "alice"
    assert r["escalation"] == ["alice", "bob"]

def test_by_team():
    reg = ServiceOwnerRegistry()
    reg.register("a", "t1", "x")
    reg.register("b", "t1", "y")
    reg.register("c", "t2", "z")
    assert len(reg.by_team("t1")) == 2
    assert reg.stats()["teams"] == 2
