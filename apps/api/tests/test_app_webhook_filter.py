"""Tests for App Webhook Filter — rules, matching, delivery decisions."""

import pytest

from app.services.app_webhook_filter import AppWebhookFilter


class TestAddRule:
    def test_add(self):
        f = AppWebhookFilter()
        r = f.add_rule("inst-1", "r1", "issue.created", "include")
        assert r.action == "include"

    def test_invalid_action(self):
        f = AppWebhookFilter()
        with pytest.raises(ValueError):
            f.add_rule("inst-1", "r1", "*", "drop")


class TestDeliver:
    def test_type_include(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "issue.created", "include")
        assert f.should_deliver("inst-1", "issue.created", {}) is True

    def test_type_exclude(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "issue.created", "exclude")
        assert f.should_deliver("inst-1", "issue.created", {}) is False

    def test_field_eq(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "*", "exclude", field="data.status", operator="eq", value="draft")
        assert f.should_deliver("inst-1", "issue.created", {"data": {"status": "draft"}}) is False
        assert f.should_deliver("inst-1", "issue.created", {"data": {"status": "open"}}) is True

    def test_field_contains(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "*", "include", field="data.title", operator="contains", value="urgent")
        assert f.should_deliver("inst-1", "issue.created", {"data": {"title": "urgent fix"}}) is True

    def test_field_exists(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "*", "exclude", field="data.internal", operator="exists")
        assert f.should_deliver("inst-1", "test", {"data": {"internal": True}}) is False
        assert f.should_deliver("inst-1", "test", {"data": {}}) is True

    def test_priority(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "*", "exclude", priority=1)
        f.add_rule("inst-1", "r2", "issue.created", "include", priority=10)
        assert f.should_deliver("inst-1", "issue.created", {}) is True

    def test_default_deliver(self):
        f = AppWebhookFilter()
        assert f.should_deliver("inst-1", "any.event", {}) is True


class TestIsolation:
    def test_cross(self):
        f = AppWebhookFilter()
        f.add_rule("inst-1", "r1", "*", "exclude")
        assert f.should_deliver("inst-2", "test", {}) is True
