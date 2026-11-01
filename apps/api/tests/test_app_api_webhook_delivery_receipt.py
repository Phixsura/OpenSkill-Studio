from app.services.app_api_webhook_delivery_receipt import AppAPIWebhookDeliveryReceipt

class TestReceipt:
    def test_record_success(self):
        r = AppAPIWebhookDeliveryReceipt()
        receipt = r.record("inst-1", "r1", "d1", "https://a.com", 200, 45.0)
        assert receipt.acknowledged is True

    def test_record_failure(self):
        r = AppAPIWebhookDeliveryReceipt()
        receipt = r.record("inst-1", "r1", "d1", "https://a.com", 500, 100.0)
        assert receipt.acknowledged is False

    def test_ack_rate(self):
        r = AppAPIWebhookDeliveryReceipt()
        r.record("inst-1", "r1", "d1", "https://a.com", 200, 50)
        r.record("inst-1", "r2", "d2", "https://a.com", 500, 50)
        assert r.acknowledged_rate("inst-1") == 50.0

    def test_isolation(self):
        r = AppAPIWebhookDeliveryReceipt()
        r.record("inst-1", "r1", "d1", "https://a.com", 200, 50)
        assert r.count("inst-2") == 0
