from app.services.app_marketplace_app_webhook_log import create_delivery_log, get_webhook_stats

def test_success():
    r = create_delivery_log(webhook_id="wh1", event="app.installed",
        url="https://example.com/hook", status_code=200, response_time_ms=120)
    assert r["success"]
    assert r["retry_count"] == 0

def test_failure():
    r = create_delivery_log(webhook_id="wh1", event="app.installed",
        url="https://example.com/hook", status_code=500, response_time_ms=5000)
    assert not r["success"]
    assert r["retry_count"] == 1

def test_stats():
    deliveries = [
        {"success": True, "response_time_ms": 100, "event": "app.installed"},
        {"success": True, "response_time_ms": 200, "event": "app.installed"},
        {"success": False, "response_time_ms": 5000, "event": "review.created"},
    ]
    r = get_webhook_stats(deliveries=deliveries)
    assert r["success_rate"] == 66.7
    assert r["failed"] == 1
    assert r["by_event"]["app.installed"] == 2
