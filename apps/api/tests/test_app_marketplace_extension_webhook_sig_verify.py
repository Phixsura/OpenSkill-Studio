from app.services.app_marketplace_extension_webhook_sig_verify import (
    WebhookSigVerifyService, WebhookSigError
)
import pytest
import time


def test_sign_and_verify():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "whsec_test123")
    sig = svc.sign("whsec_test123", '{"event":"test"}')
    result = svc.verify("ep-1", '{"event":"test"}', sig)
    assert result["verified"] is True


def test_tampered_payload():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "secret")
    sig = svc.sign("secret", '{"event":"original"}')
    with pytest.raises(WebhookSigError, match="verification failed"):
        svc.verify("ep-1", '{"event":"tampered"}', sig)


def test_wrong_secret():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "correct-secret")
    sig = svc.sign("wrong-secret", '{"event":"test"}')
    with pytest.raises(WebhookSigError, match="verification failed"):
        svc.verify("ep-1", '{"event":"test"}', sig)


def test_replay_protection():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "secret")
    old_ts = int(time.time()) - 600  # 10 minutes ago
    sig = svc.sign("secret", "payload", timestamp=old_ts)
    with pytest.raises(WebhookSigError, match="too old"):
        svc.verify("ep-1", "payload", sig, tolerance=300)


def test_within_tolerance():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "secret")
    recent_ts = int(time.time()) - 30  # 30 seconds ago
    sig = svc.sign("secret", "data", timestamp=recent_ts)
    result = svc.verify("ep-1", "data", sig, tolerance=60)
    assert result["age_seconds"] <= 60


def test_secret_rotation():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "old-secret")
    svc.rotate_secret("ep-1", "new-secret", keep_old=2)
    # Old secret still works during grace
    sig_old = svc.sign("old-secret", "data")
    result = svc.verify("ep-1", "data", sig_old)
    assert result["verified"] is True
    # New secret also works
    sig_new = svc.sign("new-secret", "data")
    result = svc.verify("ep-1", "data", sig_new)
    assert result["verified"] is True


def test_no_secret_registered():
    svc = WebhookSigVerifyService()
    with pytest.raises(WebhookSigError, match="No secrets"):
        svc.verify("unknown", "data", "t=123,v1=abc")


def test_missing_timestamp():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "secret")
    with pytest.raises(WebhookSigError, match="Missing timestamp"):
        svc.verify("ep-1", "data", "v1=abcdef")


def test_parse_multi_signature():
    svc = WebhookSigVerifyService()
    svc.register_secret("ep-1", "secret")
    sig = svc.sign("secret", "data")
    # Add extra signature
    multi_sig = sig + ",v2=extrasig"
    result = svc.verify("ep-1", "data", multi_sig)
    assert result["verified"] is True
