from app.services.app_marketplace_app_app_app_app_app_app_app_payload_transform import apply_mapping, apply_filter, apply_template

def test_mapping():
    payload = {"user": {"name": "Alice", "email": "a@b.com"}, "action": "login"}
    mapping = {"userName": "user.name", "userEmail": "user.email", "event": "action"}
    r = apply_mapping(payload, mapping)
    assert r["userName"] == "Alice"
    assert r["userEmail"] == "a@b.com"
    assert r["event"] == "login"

def test_filter():
    payload = {"id": 1, "name": "Alice", "secret": "xyz", "email": "a@b.com"}
    r = apply_filter(payload, exclude=["secret"])
    assert "secret" not in r
    assert r["name"] == "Alice"
    r2 = apply_filter(payload, include=["id", "name"])
    assert list(r2.keys()) == ["id", "name"]

def test_template():
    payload = {"user": {"name": "Alice"}, "action": "login"}
    t = apply_template("{{user.name}} performed {{action}}", payload)
    assert t == "Alice performed login"
