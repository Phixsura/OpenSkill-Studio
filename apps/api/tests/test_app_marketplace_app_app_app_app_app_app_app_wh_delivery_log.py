from app.services.app_marketplace_app_app_app_app_app_app_app_wh_delivery_log import WebhookDeliveryLog

def test_log():
    wdl = WebhookDeliveryLog()
    wdl.record("w1", "https://a.com", 200, 150, 1)
    wdl.record("w1", "https://a.com", 500, 200, 2)
    wdl.record("w2", "https://b.com", 200, 100, 1)
    assert len(wdl.by_webhook("w1")) == 2
    fr = wdl.failure_rate()
    assert fr["rate"] == 33.3
    assert fr["failures"] == 1

def test_slow():
    wdl = WebhookDeliveryLog()
    wdl.record("w1", "url", 200, 100, 1)
    wdl.record("w2", "url", 200, 6000, 1)
    assert len(wdl.slow_deliveries(5000)) == 1
