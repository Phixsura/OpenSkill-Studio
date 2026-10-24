from app.services.app_marketplace_app_webhook_filter import create_filter, evaluate_filter

def test_create():
    f = create_filter(name="only_errors", conditions=[{"field": "level", "operator": "eq", "value": "error"}])
    assert f["status"] == "active"

def test_empty():
    f = create_filter(name="x", conditions=[])
    assert f["error"]

def test_eq():
    assert evaluate_filter(payload={"level": "error"}, conditions=[{"field": "level", "operator": "eq", "value": "error"}])
    assert not evaluate_filter(payload={"level": "info"}, conditions=[{"field": "level", "operator": "eq", "value": "error"}])

def test_nested():
    assert evaluate_filter(payload={"user": {"role": "admin"}}, conditions=[{"field": "user.role", "operator": "eq", "value": "admin"}])

def test_contains():
    assert evaluate_filter(payload={"message": "Connection failed"}, conditions=[{"field": "message", "operator": "contains", "value": "failed"}])

def test_any_mode():
    conditions = [{"field": "a", "operator": "eq", "value": 1}, {"field": "b", "operator": "eq", "value": 2}]
    assert evaluate_filter(payload={"a": 1, "b": 99}, conditions=conditions, mode="any")
    assert not evaluate_filter(payload={"a": 99, "b": 99}, conditions=conditions, mode="any")
