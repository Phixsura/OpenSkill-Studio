from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_delivery import WebhookDeliveryTracker

def test_delivery():
    t = WebhookDeliveryTracker(max_retries=3)
    r1 = t.record("w1", "https://example.com", 200, 1)
    assert r1["success"]
    assert not r1["should_retry"]
    r2 = t.record("w2", "https://fail.com", 500, 1)
    assert not r2["success"]
    assert r2["should_retry"]
    s = t.stats()
    assert s["success_rate"] == 50.0
    assert s["failures"] == 1

def test_max_retries():
    t = WebhookDeliveryTracker(max_retries=2)
    r = t.record("w1", "https://fail.com", 500, 2)
    assert not r["should_retry"]
    failed = t.failed_webhooks()
    assert len(failed) == 1
