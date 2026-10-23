from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_filter import create_filter, apply_filter, filter_stats

def test_filter():
    events = [
        {"type": "app.installed", "source": "marketplace", "payload": {"plan": "pro"}},
        {"type": "app.uninstalled", "source": "marketplace", "payload": {"plan": "free"}},
        {"type": "user.created", "source": "auth", "payload": {}},
    ]
    f = create_filter(event_types=["app.installed", "app.uninstalled"])
    result = apply_filter(events, f)
    assert len(result) == 2
    f2 = create_filter(conditions={"plan": "pro"})
    result2 = apply_filter(events, f2)
    assert len(result2) == 1

def test_stats():
    s = filter_stats(100, 75)
    assert s["dropped"] == 25
    assert s["drop_rate"] == 25.0
