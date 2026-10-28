"""Tests for App Idempotency Store — check, store, expire."""

import pytest

from app.services.app_idempotency_store import AppIdempotencyStore


class TestStore:
    def test_store(self):
        s = AppIdempotencyStore()
        e = s.store("inst-1", "req-123", 201, '{"id": "obj-1"}')
        assert e.status_code == 201

    def test_no_overwrite(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 201, '{"id": "obj-1"}')
        with pytest.raises(ValueError, match="already exists"):
            s.store("inst-1", "req-123", 200, '{"id": "obj-2"}')


class TestCheck:
    def test_hit(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 201, '{"id": "obj-1"}')
        entry = s.check("inst-1", "req-123")
        assert entry is not None
        assert entry.response_body == '{"id": "obj-1"}'

    def test_miss(self):
        s = AppIdempotencyStore()
        assert s.check("inst-1", "req-456") is None

    def test_expired(self):
        s = AppIdempotencyStore(default_ttl=0)
        s.store("inst-1", "req-123", 200, "{}")
        assert s.check("inst-1", "req-123") is None


class TestPayloadBinding:
    def test_same_payload(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 201, '{"id": "1"}', payload='{"name": "test"}')
        entry = s.check("inst-1", "req-123", payload='{"name": "test"}')
        assert entry is not None

    def test_different_payload(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 201, '{"id": "1"}', payload='{"name": "test"}')
        with pytest.raises(ValueError, match="different payload"):
            s.check("inst-1", "req-123", payload='{"name": "other"}')


class TestRemove:
    def test_remove(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 200, "{}")
        assert s.remove("inst-1", "req-123") is True
        assert s.check("inst-1", "req-123") is None


class TestIsolation:
    def test_cross(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "req-123", 200, "{}")
        assert s.check("inst-2", "req-123") is None
