"""Stripe adapter — THIN wrapper (ADR-014 §6.2, user decision): parameter
assembly → SDK call → response mapping, zero logic branches. Unit tests
monkeypatch the stripe module; webhook signatures use the real
stripe.Webhook.construct_event with a fake secret.

Card data never touches the platform — only refs are stored.
"""

import structlog

from app.config import settings
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


class StripeProvider(BillingProviderBase):
    key = "stripe"

    async def create_customer(self, tenant) -> str:
        sdk = _stripe()
        customer = sdk.Customer.create(
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
            session = sdk.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": plan_price.external_price_ref, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=meta,
            )
        else:  # credit_topup | purchase — one-off payment
            session = sdk.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": currency.lower(),
                            "unit_amount": amount_minor,
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
        sub = sdk.Subscription.retrieve(external_ref)
        sdk.Subscription.modify(
            external_ref,
            items=[
                {
                    "id": sub["items"]["data"][0]["id"],
                    "price": new_price_ref,
                    "quantity": max(seat_quantity, 1),
                }
            ],
            proration_behavior="none",  # proration is computed platform-side
        )

    async def cancel_subscription(self, external_ref: str, at_period_end: bool) -> None:
        sdk = _stripe()
        if at_period_end:
            sdk.Subscription.modify(external_ref, cancel_at_period_end=True)
        else:
            sdk.Subscription.cancel(external_ref)

    async def fetch_payment_status(self, external_ref: str) -> str:
        sdk = _stripe()
        session = sdk.checkout.Session.retrieve(external_ref)
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
        return ParsedWebhookEvent(
            external_event_id=event["id"],
            event_type=event["type"],
            data=data,
        )
