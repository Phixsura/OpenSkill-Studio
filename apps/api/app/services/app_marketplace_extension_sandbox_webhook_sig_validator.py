"""Sandbox Webhook Sig Validator — validate inbound webhook signatures.

Verifies HMAC signatures for popular providers (GitHub, Stripe, Slack)
with timing-safe comparison and provider-specific header extraction.
"""
from __future__ import annotations
import hashlib
import hmac
from dataclasses import dataclass
from enum import Enum


class Provider(str, Enum):
    GITHUB = "github"
    STRIPE = "stripe"
    SLACK = "slack"
    CUSTOM = "custom"


PROVIDER_HEADERS = {
    Provider.GITHUB: "X-Hub-Signature-256",
    Provider.STRIPE: "Stripe-Signature",
    Provider.SLACK: "X-Slack-Signature",
    Provider.CUSTOM: "X-Signature",
}


@dataclass
class VerifyResult:
    valid: bool
    provider: str
    reason: str = ""


class SandboxWebhookSigValidatorService:
    """Verifies webhook signatures from popular providers."""

    def __init__(self):
        self._secrets: dict[str, dict[str, str]] = {}

    def register_secret(self, sandbox_id: str, provider: Provider,
                        secret: str) -> None:
        self._secrets.setdefault(sandbox_id, {})[provider.value] = secret

    def verify(self, sandbox_id: str, provider: Provider,
               payload: str, signature: str) -> VerifyResult:
        secret = self._secrets.get(sandbox_id, {}).get(provider.value)
        if not secret:
            return VerifyResult(False, provider.value, "No secret configured")
        if not signature:
            return VerifyResult(False, provider.value, "No signature provided")

        if provider == Provider.GITHUB:
            expected = "sha256=" + hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            valid = hmac.compare_digest(signature, expected)
        elif provider == Provider.STRIPE:
            # Simplified: real Stripe uses timestamp + payload
            expected = hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            valid = hmac.compare_digest(signature, expected)
        elif provider == Provider.SLACK:
            expected = "v0=" + hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            valid = hmac.compare_digest(signature, expected)
        else:
            expected = hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            valid = hmac.compare_digest(signature, expected)

        return VerifyResult(valid, provider.value,
                            "" if valid else "Signature mismatch")

    def get_header_name(self, provider: Provider) -> str:
        return PROVIDER_HEADERS.get(provider, "X-Signature")

    def list_configured(self, sandbox_id: str) -> list[str]:
        return sorted(self._secrets.get(sandbox_id, {}).keys())
