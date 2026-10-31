from app.services.app_marketplace_app_app_app_app_app_app_app_payload_xform import (
    transform_payload, flatten_payload, redact_fields,
)

def test_transform():
    payload = {"user": {"name": "Alice", "email": "alice@test.com"}, "action": "login"}
    r = transform_payload(payload, {"username": "user.name", "event": "action"})
    assert r["transformed"]["username"] == "Alice"
    assert r["transformed"]["event"] == "login"
    assert r["null_fields"] == 0

def test_flatten():
    r = flatten_payload({"a": {"b": {"c": 1}}, "d": 2})
    assert r["a.b.c"] == 1
    assert r["d"] == 2

def test_redact():
    r = redact_fields({"name": "Alice", "password": "secret", "nested": {"token": "abc"}},
                       ["password", "token"])
    assert r["payload"]["password"] == "[REDACTED]"
    assert r["payload"]["nested"]["token"] == "[REDACTED]"
    assert r["redacted"] == 2
