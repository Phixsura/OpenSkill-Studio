from app.services.app_marketplace_extension_webhook_signature import (
    WebhookSignatureService,
)
import time


def test_create_secret():
    svc = WebhookSignatureService()
    ws = svc.create_secret("ext-1")
    assert ws.secret_key.startswith("whsec_")


def test_sign_and_verify():
    svc = WebhookSignatureService()
    svc.create_secret("ext-1")
    payload = '{"event": "deploy", "status": "success"}'
    signed = svc.sign("ext-1", payload)
    assert signed is not None
    result = svc.verify("ext-1", payload, signed["signature"],
                        signed["timestamp"], signed["nonce"])
    assert result["valid"] is True


def test_invalid_signature():
    svc = WebhookSignatureService()
    svc.create_secret("ext-1")
    signed = svc.sign("ext-1", "payload")
    result = svc.verify("ext-1", "tampered", signed["signature"],
                        signed["timestamp"], signed["nonce"])
    assert result["valid"] is False
    assert "Invalid signature" in result["reason"]


def test_replay_protection():
    svc = WebhookSignatureService()
    svc.create_secret("ext-1")
    signed = svc.sign("ext-1", "data")
    svc.verify("ext-1", "data", signed["signature"],
               signed["timestamp"], signed["nonce"])
    # Second use of same nonce
    result = svc.verify("ext-1", "data", signed["signature"],
                        signed["timestamp"], signed["nonce"])
    assert result["valid"] is False
    assert "replay" in result["reason"].lower()


def test_expired_timestamp():
    svc = WebhookSignatureService()
    svc.create_secret("ext-1")
    old_ts = int(time.time()) - 600  # 10 minutes ago
    signed = svc.sign("ext-1", "data", timestamp=old_ts)
    result = svc.verify("ext-1", "data", signed["signature"],
                        signed["timestamp"], signed["nonce"])
    assert result["valid"] is False
    assert "expired" in result["reason"].lower()


def test_rotate_secret():
    svc = WebhookSignatureService()
    ws1 = svc.create_secret("ext-1")
    ws2 = svc.rotate_secret("ext-1")
    assert ws2 is not None
    assert ws1.secret_key != ws2.secret_key


def test_no_secret():
    svc = WebhookSignatureService()
    result = svc.verify("ext-x", "data", "v1=abc", int(time.time()), "nonce")
    assert result["valid"] is False
