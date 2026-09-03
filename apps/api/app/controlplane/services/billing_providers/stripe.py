"""Stripe adapter — THIN wrapper (ADR-014 §6.2, user decision): parameter
assembly → SDK call → response mapping, zero logic branches. Unit tests
monkeypatch the stripe module; webhook signatures use the real
stripe.Webhook.construct_event with a fake secret.

Card data never touches the platform — only refs are stored.
"""

import asyncio
from decimal import ROUND_HALF_UP, Decimal

import structlog

from app.config import settings
from app.controlplane.models.pricing import minor_multiplier
from app.controlplane.services.billing_providers.base import (
    BillingProviderBase,
    CheckoutSession,
    ParsedWebhookEvent,
)
from app.exceptions import AppError

log = structlog.get_logger()


def _stripe():
    """Lazy import + configure — keeps the SDK off the hot path and lets
    tests monkeypatch `stripe` wholesale."""
    import stripe as _sdk

    if not settings.stripe_secret_key:
        raise AppError("BILLING_PROVIDER_UNCONFIGURED", "Stripe is not configured", 409)
    _sdk.api_key = settings.stripe_secret_key
    return _sdk


# R75[15]: Stripe's smallest-currency-unit convention differs from the
# platform's minor_multiplier (which only treats JPY/KRW as zero-decimal).
# Stripe treats a larger set as zero-decimal, and a few as three-decimal —
# passing our amount_minor as Stripe's unit_amount for those currencies
# over/under-charged by 10-100x. Convert to Stripe's convention at the boundary.
# Sources: Stripe "zero-decimal" and "three-decimal" currency lists.
_STRIPE_ZERO_DECIMAL = frozenset(
    {
        "BIF",
        "CLP",
        "DJF",
        "GNF",
        "JPY",
        "KMF",
        "KRW",
        "MGA",
        "PYG",
        "RWF",
        "UGX",
        "VND",
        "VUV",
        "XAF",
        "XOF",
        "XPF",
    }
)
_STRIPE_THREE_DECIMAL = frozenset({"BHD", "JOD", "KWD", "OMR", "TND"})


def _stripe_unit_amount(amount_minor: int, currency: str) -> int:
    """Convert a platform amount_minor into Stripe's smallest-unit amount.

    The platform stores money as major × minor_multiplier(currency) where
    minor_multiplier is 1 for JPY/KRW and 100 otherwise. Recover the major
    amount, then re-express it in Stripe's convention for this currency:
    ×1 (zero-decimal), ×1000 (three-decimal), or ×100 (default two-decimal)."""
    major = Decimal(amount_minor) / Decimal(minor_multiplier(currency))
    return int((major * _stripe_factor(currency)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _stripe_factor(currency: str) -> Decimal:
    cur = currency.upper()
    if cur in _STRIPE_ZERO_DECIMAL:
        return Decimal(1)
    if cur in _STRIPE_THREE_DECIMAL:
        return Decimal(1000)
    return Decimal(100)


def _platform_minor_from_stripe(stripe_amount: int, currency: str) -> int:
    """Inverse of _stripe_unit_amount: Stripe smallest-unit → platform minor."""
    major = Decimal(stripe_amount) / _stripe_factor(currency)
    return int((major * minor_multiplier(currency)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class StripeProvider(BillingProviderBase):
    key = "stripe"

    # R89[13]: the stripe-python SDK is SYNCHRONOUS — calling it inline in
    # async methods froze the whole event loop for the duration of every
    # Stripe HTTP round-trip (worker: outbox poll, all crons, every in-flight
    # advance task; API: every concurrent request). Offload each SDK call to
    # a thread with asyncio.to_thread.

    async def create_customer(self, tenant) -> str:
        sdk = _stripe()
        customer = await asyncio.to_thread(
            sdk.Customer.create,
            name=tenant.name,
            email=tenant.billing_email,
            metadata={"tenant_id": tenant.id},
        )
        return customer["id"]

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
        sdk = _stripe()
        meta = {"tenant_id": tenant.id, "kind": kind, **(metadata or {})}
        if kind == "subscription":
            if plan_price is None or not plan_price.external_price_ref:
                raise AppError(
                    "PLAN_NOT_AVAILABLE",
                    "This plan price has no Stripe price configured",
                    409,
                )
            session = await asyncio.to_thread(
                sdk.checkout.Session.create,
                mode="subscription",
                line_items=[{"price": plan_price.external_price_ref, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=meta,
            )
        else:  # credit_topup | purchase — one-off payment
            session = await asyncio.to_thread(
                sdk.checkout.Session.create,
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": currency.lower(),
                            "unit_amount": _stripe_unit_amount(amount_minor, currency),
                            "product_data": {"name": f"OpenSkill {kind.replace('_', ' ')}"},
                        },
                        "quantity": 1,
                    }
                ],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=meta,
            )
        return CheckoutSession(url=session["url"], session_ref=session["id"])

    async def change_subscription(
        self, external_ref: str, new_price_ref: str, seat_quantity: int
    ) -> None:
        sdk = _stripe()
        sub = await asyncio.to_thread(sdk.Subscription.retrieve, external_ref)
        await asyncio.to_thread(
            sdk.Subscription.modify,
            external_ref,
            items=[
                {
                    "id": sub["items"]["data"][0]["id"],
                    "price": new_price_ref,
                    "quantity": max(seat_quantity, 1),
                }
            ],
            proration_behavior="none",  # proration is computed platform-side
            # R101[H17]: pushing current state must also clear a pending
            # provider-side cancellation — reactivate flips the platform row
            # to active, but without this the Stripe sub still cancelled at
            # period end and the "reactivated" customer was silently dropped.
            cancel_at_period_end=False,
        )

    async def cancel_subscription(self, external_ref: str, at_period_end: bool) -> None:
        sdk = _stripe()
        if at_period_end:
            await asyncio.to_thread(
                sdk.Subscription.modify, external_ref, cancel_at_period_end=True
            )
        else:
            await asyncio.to_thread(sdk.Subscription.cancel, external_ref)

    async def fetch_payment_status(self, external_ref: str) -> str:
        sdk = _stripe()
        session = await asyncio.to_thread(sdk.checkout.Session.retrieve, external_ref)
        return session.get("payment_status", "unknown")

    def verify_webhook(self, headers: dict, raw_body: bytes) -> ParsedWebhookEvent:
        import stripe as _sdk

        sig = headers.get("stripe-signature") or headers.get("Stripe-Signature")
        if not sig or not settings.stripe_webhook_secret:
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Missing signature", 401)
        try:
            event = _sdk.Webhook.construct_event(raw_body, sig, settings.stripe_webhook_secret)
        except Exception as exc:  # noqa: BLE001 — any construct failure = invalid
            raise AppError("WEBHOOK_SIGNATURE_INVALID", "Invalid signature", 401) from exc
        obj = event["data"]["object"]
        data = obj.to_dict() if hasattr(obj, "to_dict") else dict(obj)
        # R75[15]: amount_total comes back in Stripe's smallest unit — normalize
        # it to the platform's amount_minor convention so downstream credit
        # top-ups store the right figure (a VND top-up otherwise credited 1/100
        # of the paid amount; KWD 10×). Inverse of _stripe_unit_amount.
        amt = data.get("amount_total")
        cur = data.get("currency")
        if amt is not None and cur:
            data["amount_total"] = _platform_minor_from_stripe(int(amt), cur)
        return ParsedWebhookEvent(
            external_event_id=event["id"],
            event_type=event["type"],
            data=data,
        )
