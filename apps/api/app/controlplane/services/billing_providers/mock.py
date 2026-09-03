"""Mock billing provider (ADR-014 §6.2): deterministic refs + HMAC-signed
webhooks so tests and dev flows can forge VALID events end-to-end."""

import hashlib
import hmac
import json

from ulid import ULID

from app.config import settings
from app.controlplane.services.billing_providers.base import (
    BillingProviderBase,
    CheckoutSession,
    ParsedWebhookEvent,
)
from app.exceptions import AppError


def mock_webhook_key() -> bytes:
    """Derived signing key — tests import this to forge valid events."""
    return hashlib.sha256((settings.jwt_secret + "mock-billing").encode()).digest()


def sign_mock_event(payload: dict) -> tuple[bytes, str]:
    """Return (raw_body, signature header value) for a forged event."""
    raw = json.dumps(payload, sort_keys=True).encode()
    sig = hmac.new(mock_webhook_key(), raw, hashlib.sha256).hexdigest()
    return raw, sig


class MockProvider(BillingProviderBase):
    key = "mock"

    async def create_customer(self, tenant) -> str:
        return f"mock_cus_{tenant.id}"

    async def create_checkout_session(
        self,
        *,
        tenant,
        kind: str,
        plan_price=None,
        amount_minor: int | None = None,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> CheckoutSession:
        session_ref = f"mock_sess_{ULID()}"
        return CheckoutSession(
            url=f"{settings.frontend_url}/mock-checkout?session={session_ref}&kind={kind}",
            session_ref=session_ref,
        )

    async def change_subscription(
        self, external_ref, new_price_ref, seat_quantity, cancel_at_period_end: bool = False
    ) -> None:
        return None

    async def cancel_subscription(self, external_ref, at_period_end) -> None:
        return None

    async def fetch_payment_status(self, external_ref) -> str:
        return "succeeded"

    def verify_webhook(self, headers: dict, raw_body: bytes) -> ParsedWebhookEvent:
        provided = headers.get("x-mock-signature") or headers.get("X-Mock-Signature")
        if not provided:
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Missing signature", 401)
        expected = hmac.new(mock_webhook_key(), raw_body, hashlib.sha256).hexdigest()
        # Compare as bytes: hmac.compare_digest raises TypeError on non-ASCII
        # str inputs, and Starlette decodes header bytes as latin-1 — a header
        # like `X-Mock-Signature: \xff\xff` turned an unauthenticated request
        # into a 500 instead of a 401 (R64[20]).
        if not hmac.compare_digest(provided.encode("utf-8", errors="replace"), expected.encode()):
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Invalid signature", 401)
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Malformed payload", 401) from exc
        event_id = payload.get("id")
        event_type = payload.get("type")
        if not isinstance(event_id, str) or not isinstance(event_type, str):
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Malformed event", 401)
        return ParsedWebhookEvent(
            external_event_id=event_id,
            event_type=event_type,
            data=payload.get("data") or {},
        )
