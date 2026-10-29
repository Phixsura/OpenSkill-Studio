from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_webhook_delivery_confirmation import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation

class TestDeliveryConfirmation:
    def test_create_and_confirm(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation()
        c.create("inst-1", "d1", "https://a.com")
        r = c.confirm("inst-1", "d1", 50.0)
        assert r.confirmed is True

    def test_unconfirmed(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation()
        c.create("inst-1", "d1", "https://a.com")
        c.create("inst-1", "d2", "https://b.com")
        c.confirm("inst-1", "d1", 50.0)
        assert len(c.unconfirmed("inst-1")) == 1

    def test_confirmation_rate(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation()
        c.create("inst-1", "d1", "https://a.com")
        c.create("inst-1", "d2", "https://b.com")
        c.confirm("inst-1", "d1", 50.0)
        assert c.confirmation_rate("inst-1") == 50.0

    def test_avg_latency(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation()
        c.create("inst-1", "d1", "https://a.com")
        c.create("inst-1", "d2", "https://b.com")
        c.confirm("inst-1", "d1", 50.0)
        c.confirm("inst-1", "d2", 100.0)
        assert c.avg_latency("inst-1") == 75.0

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation()
        c.create("inst-1", "d1", "https://a.com")
        assert c.confirmation_rate("inst-2") == 100.0
