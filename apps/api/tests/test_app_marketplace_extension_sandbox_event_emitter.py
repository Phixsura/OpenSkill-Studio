from app.services.app_marketplace_extension_sandbox_event_emitter import (
    SandboxEventEmitterService,
)
import pytest


def test_on_and_emit():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "user:created", "handle_user")
    event = svc.emit("sb-1", "user:created", {"name": "alice"})
    assert event.listeners_notified == 1


def test_wildcard_match():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "user:*", "handle_all")
    e1 = svc.emit("sb-1", "user:created")
    e2 = svc.emit("sb-1", "user:deleted")
    e3 = svc.emit("sb-1", "order:created")
    assert e1.listeners_notified == 1
    assert e2.listeners_notified == 1
    assert e3.listeners_notified == 0


def test_once_listener():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "init", "setup", once=True)
    svc.emit("sb-1", "init")
    event = svc.emit("sb-1", "init")
    assert event.listeners_notified == 0


def test_max_calls():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "tick", "handler", max_calls=3)
    for _ in range(3):
        svc.emit("sb-1", "tick")
    event = svc.emit("sb-1", "tick")
    assert event.listeners_notified == 0


def test_off():
    svc = SandboxEventEmitterService()
    listener = svc.on("sb-1", "event", "handler")
    assert svc.off("sb-1", listener.listener_id) is True
    event = svc.emit("sb-1", "event")
    assert event.listeners_notified == 0


def test_max_listeners():
    svc = SandboxEventEmitterService()
    for i in range(50):
        svc.on("sb-1", "flood", f"handler_{i}")
    with pytest.raises(ValueError, match="Max listeners"):
        svc.on("sb-1", "flood", "one_more")


def test_history():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "*", "log")
    svc.emit("sb-1", "a")
    svc.emit("sb-1", "b")
    svc.emit("sb-1", "a")
    history = svc.get_history("sb-1", event_name="a")
    assert len(history) == 2


def test_clear_listeners():
    svc = SandboxEventEmitterService()
    svc.on("sb-1", "a", "h1")
    svc.on("sb-1", "b", "h2")
    cleared = svc.clear_listeners("sb-1")
    assert cleared == 2
    assert len(svc.list_listeners("sb-1")) == 0
