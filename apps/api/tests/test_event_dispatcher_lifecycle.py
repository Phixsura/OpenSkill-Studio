"""EventDispatcher lifecycle tests."""

import inspect
import pytest
from app.services.event_dispatch import EventDispatcher, emit_event

def test_create_dispatcher():
    d = EventDispatcher()
    assert d is not None

def test_dispatcher_has_emit():
    assert inspect.iscoroutinefunction(EventDispatcher.emit)

def test_dispatcher_has_close():
    assert inspect.iscoroutinefunction(EventDispatcher.close)

def test_dispatcher_has_deliver_webhook():
    assert hasattr(EventDispatcher, "_deliver_webhook")
    assert inspect.iscoroutinefunction(EventDispatcher._deliver_webhook)

def test_dispatcher_has_process_automation():
    assert hasattr(EventDispatcher, "_process_automation_rules")
    assert inspect.iscoroutinefunction(EventDispatcher._process_automation_rules)

def test_emit_event_shortcut():
    assert inspect.iscoroutinefunction(emit_event)

def test_emit_event_params():
    params = inspect.signature(emit_event).parameters
    assert "db" in params
    assert "event_type" in params
