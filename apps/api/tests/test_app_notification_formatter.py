"""Notification formatter tests."""
import pytest
from app.services.app_notification_formatter import format_notification, get_notification_icon, TEMPLATES

@pytest.mark.parametrize("event", TEMPLATES.keys())
def test_known_event_formats(event):
    result = format_notification(event, app_name="App", org_name="Org", version="1.0.0")
    assert "App" in result

def test_unknown_event():
    result = format_notification("custom.event")
    assert "custom.event" in result

def test_missing_kwargs():
    result = format_notification("app.installed", app_name="App")
    assert "App" in result

@pytest.mark.parametrize("event", TEMPLATES.keys())
def test_icons_exist(event):
    icon = get_notification_icon(event)
    assert len(icon) > 0

def test_unknown_icon():
    assert get_notification_icon("unknown") == "🔔"
