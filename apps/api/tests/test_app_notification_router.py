"""Tests for App Notification Router — channels, routing, delivery."""

import pytest

from app.services.app_notification_router import (
    AppNotificationRouter,
    ChannelType,
    DeliveryStatus,
    NotificationEvent,
)


def _event(event_id="evt-1", event_type="app.installed", installation_id="inst-1"):
    return NotificationEvent(
        event_id=event_id,
        event_type=event_type,
        payload={"app_id": "app-1"},
        installation_id=installation_id,
    )


class TestRegisterChannel:
    def test_register(self):
        r = AppNotificationRouter()
        c = r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://example.com/hook")
        assert c.channel_id == "ch-1"
        assert c.channel_type == ChannelType.WEBHOOK
        assert c.enabled is True

    def test_register_with_event_filter(self):
        r = AppNotificationRouter()
        c = r.register_channel("inst-1", "ch-1", ChannelType.EMAIL, "admin@example.com",
                               event_types=["app.error", "app.down"])
        assert c.event_types == ["app.error", "app.down"]

    def test_missing_target(self):
        r = AppNotificationRouter()
        with pytest.raises(ValueError, match="target"):
            r.register_channel("inst-1", "ch-1", ChannelType.SLACK, "")

    def test_missing_installation_id(self):
        r = AppNotificationRouter()
        with pytest.raises(ValueError, match="installation_id"):
            r.register_channel("", "ch-1", ChannelType.WEBHOOK, "https://x.com")


class TestRouting:
    def test_route_to_all_channels(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.register_channel("inst-1", "ch-2", ChannelType.SLACK, "#alerts")
        records = r.route(_event())
        assert len(records) == 2
        assert all(d.status == DeliveryStatus.DELIVERED for d in records)

    def test_route_filtered_by_event_type(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com",
                           event_types=["app.error"])
        r.register_channel("inst-1", "ch-2", ChannelType.SLACK, "#all")  # all events
        records = r.route(_event(event_type="app.installed"))
        assert len(records) == 1
        assert records[0].channel_id == "ch-2"

    def test_no_matching_channels(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com",
                           event_types=["app.error"])
        records = r.route(_event(event_type="app.installed"))
        assert len(records) == 0

    def test_cross_installation_isolation(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        records = r.route(_event(installation_id="inst-2"))
        assert len(records) == 0


class TestDisableEnable:
    def test_disabled_channel_skipped(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.disable_channel("inst-1", "ch-1")
        records = r.route(_event())
        assert len(records) == 1
        assert records[0].status == DeliveryStatus.SKIPPED

    def test_re_enable_channel(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.disable_channel("inst-1", "ch-1")
        r.enable_channel("inst-1", "ch-1")
        records = r.route(_event())
        assert records[0].status == DeliveryStatus.DELIVERED


class TestRemoveChannel:
    def test_remove(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.remove_channel("inst-1", "ch-1")
        assert len(r.list_channels("inst-1")) == 0

    def test_remove_nonexistent(self):
        r = AppNotificationRouter()
        with pytest.raises(KeyError):
            r.remove_channel("inst-1", "nope")


class TestBatchRouting:
    def test_batch(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        events = [_event(event_id=f"evt-{i}") for i in range(3)]
        records = r.route_batch(events)
        assert len(records) == 3


class TestDeliveryHistory:
    def test_get_deliveries_by_event(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.route(_event(event_id="evt-1"))
        r.route(_event(event_id="evt-2"))
        records = r.get_deliveries("inst-1", event_id="evt-1")
        assert len(records) == 1
        assert records[0].event_id == "evt-1"

    def test_delivery_limit(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        for i in range(10):
            r.route(_event(event_id=f"evt-{i}"))
        records = r.get_deliveries("inst-1", limit=5)
        assert len(records) == 5

    def test_deliveries_scoped_to_installation(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.register_channel("inst-2", "ch-2", ChannelType.WEBHOOK, "https://b.com")
        r.route(_event(event_id="evt-1", installation_id="inst-1"))
        r.route(_event(event_id="evt-2", installation_id="inst-2"))
        records = r.get_deliveries("inst-1")
        assert len(records) == 1
        assert records[0].installation_id == "inst-1"


class TestListChannels:
    def test_list(self):
        r = AppNotificationRouter()
        r.register_channel("inst-1", "ch-1", ChannelType.WEBHOOK, "https://a.com")
        r.register_channel("inst-1", "ch-2", ChannelType.EMAIL, "a@b.com")
        r.register_channel("inst-2", "ch-3", ChannelType.SLACK, "#ops")
        channels = r.list_channels("inst-1")
        assert len(channels) == 2
