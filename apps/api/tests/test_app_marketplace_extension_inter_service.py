from app.services.app_marketplace_extension_inter_service import (
    InterServiceCommService, MessageType,
)


def test_send_and_receive():
    svc = InterServiceCommService()
    svc.grant_access("ext-a", ["data"])
    svc.grant_access("ext-b", ["data"])
    msg = svc.send("ext-a", "ext-b", "data", {"key": "value"})
    assert isinstance(msg, object)
    received = svc.receive("ext-b")
    assert len(received) == 1
    assert received[0].payload["key"] == "value"


def test_no_access_rejected():
    svc = InterServiceCommService()
    result = svc.send("ext-a", "ext-b", "secret", {})
    assert isinstance(result, dict)
    assert "error" in result


def test_broadcast():
    svc = InterServiceCommService()
    svc.grant_access("ext-a", ["events"])
    svc.grant_access("ext-b", ["events"])
    svc.grant_access("ext-c", ["events"])
    svc.subscribe("ext-b", "events")
    svc.subscribe("ext-c", "events")
    msgs = svc.broadcast("ext-a", "events", {"type": "deploy"})
    assert len(msgs) == 2  # b and c, not a


def test_subscribe_requires_access():
    svc = InterServiceCommService()
    assert svc.subscribe("ext-a", "private") is False


def test_reply():
    svc = InterServiceCommService()
    svc.grant_access("ext-a", ["rpc"])
    svc.grant_access("ext-b", ["rpc"])
    msg = svc.send("ext-a", "ext-b", "rpc", {"question": "status?"})
    reply = svc.reply("ext-b", msg.message_id, {"answer": "ok"})
    assert isinstance(reply, object)
    assert reply.correlation_id == msg.message_id
    assert reply.message_type == MessageType.RESPONSE


def test_channel_filter():
    svc = InterServiceCommService()
    svc.grant_access("ext-a", ["ch1", "ch2"])
    svc.send("ext-a", "ext-b", "ch1", {"a": 1})
    svc.send("ext-a", "ext-b", "ch2", {"b": 2})
    ch1_msgs = svc.receive("ext-b", channel="ch1")
    assert len(ch1_msgs) == 1


def test_stats():
    svc = InterServiceCommService()
    svc.grant_access("ext-a", ["data"])
    svc.send("ext-a", "ext-b", "data", {})
    svc.send("ext-a", "ext-b", "data", {})
    stats = svc.get_stats("ext-a")
    assert stats["sent"] == 2
    assert "data" in stats["channels"]
