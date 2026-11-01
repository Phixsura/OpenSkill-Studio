from app.services.app_marketplace_extension_sandbox_webhook_sig_validator import (
    SandboxWebhookSigValidatorService, Provider,
)
import hashlib, hmac


def test_github_verify():
    svc = SandboxWebhookSigValidatorService()
    svc.register_secret("sb-1", Provider.GITHUB, "mysecret")
    payload = '{"action":"push"}'
    sig = "sha256=" + hmac.new(b"mysecret", payload.encode(), hashlib.sha256).hexdigest()
    result = svc.verify("sb-1", Provider.GITHUB, payload, sig)
    assert result.valid is True


def test_invalid_signature():
    svc = SandboxWebhookSigValidatorService()
    svc.register_secret("sb-1", Provider.GITHUB, "mysecret")
    result = svc.verify("sb-1", Provider.GITHUB, "payload", "sha256=wrong")
    assert result.valid is False
    assert "mismatch" in result.reason


def test_no_secret():
    svc = SandboxWebhookSigValidatorService()
    result = svc.verify("sb-1", Provider.GITHUB, "payload", "sig")
    assert result.valid is False
    assert "No secret" in result.reason


def test_slack_verify():
    svc = SandboxWebhookSigValidatorService()
    svc.register_secret("sb-1", Provider.SLACK, "slacksecret")
    payload = "body"
    sig = "v0=" + hmac.new(b"slacksecret", payload.encode(), hashlib.sha256).hexdigest()
    result = svc.verify("sb-1", Provider.SLACK, payload, sig)
    assert result.valid is True


def test_header_names():
    svc = SandboxWebhookSigValidatorService()
    assert svc.get_header_name(Provider.GITHUB) == "X-Hub-Signature-256"
    assert svc.get_header_name(Provider.STRIPE) == "Stripe-Signature"


def test_list_configured():
    svc = SandboxWebhookSigValidatorService()
    svc.register_secret("sb-1", Provider.GITHUB, "s1")
    svc.register_secret("sb-1", Provider.SLACK, "s2")
    assert svc.list_configured("sb-1") == ["github", "slack"]
