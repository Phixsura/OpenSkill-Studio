"""Tests for App Response Transform — rename, remove, default."""

import pytest

from app.services.app_response_transform import AppResponseTransform


class TestAddRule:
    def test_add(self):
        t = AppResponseTransform()
        r = t.add_rule("inst-1", "r1", "rename", "user_name", "username")
        assert r.action == "rename"

    def test_rename_requires_value(self):
        t = AppResponseTransform()
        with pytest.raises(ValueError, match="new field name"):
            t.add_rule("inst-1", "r1", "rename", "field")


class TestApply:
    def test_rename(self):
        t = AppResponseTransform()
        t.add_rule("inst-1", "r1", "rename", "user_name", "username")
        result = t.apply("inst-1", {"user_name": "alice", "age": 30})
        assert "username" in result
        assert "user_name" not in result

    def test_remove(self):
        t = AppResponseTransform()
        t.add_rule("inst-1", "r1", "remove", "internal_id")
        result = t.apply("inst-1", {"id": "1", "internal_id": "secret"})
        assert "internal_id" not in result
        assert result["id"] == "1"

    def test_default(self):
        t = AppResponseTransform()
        t.add_rule("inst-1", "r1", "default", "status", "active")
        result = t.apply("inst-1", {"id": "1"})
        assert result["status"] == "active"

    def test_default_no_overwrite(self):
        t = AppResponseTransform()
        t.add_rule("inst-1", "r1", "default", "status", "active")
        result = t.apply("inst-1", {"status": "inactive"})
        assert result["status"] == "inactive"

    def test_no_rules(self):
        t = AppResponseTransform()
        result = t.apply("inst-1", {"a": 1})
        assert result == {"a": 1}


class TestIsolation:
    def test_cross(self):
        t = AppResponseTransform()
        t.add_rule("inst-1", "r1", "remove", "secret")
        result = t.apply("inst-2", {"secret": "x"})
        assert "secret" in result
