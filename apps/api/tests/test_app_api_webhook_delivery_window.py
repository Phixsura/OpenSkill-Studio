import pytest
from app.services.app_api_webhook_delivery_window import AppAPIWebhookDeliveryWindow

class TestWindow:
    def test_in_window(self):
        w = AppAPIWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17)
        assert w.is_in_window("inst-1", "w1", 12) is True
        assert w.is_in_window("inst-1", "w1", 20) is False

    def test_overnight(self):
        w = AppAPIWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 22, 6)
        assert w.is_in_window("inst-1", "w1", 23) is True
        assert w.is_in_window("inst-1", "w1", 3) is True
        assert w.is_in_window("inst-1", "w1", 12) is False

    def test_invalid_hours(self):
        w = AppAPIWebhookDeliveryWindow()
        with pytest.raises(ValueError):
            w.configure("inst-1", "w1", "https://a.com", 25, 10)

    def test_isolation(self):
        w = AppAPIWebhookDeliveryWindow()
        w.configure("inst-1", "w1", "https://a.com", 9, 17)
        assert w.list_windows("inst-2") == []
