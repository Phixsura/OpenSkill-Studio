from app.services.app_api_developer_api_api_developer_api_api_webhook_delivery_window import AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow

class TestDeliveryWindow:
    def test_within_window(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17)
        assert w.can_deliver("inst-1", "w1", 12, 0) is True

    def test_outside_window(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17)
        assert w.can_deliver("inst-1", "w1", 20, 0) is False

    def test_overnight_window(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 22, 6)
        assert w.can_deliver("inst-1", "w1", 23, 0) is True
        assert w.can_deliver("inst-1", "w1", 3, 0) is True
        assert w.can_deliver("inst-1", "w1", 12, 0) is False

    def test_day_restriction(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17, days=[0, 1, 2, 3, 4])  # weekdays
        assert w.can_deliver("inst-1", "w1", 12, 5) is False  # Saturday
        assert w.can_deliver("inst-1", "w1", 12, 2) is True   # Wednesday

    def test_no_window_allows(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        assert w.can_deliver("inst-1", "nonexistent", 12, 0) is True

    def test_isolation(self):
        w = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17)
        assert len(w.all_windows("inst-2")) == 0
