from app.services.app_marketplace_app_app_app_app_app_app_app_ep_ownership import EndpointOwnershipRegistry

def test_register():
    eor = EndpointOwnershipRegistry()
    eor.register("/api/users", "user-team", "alice", "critical")
    eor.register("/api/orders", "order-team", "bob")
    r = eor.get_owner("/api/users")
    assert r["team"] == "user-team"
    assert r["oncall"] == "alice"
    assert len(eor.by_team("user-team")) == 1

def test_unowned():
    eor = EndpointOwnershipRegistry()
    eor.register("/api/users", "team-a")
    r = eor.unowned(["/api/users", "/api/orders", "/api/health"])
    assert "/api/orders" in r
    assert "/api/users" not in r
    assert eor.stats()["teams"] == 1
