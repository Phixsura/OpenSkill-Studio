from app.services.app_marketplace_app_app_app_app_app_app_app_payload_inspector import inspect_payload

def test_inspect():
    r = inspect_payload({"event": "app.installed", "data": {"app_id": "test", "user": {"id": "u1", "name": "Alice"}}})
    assert r["field_count"] == 6
    assert r["depth"] >= 3
    assert r["size_bytes"] > 0
    assert "event" in r["fields"]
    assert len(r["warnings"]) == 0

def test_simple():
    r = inspect_payload({"key": "value"})
    assert r["field_count"] == 1
    assert r["depth"] == 1
