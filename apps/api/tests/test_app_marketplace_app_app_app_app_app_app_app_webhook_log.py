from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_log import WebhookDeliveryLog

def test_log():
    log = WebhookDeliveryLog()
    log.log_delivery(webhook_id="wh1", url="https://example.com/hook",
                      event_type="app.installed", status_code=200, duration_ms=150, success=True)
    log.log_delivery(webhook_id="wh1", url="https://example.com/hook",
                      event_type="app.updated", status_code=500, duration_ms=3000, success=False)
    log.log_delivery(webhook_id="wh2", url="https://other.com/hook",
                      event_type="user.created", status_code=200, duration_ms=80, success=True)
    q = log.query(webhook_id="wh1")
    assert len(q) == 2
    failed = log.query(success=False)
    assert len(failed) == 1
    s = log.stats("wh1")
    assert s["total_deliveries"] == 2
    assert s["success_rate"] == 50.0
