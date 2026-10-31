"""Webhook header builder tests."""
import pytest
from app.services.app_webhook_headers import build_webhook_headers, extract_webhook_headers

def test_build_has_all_headers():
    h = build_webhook_headers(event_type="test.event", delivery_id="d1", payload=b'{}', webhook_secret="s")
    assert h["X-OpenSkill-Event"] == "test.event"
    assert h["X-OpenSkill-Delivery"] == "d1"
    assert h["X-OpenSkill-Signature"].startswith("sha256=")
    assert h["Content-Type"] == "application/json"
    assert "X-OpenSkill-Timestamp" in h

def test_signature_matches_payload():
    from app.services.webhook_verify import verify_signature
    payload = b'{"event":"test"}'
    secret = "my-secret"
    h = build_webhook_headers(event_type="t", delivery_id="d", payload=payload, webhook_secret=secret)
    sig = h["X-OpenSkill-Signature"]
    assert verify_signature(payload, sig, secret)

def test_extract_headers():
    h = build_webhook_headers(event_type="app.installed", delivery_id="d99", payload=b'{}', webhook_secret="s")
    extracted = extract_webhook_headers(h)
    assert extracted["event_type"] == "app.installed"
    assert extracted["delivery_id"] == "d99"
    assert len(extracted["signature"]) > 60

def test_extract_empty():
    extracted = extract_webhook_headers({})
    assert extracted["event_type"] == ""

def test_user_agent():
    h = build_webhook_headers(event_type="t", delivery_id="d", payload=b'{}', webhook_secret="s")
    assert "OpenSkill" in h["User-Agent"]
