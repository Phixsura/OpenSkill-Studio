from app.services.app_marketplace_extension_webhook_filter import ExtWebhookFilterService

def test_event_type_filter():
    svc = ExtWebhookFilterService()
    f = svc.create(event_types=["install", "uninstall"])
    assert svc.matches(f.filter_id, "install", {}) is True
    assert svc.matches(f.filter_id, "review", {}) is False

def test_condition():
    svc = ExtWebhookFilterService()
    f = svc.create(conditions=[{"field": "rating", "op": "gt", "value": 3}])
    assert svc.matches(f.filter_id, "review", {"rating": 5}) is True
    assert svc.matches(f.filter_id, "review", {"rating": 2}) is False

def test_contains():
    svc = ExtWebhookFilterService()
    f = svc.create(conditions=[{"field": "message", "op": "contains", "value": "error"}])
    assert svc.matches(f.filter_id, "log", {"message": "Got an error"}) is True
    assert svc.matches(f.filter_id, "log", {"message": "All good"}) is False
