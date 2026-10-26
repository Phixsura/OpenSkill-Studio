from app.services.app_marketplace_extension_notification_channel import (
    NotificationChannelService, ChannelType, Severity, DeliveryStatus,
)
import pytest


def test_add_channel():
    svc = NotificationChannelService()
    ch = svc.add_channel("ext-1", "Alerts", ChannelType.EMAIL, {"address": "a@b.com"})
    assert ch.channel_id.startswith("ch_")
    assert ch.channel_type == ChannelType.EMAIL


def test_email_requires_address():
    svc = NotificationChannelService()
    with pytest.raises(ValueError, match="address"):
        svc.add_channel("ext-1", "Bad", ChannelType.EMAIL, {})


def test_send_to_matching_channels():
    svc = NotificationChannelService()
    svc.add_channel("ext-1", "All", ChannelType.IN_APP, {})
    svc.add_channel("ext-1", "Errors Only", ChannelType.IN_APP, {},
                    min_severity=Severity.ERROR)
    sent = svc.send("ext-1", "deploy", Severity.INFO, "Deployed", "v1.0")
    assert len(sent) == 1  # only "All" channel


def test_severity_filter():
    svc = NotificationChannelService()
    svc.add_channel("ext-1", "Critical", ChannelType.IN_APP, {},
                    min_severity=Severity.CRITICAL)
    sent = svc.send("ext-1", "warn", Severity.WARNING, "Warning", "msg")
    assert len(sent) == 0
    sent2 = svc.send("ext-1", "crash", Severity.CRITICAL, "Crash", "msg")
    assert len(sent2) == 1


def test_event_filter():
    svc = NotificationChannelService()
    svc.add_channel("ext-1", "Deploy Only", ChannelType.IN_APP, {},
                    event_filters=["deploy"])
    sent = svc.send("ext-1", "build", Severity.INFO, "Built", "ok")
    assert len(sent) == 0
    sent2 = svc.send("ext-1", "deploy", Severity.INFO, "Deployed", "ok")
    assert len(sent2) == 1


def test_disable_channel():
    svc = NotificationChannelService()
    ch = svc.add_channel("ext-1", "Ch", ChannelType.IN_APP, {})
    svc.disable_channel(ch.channel_id)
    sent = svc.send("ext-1", "test", Severity.INFO, "T", "M")
    assert len(sent) == 0


def test_history():
    svc = NotificationChannelService()
    svc.add_channel("ext-1", "Ch", ChannelType.IN_APP, {})
    svc.send("ext-1", "a", Severity.INFO, "A", "m")
    svc.send("ext-1", "b", Severity.ERROR, "B", "m")
    history = svc.get_history("ext-1")
    assert len(history) == 2
    assert history[1]["severity"] == "error"
