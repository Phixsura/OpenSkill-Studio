"""Tests for App Webhook Event Type — register, emit, categories."""

import pytest

from app.services.app_webhook_event_type import AppWebhookEventType


class TestRegister:
    def test_register(self):
        e = AppWebhookEventType()
        et = e.register("inst-1", "app.installed", "App was installed", "lifecycle", ["app_id"])
        assert et.category == "lifecycle"

    def test_empty_type(self):
        e = AppWebhookEventType()
        with pytest.raises(ValueError):
            e.register("inst-1", "", "Desc")


class TestEmit:
    def test_count(self):
        e = AppWebhookEventType()
        e.register("inst-1", "app.installed", "Desc")
        e.record_emit("inst-1", "app.installed")
        e.record_emit("inst-1", "app.installed")
        types = e.list_types("inst-1")
        assert types[0].emit_count == 2


class TestQuery:
    def test_by_category(self):
        e = AppWebhookEventType()
        e.register("inst-1", "app.installed", "D", "lifecycle")
        e.register("inst-1", "webhook.sent", "D", "delivery")
        assert len(e.list_types("inst-1", category="lifecycle")) == 1

    def test_categories(self):
        e = AppWebhookEventType()
        e.register("inst-1", "app.installed", "D", "lifecycle")
        e.register("inst-1", "webhook.sent", "D", "delivery")
        assert e.categories("inst-1") == ["delivery", "lifecycle"]


class TestIsolation:
    def test_cross(self):
        e = AppWebhookEventType()
        e.register("inst-1", "app.installed", "D")
        assert e.list_types("inst-2") == []
