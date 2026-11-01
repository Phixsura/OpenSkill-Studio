import pytest
from app.services.app_api_developer_api_api_webhook_payload_encryption import AppAPIDeveloperAPIApiWebhookPayloadEncryption

class TestPayloadEncryption:
    def test_configure(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        c = e.configure("inst-1", "https://a.com", "aes-256-gcm", "a" * 32)
        assert c.algorithm == "aes-256-gcm"
        assert len(c.key_fingerprint) == 16

    def test_short_key(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        with pytest.raises(ValueError, match="32 bytes"):
            e.configure("inst-1", "https://a.com", "aes-256-gcm", "short")

    def test_encrypt(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        e.configure("inst-1", "https://a.com", "aes-256-gcm", "a" * 32)
        ct, size = e.encrypt("inst-1", "https://a.com", '{"data": "secret"}')
        assert len(ct) > 0
        assert size > 0

    def test_stats(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        e.configure("inst-1", "https://a.com", "aes-256-gcm", "a" * 32)
        e.encrypt("inst-1", "https://a.com", "test payload")
        s = e.stats("inst-1")
        assert s["payloads_encrypted"] == 1

    def test_disabled(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        e.configure("inst-1", "https://a.com", "aes-256-gcm", "a" * 32)
        e.toggle("inst-1", "https://a.com", False)
        with pytest.raises(ValueError, match="disabled"):
            e.encrypt("inst-1", "https://a.com", "test")

    def test_isolation(self):
        e = AppAPIDeveloperAPIApiWebhookPayloadEncryption()
        e.configure("inst-1", "https://a.com", "aes-256-gcm", "a" * 32)
        assert len(e.all_configs("inst-2")) == 0
