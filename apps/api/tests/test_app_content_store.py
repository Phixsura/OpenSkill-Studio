"""Tests for App Content Store — CRUD, versioning, quota."""

import pytest

from app.services.app_content_store import AppContentStore


class TestPut:
    def test_create(self):
        s = AppContentStore()
        e = s.put("inst-1", "readme", "# Hello", content_type="text/markdown")
        assert e.key == "readme"
        assert e.version == 1
        assert e.content_type == "text/markdown"

    def test_update_increments_version(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "v1")
        e = s.put("inst-1", "k1", "v2")
        assert e.version == 2
        assert e.content == "v2"

    def test_missing_key(self):
        s = AppContentStore()
        with pytest.raises(ValueError, match="key"):
            s.put("inst-1", "", "content")

    def test_quota_exceeded(self):
        s = AppContentStore(max_size_bytes=100)
        with pytest.raises(ValueError, match="quota"):
            s.put("inst-1", "k1", "x" * 200)

    def test_update_within_quota(self):
        s = AppContentStore(max_size_bytes=100)
        s.put("inst-1", "k1", "x" * 50)
        # Replacing same key — old size freed
        e = s.put("inst-1", "k1", "y" * 80)
        assert e.version == 2


class TestGet:
    def test_get_existing(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "hello")
        e = s.get("inst-1", "k1")
        assert e is not None
        assert e.content == "hello"

    def test_get_nonexistent(self):
        s = AppContentStore()
        assert s.get("inst-1", "nope") is None


class TestDelete:
    def test_delete(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "data")
        assert s.delete("inst-1", "k1") is True
        assert s.get("inst-1", "k1") is None

    def test_delete_nonexistent(self):
        s = AppContentStore()
        assert s.delete("inst-1", "nope") is False


class TestHistory:
    def test_version_history(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "v1", now=1000.0)
        s.put("inst-1", "k1", "v2", now=1001.0)
        s.put("inst-1", "k1", "v3", now=1002.0)
        h = s.get_history("inst-1", "k1")
        assert len(h) == 2  # v1 and v2 (v3 is current)
        assert h[0].content == "v2"  # newest archived first

    def test_no_history(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "v1")
        h = s.get_history("inst-1", "k1")
        assert h == []


class TestListKeys:
    def test_list(self):
        s = AppContentStore()
        s.put("inst-1", "b", "1")
        s.put("inst-1", "a", "2")
        assert s.list_keys("inst-1") == ["a", "b"]


class TestSize:
    def test_total_size(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "hello")  # 5 bytes
        s.put("inst-1", "k2", "world")  # 5 bytes
        assert s.total_size("inst-1") == 10

    def test_entry_count(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "a")
        s.put("inst-1", "k2", "b")
        assert s.entry_count("inst-1") == 2


class TestIsolation:
    def test_cross_installation(self):
        s = AppContentStore()
        s.put("inst-1", "k1", "data")
        assert s.get("inst-2", "k1") is None
