"""Webhook config builder tests."""
import pytest
from app.services.app_webhook_config import build_webhook_config, validate_webhook_config

def test_build():
    c = build_webhook_config(webhook_url="https://x.com/hook", events=["app.installed"], secret="s")
    assert c["url"] == "https://x.com/hook"
    assert c["ssl_verification"] is True

def test_events_sorted():
    c = build_webhook_config(webhook_url="u", events=["b.event", "a.event"], secret="s")
    assert c["events"] == ["a.event", "b.event"]

def test_validate_valid():
    c = build_webhook_config(webhook_url="u", events=["e"], secret="s")
    assert validate_webhook_config(c) == []

def test_validate_missing_url():
    assert len(validate_webhook_config({"events": ["e"], "secret": "s"})) > 0

def test_validate_missing_events():
    assert len(validate_webhook_config({"url": "u", "events": [], "secret": "s"})) > 0

def test_validate_excessive_retries():
    c = build_webhook_config(webhook_url="u", events=["e"], secret="s", max_retries=20)
    assert len(validate_webhook_config(c)) > 0
