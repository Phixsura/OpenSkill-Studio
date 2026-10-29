from app.services.app_api_developer_api_api_webhook_delivery_receipt import AppAPIDeveloperAPIApiWebhookDeliveryReceipt

class TestDeliveryReceipt:
    def test_acknowledged(self):
        r = AppAPIDeveloperAPIApiWebhookDeliveryReceipt()
        d = r.create("inst-1", "d1", "https://a.com", 200, 50.0)
        assert d.acknowledged is True
        assert d.acknowledged_at is not None

    def test_unacknowledged(self):
        r = AppAPIDeveloperAPIApiWebhookDeliveryReceipt()
        r.create("inst-1", "d1", "https://a.com", 500, 100.0)
        assert len(r.unacknowledged("inst-1")) == 1

    def test_ack_rate(self):
        r = AppAPIDeveloperAPIApiWebhookDeliveryReceipt()
        r.create("inst-1", "d1", "https://a.com", 200, 50)
        r.create("inst-1", "d2", "https://a.com", 200, 60)
        r.create("inst-1", "d3", "https://a.com", 500, 100)
        assert r.ack_rate("inst-1") == 66.7

    def test_avg_response(self):
        r = AppAPIDeveloperAPIApiWebhookDeliveryReceipt()
        r.create("inst-1", "d1", "https://a.com", 200, 50)
        r.create("inst-1", "d2", "https://a.com", 200, 100)
        assert r.avg_response_time("inst-1") == 75.0

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiWebhookDeliveryReceipt()
        r.create("inst-1", "d1", "https://a.com", 200, 50)
        assert r.ack_rate("inst-2") == 100.0
