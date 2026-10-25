from app.services.app_marketplace_inter_extension_messaging import (
    InterExtensionMessaging,
)


def test_create_channel_and_send():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-1", "Events", "ext-a", receivers=["ext-b"])
    msg, status = iem.send("ch-1", "ext-a", {"event": "user.created"})
    assert msg is not None
    assert status == "Sent"


def test_unauthorized_sender():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-2", "Data", "ext-a")
    msg, status = iem.send("ch-2", "ext-b", {"data": 1})
    assert msg is None
    assert "not authorized" in status


def test_receive():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-3", "Queue", "ext-a", receivers=["ext-b"])
    iem.send("ch-3", "ext-a", {"n": 1})
    iem.send("ch-3", "ext-a", {"n": 2})
    msgs, _ = iem.receive("ch-3", "ext-b")
    assert len(msgs) == 2


def test_unauthorized_receiver():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-4", "Private", "ext-a", receivers=["ext-b"])
    msgs, status = iem.receive("ch-4", "ext-c")
    assert len(msgs) == 0
    assert "not authorized" in status


def test_consume():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-5", "Work", "ext-a", receivers=["ext-b"])
    iem.send("ch-5", "ext-a", {"task": "A"})
    iem.send("ch-5", "ext-a", {"task": "B"})
    consumed = iem.consume("ch-5", "ext-b", 1)
    assert len(consumed) == 1
    assert consumed[0].payload["task"] == "A"
    assert iem.get_queue_depth("ch-5") == 1


def test_grant_access():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-6", "Shared", "ext-a")
    iem.grant_access("ch-6", "ext-c", can_send=True, can_receive=True)
    msg, _ = iem.send("ch-6", "ext-c", {"from": "c"})
    assert msg is not None


def test_list_channels():
    iem = InterExtensionMessaging()
    iem.create_channel("ch-a", "A", "ext-1", receivers=["ext-2"])
    iem.create_channel("ch-b", "B", "ext-2")
    channels = iem.list_channels("ext-2")
    assert len(channels) == 2
