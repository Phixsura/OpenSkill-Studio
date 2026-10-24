from app.services.app_marketplace_app_webhook_transformer import apply_transform, validate_transform_rules

def test_rename():
    r = apply_transform(payload={"user_id": "u1", "name": "Alice"},
        rules=[{"action": "rename", "path": "user_id", "to": "uid"}])
    assert "uid" in r["transformed"]
    assert "user_id" not in r["transformed"]

def test_remove():
    r = apply_transform(payload={"secret": "xyz", "name": "A"},
        rules=[{"action": "remove", "path": "secret"}])
    assert "secret" not in r["transformed"]

def test_mask():
    r = apply_transform(payload={"email": "alice@example.com"},
        rules=[{"action": "mask", "path": "email"}])
    assert "••" in r["transformed"]["email"]

def test_validate():
    r = validate_transform_rules(rules=[{"action": "rename", "path": "a", "to": "b"}])
    assert r["valid"]

def test_validate_invalid():
    r = validate_transform_rules(rules=[{"action": "explode", "path": "x"}])
    assert not r["valid"]
