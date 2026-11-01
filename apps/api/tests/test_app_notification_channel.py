"""Tests for App Notification Channel — add, test, deliver, toggle."""

import pytest

from app.services.app_notification_channel import AppNotificationChannel


class TestAdd:
    def test_add(self):
        n = AppNotificationChannel()
        ch = n.add_channel("inst-1", "ch1", "slack", "Dev Alerts", {"webhook_url": "https://hooks.slack.com/..."})
        assert ch.channel_type == "slack"
        assert ch.enabled is True

    def test_invalid_type(self):
        n = AppNotificationChannel()
        with pytest.raises(ValueError):
            n.add_channel("inst-1", "ch1", "carrier_pigeon", "Bad")


class TestDelivery:
    def test_record(self):
        n = AppNotificationChannel()
        n.add_channel("inst-1", "ch1", "email", "Email")
        n.record_delivery("inst-1", "ch1", True)
        n.record_delivery("inst-1", "ch1", True)
        n.record_delivery("inst-1", "ch1", False)
        ch = n.list_channels("inst-1")[0]
        assert ch.success_rate == 66.7

    def test_test_channel(self):
        n = AppNotificationChannel()
        n.add_channel("inst-1", "ch1", "webhook", "WH")
        ch = n.test_channel("inst-1", "ch1", True)
        assert ch.test_success is True


class TestToggle:
    def test_disable(self):
        n = AppNotificationChannel()
        n.add_channel("inst-1", "ch1", "sms", "SMS")
        n.toggle("inst-1", "ch1", False)
        assert n.enabled_channels("inst-1") == []

    def test_filter_type(self):
        n = AppNotificationChannel()
        n.add_channel("inst-1", "ch1", "email", "Email")
        n.add_channel("inst-1", "ch2", "slack", "Slack")
        assert len(n.enabled_channels("inst-1", "email")) == 1


class TestIsolation:
    def test_cross(self):
        n = AppNotificationChannel()
        n.add_channel("inst-1", "ch1", "email", "Email")
        assert n.list_channels("inst-2") == []
