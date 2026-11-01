"""Tests for Webhook Secret Rotation service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_secret_rotation import SecretRotation


class TestSecretRotation:
    def test_initialize(self):
        svc = SecretRotation()
        result = svc.initialize("wh1", "my-secret-key-abcdef1234567890")
        assert result["version"] == 1

    def test_validate_active(self):
        svc = SecretRotation()
        svc.initialize("wh1", "secret-abcdefghijklmnop")
        result = svc.validate("wh1", "secret-abcdefghijklmnop")
        assert result["valid"] is True
        assert result["status"] == "active"

    def test_rotate(self):
        svc = SecretRotation()
        svc.initialize("wh1", "old-secret-key-12345678")
        result = svc.rotate("wh1", current_time=100.0, new_secret="new-secret-key-87654321")
        assert result["new_version"] == 2

    def test_grace_period(self):
        svc = SecretRotation()
        svc.configure_grace(3600)
        svc.initialize("wh1", "old-key-1234567890abcdef")
        svc.rotate("wh1", current_time=100.0, new_secret="new-key-1234567890abcdef")
        # Old key still valid during grace
        result = svc.validate("wh1", "old-key-1234567890abcdef", current_time=200.0)
        assert result["valid"] is True
        assert result["status"] == "grace"

    def test_grace_expired(self):
        svc = SecretRotation()
        svc.configure_grace(100)
        svc.initialize("wh1", "old-key-1234567890abcdef")
        svc.rotate("wh1", current_time=100.0, new_secret="new-key-1234567890abcdef")
        result = svc.validate("wh1", "old-key-1234567890abcdef", current_time=300.0)
        assert result["valid"] is False

    def test_mismatch(self):
        svc = SecretRotation()
        svc.initialize("wh1", "real-secret-key-0000000")
        result = svc.validate("wh1", "wrong-secret")
        assert result["valid"] is False

    def test_versions(self):
        svc = SecretRotation()
        svc.initialize("wh1", "secret-v1-aaaabbbbccccdddd")
        svc.rotate("wh1", new_secret="secret-v2-eeeeffffgggghhhh")
        versions = svc.get_versions("wh1")
        assert len(versions) == 2
        assert versions[0]["version"] == 1

    def test_cleanup(self):
        svc = SecretRotation()
        svc.configure_grace(10)
        svc.initialize("wh1", "s1-abcdefghijklmnop")
        svc.rotate("wh1", current_time=100.0, new_secret="s2-abcdefghijklmnop")
        result = svc.cleanup_expired("wh1", current_time=200.0)
        assert result["removed"] == 1

    def test_get_active(self):
        svc = SecretRotation()
        svc.initialize("wh1", "the-active-secret-key!")
        active = svc.get_active_secret("wh1")
        assert active["secret"] == "the-active-secret-key!"

    def test_duplicate_init(self):
        svc = SecretRotation()
        svc.initialize("wh1", "secret-1234567890abcdef")
        with pytest.raises(ValueError):
            svc.initialize("wh1", "secret-abcdef1234567890")

    def test_isolation(self):
        a, b = SecretRotation(), SecretRotation()
        a.initialize("wh1", "secret-aaaaaaaabbbbbbbb")
        assert b.validate("wh1", "secret-aaaaaaaabbbbbbbb")["valid"] is False
