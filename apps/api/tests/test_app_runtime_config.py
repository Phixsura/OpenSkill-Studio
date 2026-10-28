"""Tests for App Runtime Config — versioning, rollback, history."""

import pytest

from app.services.app_runtime_config import AppRuntimeConfig


class TestSetGet:
    def test_set_and_get(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"debug": True, "timeout": 30})
        assert c.get_value("inst-1", "debug") is True
        assert c.get_value("inst-1", "timeout") == 30

    def test_get_default(self):
        c = AppRuntimeConfig()
        assert c.get_value("inst-1", "missing", default=42) == 42

    def test_get_all(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1, "b": 2})
        assert c.get_all("inst-1") == {"a": 1, "b": 2}

    def test_merge_values(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1})
        c.set_values("inst-1", {"b": 2})
        assert c.get_all("inst-1") == {"a": 1, "b": 2}

    def test_empty_values(self):
        c = AppRuntimeConfig()
        with pytest.raises(ValueError, match="empty"):
            c.set_values("inst-1", {})


class TestVersioning:
    def test_version_increments(self):
        c = AppRuntimeConfig()
        v1 = c.set_values("inst-1", {"a": 1})
        v2 = c.set_values("inst-1", {"b": 2})
        assert v1.version == 1
        assert v2.version == 2

    def test_get_version(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1})
        c.set_values("inst-1", {"b": 2})
        assert c.get_version("inst-1") == 2


class TestHistory:
    def test_newest_first(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1}, now=1000.0)
        c.set_values("inst-1", {"b": 2}, now=1001.0)
        h = c.get_history("inst-1")
        assert h[0].version == 2


class TestRollback:
    def test_rollback(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1, "b": 2})
        c.set_values("inst-1", {"a": 99})
        v = c.rollback("inst-1", 1)
        assert c.get_value("inst-1", "a") == 1
        assert v.changed_by == "rollback_to_v1"

    def test_invalid_version(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1})
        with pytest.raises(ValueError, match="Invalid version"):
            c.rollback("inst-1", 5)


class TestDeleteKey:
    def test_delete(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"a": 1, "b": 2})
        assert c.delete_key("inst-1", "a") is True
        assert c.get_value("inst-1", "a") is None

    def test_delete_nonexistent(self):
        c = AppRuntimeConfig()
        assert c.delete_key("inst-1", "nope") is False


class TestIsolation:
    def test_cross_installation(self):
        c = AppRuntimeConfig()
        c.set_values("inst-1", {"x": 1})
        assert c.get_value("inst-2", "x") is None
