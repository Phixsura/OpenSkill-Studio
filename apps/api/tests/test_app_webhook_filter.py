"""Tests for App Webhook Filter — patterns, include/exclude, delivery."""

import pytest

from app.services.app_webhook_filter import AppWebhookFilter


class TestCreateFilter:
    def test_create(self):
        f = AppWebhookFilter()
        flt = f.create_filter("inst-1", "f1", "wh-1", ["user.*"])
        assert flt.patterns == ["user.*"]
        assert flt.mode == "include"

    def test_empty_patterns(self):
        f = AppWebhookFilter()
        with pytest.raises(ValueError, match="at least one"):
            f.create_filter("inst-1", "f1", "wh-1", [])

    def test_invalid_mode(self):
        f = AppWebhookFilter()
        with pytest.raises(ValueError, match="mode"):
            f.create_filter("inst-1", "f1", "wh-1", ["*"], mode="block")

    def test_duplicate(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["*"])
        with pytest.raises(ValueError, match="already exists"):
            f.create_filter("inst-1", "f1", "wh-1", ["*"])


class TestShouldDeliver:
    def test_no_filters_delivers_all(self):
        f = AppWebhookFilter()
        assert f.should_deliver("inst-1", "wh-1", "user.created") is True

    def test_include_match(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["user.*"], mode="include")
        assert f.should_deliver("inst-1", "wh-1", "user.created") is True
        assert f.should_deliver("inst-1", "wh-1", "order.placed") is False

    def test_exclude_match(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["internal.*"], mode="exclude")
        assert f.should_deliver("inst-1", "wh-1", "user.created") is True
        assert f.should_deliver("inst-1", "wh-1", "internal.debug") is False

    def test_exact_match(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["order.created"], mode="include")
        assert f.should_deliver("inst-1", "wh-1", "order.created") is True
        assert f.should_deliver("inst-1", "wh-1", "order.updated") is False

    def test_wildcard_all(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["*"], mode="include")
        assert f.should_deliver("inst-1", "wh-1", "anything") is True


class TestMatchPatterns:
    def test_glob(self):
        f = AppWebhookFilter()
        assert f.match_patterns("user.created", ["user.*"]) is True
        assert f.match_patterns("order.placed", ["user.*"]) is False

    def test_multiple_patterns(self):
        f = AppWebhookFilter()
        assert f.match_patterns("order.placed", ["user.*", "order.*"]) is True


class TestRemoveFilter:
    def test_remove(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["*"])
        assert f.remove_filter("inst-1", "f1") is True
        assert f.list_filters("inst-1") == []

    def test_remove_nonexistent(self):
        f = AppWebhookFilter()
        assert f.remove_filter("inst-1", "nope") is False


class TestIsolation:
    def test_cross_installation(self):
        f = AppWebhookFilter()
        f.create_filter("inst-1", "f1", "wh-1", ["user.*"], mode="include")
        # inst-2 has no filters → deliver all
        assert f.should_deliver("inst-2", "wh-1", "user.created") is True
