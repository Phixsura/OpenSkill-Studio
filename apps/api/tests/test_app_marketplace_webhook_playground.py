from app.services.app_marketplace_webhook_playground import create_test_endpoint, send_test_webhook, inspect_received_webhooks

def test_create():
    e = create_test_endpoint()
    assert "webhook.openskill.dev" in e["url"]
    assert e["status"] == "active"

def test_send():
    r = send_test_webhook(url="https://x.com", event_type="test", payload={"key": "val"})
    assert r["success"]
    assert r["status_code"] == 200

def test_inspect():
    webhooks = [{"event_type": "install", "response_ms": 100}, {"event_type": "install", "response_ms": 200}]
    r = inspect_received_webhooks(webhooks=webhooks)
    assert r["total"] == 2
    assert r["by_event"]["install"] == 2
    assert r["avg_response_ms"] == 150
