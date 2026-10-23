from app.services.app_marketplace_app_app_webhook_filter import create_filter, apply_filter

def test_create():
    r = create_filter(name="High value only", conditions=[
        {"field": "data.amount", "operator": "gt", "value": 100}])
    assert r["condition_count"] == 1
    assert r["active"]

def test_create_empty():
    r = create_filter(name="X", conditions=[])
    assert "error" in r

def test_apply_pass():
    event = {"type": "payment", "data": {"amount": 200}}
    conditions = [{"field": "data.amount", "operator": "gt", "value": 100}]
    r = apply_filter(event=event, conditions=conditions)
    assert r["deliver"]

def test_apply_block():
    event = {"type": "payment", "data": {"amount": 50}}
    conditions = [{"field": "data.amount", "operator": "gt", "value": 100}]
    r = apply_filter(event=event, conditions=conditions)
    assert not r["deliver"]

def test_apply_contains():
    event = {"type": "app.installed", "user": {"email": "alice@example.com"}}
    conditions = [{"field": "user.email", "operator": "contains", "value": "example.com"}]
    r = apply_filter(event=event, conditions=conditions)
    assert r["deliver"]
