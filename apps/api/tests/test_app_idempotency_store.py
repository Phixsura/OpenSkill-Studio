"""Tests for App Idempotency Store — dedup, collision, TTL, replay."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_idempotency_store import AppIdempotencyStore


class TestCheck:
    def test_first_request_not_duplicate(self):
        s = AppIdempotencyStore()
        r = s.check("inst-1", "key-1", {"action": "create"})
        assert r.is_duplicate is False

    def test_empty_key_not_duplicate(self):
        s = AppIdempotencyStore()
        r = s.check("inst-1", "", {"action": "create"})
        assert r.is_duplicate is False

    def test_stored_request_is_duplicate(self):
        s = AppIdempotencyStore()
        payload = {"action": "create", "name": "test"}
        s.store("inst-1", "key-1", payload, 201, {"id": "new-1"})
        r = s.check("inst-1", "key-1", payload)
        assert r.is_duplicate is True
        assert r.stored_status_code == 201
        assert r.stored_response == {"id": "new-1"}

    def test_different_key_not_duplicate(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "key-1", {"a": 1}, 200, {"ok": True})
        r = s.check("inst-1", "key-2", {"a": 1})
        assert r.is_duplicate is False


class TestCollision:
    def test_same_key_different_payload(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "key-1", {"action": "create"}, 201, {"id": "1"})
        r = s.check("inst-1", "key-1", {"action": "delete"})
        assert r.is_duplicate is True
        assert r.is_collision is True
        assert "different payload" in r.error

    def test_same_key_same_payload_no_collision(self):
        s = AppIdempotencyStore()
        payload = {"x": 1}
        s.store("inst-1", "key-1", payload, 200, {"ok": True})
        r = s.check("inst-1", "key-1", payload)
        assert r.is_collision is False


class TestTTL:
    def test_expired_not_duplicate(self):
        s = AppIdempotencyStore(ttl_hours=1)
        s.store("inst-1", "key-1", {"a": 1}, 200, {"ok": True})
        future = datetime.now(UTC) + timedelta(hours=2)
        r = s.check("inst-1", "key-1", {"a": 1}, now=future)
        assert r.is_duplicate is False

    def test_not_expired_is_duplicate(self):
        s = AppIdempotencyStore(ttl_hours=24)
        s.store("inst-1", "key-1", {"a": 1}, 200, {"ok": True})
        soon = datetime.now(UTC) + timedelta(hours=1)
        r = s.check("inst-1", "key-1", {"a": 1}, now=soon)
        assert r.is_duplicate is True

    def test_cleanup_expired(self):
        s = AppIdempotencyStore(ttl_hours=1)
        s.store("inst-1", "key-1", {}, 200, {})
        s.store("inst-1", "key-2", {}, 200, {})
        future = datetime.now(UTC) + timedelta(hours=2)
        count = s.cleanup_expired(now=future)
        assert count == 2
        assert s.size() == 0

    def test_cleanup_keeps_fresh(self):
        s = AppIdempotencyStore(ttl_hours=24)
        s.store("inst-1", "key-1", {}, 200, {})
        soon = datetime.now(UTC) + timedelta(hours=1)
        count = s.cleanup_expired(now=soon)
        assert count == 0
        assert s.size() == 1


class TestInstallationScope:
    def test_different_installations_independent(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "key-1", {"a": 1}, 200, {"ok": True})
        r = s.check("inst-2", "key-1", {"a": 1})
        assert r.is_duplicate is False


class TestStore:
    def test_store_requires_key(self):
        s = AppIdempotencyStore()
        with pytest.raises(ValueError, match="required"):
            s.store("inst-1", "", {}, 200, {})

    def test_store_overwrites(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "key-1", {"v": 1}, 200, {"r": 1})
        s.store("inst-1", "key-1", {"v": 2}, 201, {"r": 2})
        r = s.check("inst-1", "key-1", {"v": 2})
        assert r.stored_status_code == 201

    def test_size(self):
        s = AppIdempotencyStore()
        s.store("inst-1", "k1", {}, 200, {})
        s.store("inst-1", "k2", {}, 200, {})
        assert s.size() == 2
