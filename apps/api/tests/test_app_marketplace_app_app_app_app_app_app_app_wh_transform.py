from app.services.app_marketplace_app_app_app_app_app_app_app_wh_transform import transform_payload, sanitize_payload

def test_transform():
    r = transform_payload(
        {"user": {"id": "u1", "name": "Alice"}, "event": "signup"},
        {"userId": "user.id", "userName": "user.name", "action": "event"})
    assert r["transformed"]["userId"] == "u1"
    assert r["transformed"]["action"] == "signup"
    assert r["fields_mapped"] == 3

def test_missing():
    r = transform_payload({"a": 1}, {"x": "b.c"})
    assert r["fields_missing"] == 1

def test_sanitize():
    r = sanitize_payload({"name": "<script>alert(1)</script>", "count": 5})
    assert "&lt;script&gt;" in r["data"]["name"]
    assert r["data"]["count"] == 5
