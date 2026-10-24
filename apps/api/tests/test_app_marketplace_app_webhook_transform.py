from app.services.app_marketplace_app_webhook_transform import apply_transform, build_transform_preview, validate_mappings

def test_transform():
    payload = {"user": {"name": "Alice", "email": "a@b.com"}, "action": "login"}
    mappings = [{"source": "user.name", "target": "username"}, {"source": "action", "target": "event_type"}]
    r = apply_transform(payload=payload, mappings=mappings)
    assert r["username"] == "Alice"
    assert r["event_type"] == "login"

def test_preview():
    r = build_transform_preview(payload={"a": 1, "b": 2}, mappings=[{"source": "a", "target": "x"}])
    assert r["fields_mapped"] == 1

def test_validate_ok():
    r = validate_mappings(mappings=[{"source": "a", "target": "b"}])
    assert r["valid"]

def test_validate_bad():
    r = validate_mappings(mappings=[{"source": "", "target": "b"}])
    assert not r["valid"]
