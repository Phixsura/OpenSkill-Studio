import hashlib, hmac, pytest
from app.services.app_api_developer_api_webhook_signature_verifier import AppAPIDeveloperAPIWebhookSignatureVerifier

class TestSignatureVerifier:
    def test_valid_signature(self):
        v = AppAPIDeveloperAPIWebhookSignatureVerifier()
        secret = "this-is-a-long-secret-key"
        v.register_secret("inst-1", "https://a.com", secret)
        payload = '{"event": "push"}'
        sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        r = v.verify("inst-1", "https://a.com", "d1", payload, sig)
        assert r.valid is True

    def test_invalid_signature(self):
        v = AppAPIDeveloperAPIWebhookSignatureVerifier()
        v.register_secret("inst-1", "https://a.com", "this-is-a-long-secret-key")
        r = v.verify("inst-1", "https://a.com", "d1", "payload", "badsig")
        assert r.valid is False

    def test_no_secret(self):
        v = AppAPIDeveloperAPIWebhookSignatureVerifier()
        r = v.verify("inst-1", "https://a.com", "d1", "payload", "sig")
        assert r.valid is False
        assert "no secret" in r.reason

    def test_short_secret(self):
        v = AppAPIDeveloperAPIWebhookSignatureVerifier()
        with pytest.raises(ValueError):
            v.register_secret("inst-1", "https://a.com", "short")

    def test_stats(self):
        v = AppAPIDeveloperAPIWebhookSignatureVerifier()
        v.register_secret("inst-1", "https://a.com", "this-is-a-long-secret-key")
        payload = "test"
        sig = hmac.new("this-is-a-long-secret-key".encode(), payload.encode(), hashlib.sha256).hexdigest()
        v.verify("inst-1", "https://a.com", "d1", payload, sig)
        v.verify("inst-1", "https://a.com", "d2", payload, "bad")
        s = v.stats("inst-1")
        assert s == {"total": 2, "valid": 1, "invalid": 1}
