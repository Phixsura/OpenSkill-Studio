from app.services.app_marketplace_app_app_app_app_app_app_app_gw_auth import GatewayAuth

def test_auth():
    ga = GatewayAuth()
    ga.register_key("my-secret-key", "alice", ["read", "write"])
    r = ga.authenticate("my-secret-key", "read")
    assert r["authenticated"]
    assert r["owner"] == "alice"

def test_denied():
    ga = GatewayAuth()
    r = ga.authenticate("bad-key")
    assert not r["authenticated"]
    assert ga.stats()["denied"] == 1

def test_scope():
    ga = GatewayAuth()
    ga.register_key("key", "bob", ["read"])
    r = ga.authenticate("key", "admin")
    assert not r["authenticated"]
    assert r["reason"] == "insufficient_scope"
