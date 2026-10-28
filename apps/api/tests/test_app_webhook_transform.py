"""Tests for App Webhook Transform — mappings, filters, headers."""

import pytest

from app.services.app_webhook_transform import AppWebhookTransform


class TestCreate:
    def test_create(self):
        t = AppWebhookTransform()
        c = t.create_transform("inst-1", "t1", "wh-1", field_mappings={"user": "customer"})
        assert c.field_mappings == {"user": "customer"}

    def test_duplicate(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1")
        with pytest.raises(ValueError, match="already exists"):
            t.create_transform("inst-1", "t1", "wh-2")


class TestTransform:
    def test_field_rename(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1", field_mappings={"user_id": "customer_id"})
        result = t.apply_transform("inst-1", "t1", {"user_id": "u1", "name": "Alice"})
        assert "customer_id" in result.body
        assert "user_id" not in result.body
        assert result.body["name"] == "Alice"

    def test_include_fields(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1", include_fields=["id", "name"])
        result = t.apply_transform("inst-1", "t1", {"id": 1, "name": "A", "secret": "x"})
        assert "secret" not in result.body
        assert result.body["id"] == 1

    def test_exclude_fields(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1", exclude_fields=["password", "token"])
        result = t.apply_transform("inst-1", "t1", {"name": "A", "password": "x", "token": "y"})
        assert "password" not in result.body
        assert "name" in result.body

    def test_extra_headers(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1", extra_headers={"X-Custom": "value"})
        result = t.apply_transform("inst-1", "t1", {"a": 1}, headers={"Content-Type": "application/json"})
        assert result.headers["X-Custom"] == "value"
        assert result.headers["Content-Type"] == "application/json"

    def test_size_tracking(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1", exclude_fields=["big"])
        result = t.apply_transform("inst-1", "t1", {"small": 1, "big": "x" * 1000})
        assert result.transformed_size < result.original_size


class TestIsolation:
    def test_cross_installation(self):
        t = AppWebhookTransform()
        t.create_transform("inst-1", "t1", "wh-1")
        with pytest.raises(KeyError):
            t.apply_transform("inst-2", "t1", {})
