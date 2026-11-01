from app.services.app_marketplace_sandbox_ipc import (
    SandboxIPC, MessageType,
)


def test_send_and_receive():
    ipc = SandboxIPC()
    msg, status = ipc.send("config.read", {"key": "theme"}, sender="sandbox")
    assert msg is not None
    assert status == "Sent"
    messages = ipc.receive("host")
    assert len(messages) == 1
    assert messages[0].payload["key"] == "theme"


def test_disallowed_channel():
    ipc = SandboxIPC()
    msg, status = ipc.send("forbidden.channel", {})
    assert msg is None
    assert "not allowed" in status


def test_handler_auto_response():
    ipc = SandboxIPC()
    ipc.register_handler("config.read", lambda p: {"value": "dark"})
    ipc.send("config.read", {"key": "theme"}, sender="sandbox")
    responses = ipc.receive("sandbox")
    assert len(responses) == 1
    assert responses[0].msg_type == MessageType.RESPONSE
    assert responses[0].payload["value"] == "dark"


def test_drain():
    ipc = SandboxIPC()
    ipc.send("log.write", {"msg": "a"}, sender="sandbox")
    ipc.send("log.write", {"msg": "b"}, sender="sandbox")
    drained = ipc.drain("host")
    assert len(drained) == 2
    assert ipc.receive("host") == []  # cleared


def test_message_log():
    ipc = SandboxIPC()
    ipc.send("event.emit", {"type": "click"}, sender="sandbox")
    ipc.send("ui.notify", {"text": "hello"}, sender="host")
    log = ipc.get_log()
    assert len(log) == 2
    event_log = ipc.get_log(channel="event.emit")
    assert len(event_log) == 1


def test_allowed_channels():
    ipc = SandboxIPC()
    channels = ipc.get_allowed_channels()
    assert "config.read" in channels
    assert "storage.get" in channels
    assert len(channels) >= 10


def test_custom_channels():
    ipc = SandboxIPC(allowed_channels={"custom.ping", "custom.pong"})
    msg, _ = ipc.send("custom.ping", {"data": 1})
    assert msg is not None
    msg2, _ = ipc.send("config.read", {})
    assert msg2 is None  # not in custom set
