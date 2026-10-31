"""Tests for Consumer API Key Rotation Scheduler service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_key_rotation import KeyRotationScheduler


class TestKeyRotationScheduler:
    def test_create_key(self):
        svc = KeyRotationScheduler()
        result = svc.create_key("c1")
        assert result["key_value"].startswith("sk_")
        assert result["version"] == 1

    def test_rotate(self):
        svc = KeyRotationScheduler()
        created = svc.create_key("c1")
        old_key = created["key_value"]
        result = svc.rotate(created["key_id"])
        assert result["version"] == 2
        assert result["new_key_value"] != old_key

    def test_check_due(self):
        svc = KeyRotationScheduler()
        created = svc.create_key("c1", rotation_interval_days=30, current_time=0)
        due = svc.check_due(current_time=31 * 86400)
        assert len(due) == 1
        assert due[0]["key_id"] == created["key_id"]

    def test_not_due(self):
        svc = KeyRotationScheduler()
        svc.create_key("c1", rotation_interval_days=90, current_time=0)
        due = svc.check_due(current_time=10 * 86400)
        assert len(due) == 0

    def test_auto_rotate_disabled(self):
        svc = KeyRotationScheduler()
        svc.create_key("c1", rotation_interval_days=1, auto_rotate=False, current_time=0)
        due = svc.check_due(current_time=100 * 86400)
        assert len(due) == 0

    def test_revoke(self):
        svc = KeyRotationScheduler()
        created = svc.create_key("c1")
        svc.revoke(created["key_id"])
        info = svc.get_key_info(created["key_id"])
        assert info["status"] == "revoked"

    def test_cannot_rotate_revoked(self):
        svc = KeyRotationScheduler()
        created = svc.create_key("c1")
        svc.revoke(created["key_id"])
        with pytest.raises(ValueError):
            svc.rotate(created["key_id"])

    def test_rotation_history(self):
        svc = KeyRotationScheduler()
        created = svc.create_key("c1")
        svc.rotate(created["key_id"])
        svc.rotate(created["key_id"])
        history = svc.get_rotation_history(created["key_id"])
        assert len(history) == 2

    def test_list_keys(self):
        svc = KeyRotationScheduler()
        svc.create_key("c1")
        svc.create_key("c1")
        svc.create_key("c2")
        assert len(svc.list_keys(consumer_id="c1")) == 2

    def test_stats(self):
        svc = KeyRotationScheduler()
        k1 = svc.create_key("c1")
        svc.create_key("c2", auto_rotate=False)
        svc.rotate(k1["key_id"])
        stats = svc.get_stats()
        assert stats["total_keys"] == 2
        assert stats["auto_rotate_enabled"] == 1
        assert stats["total_rotations"] == 1

    def test_isolation(self):
        a, b = KeyRotationScheduler(), KeyRotationScheduler()
        a.create_key("c1")
        assert b.list_keys() == []
