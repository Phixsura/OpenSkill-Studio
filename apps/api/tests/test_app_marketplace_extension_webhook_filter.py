from app.services.app_marketplace_extension_webhook_filter import WebhookFilterService


def test_eq_filter():
    wfs = WebhookFilterService()
    wfs.create_filter("f1", "wh-1", [{"field": "event_type", "operator": "eq", "value": "install"}])
    assert wfs.evaluate("f1", {"event_type": "install"}) is True
    assert wfs.evaluate("f1", {"event_type": "uninstall"}) is False


def test_contains_filter():
    wfs = WebhookFilterService()
    wfs.create_filter("f2", "wh-2", [{"field": "message", "operator": "contains", "value": "error"}])
    assert wfs.evaluate("f2", {"message": "Critical error occurred"}) is True
    assert wfs.evaluate("f2", {"message": "All good"}) is False


def test_nested_field():
    wfs = WebhookFilterService()
    wfs.create_filter("f3", "wh-3", [{"field": "data.status", "operator": "eq", "value": "active"}])
    assert wfs.evaluate("f3", {"data": {"status": "active"}}) is True
    assert wfs.evaluate("f3", {"data": {"status": "inactive"}}) is False


def test_all_mode():
    wfs = WebhookFilterService()
    wfs.create_filter("f4", "wh-4", [
        {"field": "type", "operator": "eq", "value": "install"},
        {"field": "org", "operator": "startswith", "value": "enterprise"},
    ], match_mode="all")
    assert wfs.evaluate("f4", {"type": "install", "org": "enterprise-abc"}) is True
    assert wfs.evaluate("f4", {"type": "install", "org": "free-xyz"}) is False


def test_any_mode():
    wfs = WebhookFilterService()
    wfs.create_filter("f5", "wh-5", [
        {"field": "type", "operator": "eq", "value": "install"},
        {"field": "type", "operator": "eq", "value": "update"},
    ], match_mode="any")
    assert wfs.evaluate("f5", {"type": "install"}) is True
    assert wfs.evaluate("f5", {"type": "update"}) is True
    assert wfs.evaluate("f5", {"type": "delete"}) is False


def test_in_operator():
    wfs = WebhookFilterService()
    wfs.create_filter("f6", "wh-6", [{"field": "status", "operator": "in", "value": "active,pending"}])
    assert wfs.evaluate("f6", {"status": "active"}) is True
    assert wfs.evaluate("f6", {"status": "expired"}) is False


def test_filter_batch():
    wfs = WebhookFilterService()
    wfs.create_filter("f7", "wh-7", [{"field": "level", "operator": "eq", "value": "error"}])
    events = [{"level": "info"}, {"level": "error"}, {"level": "warn"}, {"level": "error"}]
    filtered = wfs.filter_events("f7", events)
    assert len(filtered) == 2
