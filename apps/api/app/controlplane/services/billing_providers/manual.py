"""Manual/offline billing (ADR-014 §6.2): enterprise contracts, bank
transfers. All remote operations are deliberate 409s — billing admins drive
invoices and payments through the platform endpoints instead."""

from app.controlplane.services.billing_providers.base import (
    BillingProviderBase,
    CheckoutSession,
    ParsedWebhookEvent,
)
from app.exceptions import AppError


def _manual_mode() -> AppError:
    return AppError(
        "MANUAL_BILLING_MODE",
        "This tenant uses manual billing — a platform billing admin manages "
        "invoices and payments directly",
        409,
    )


class ManualProvider(BillingProviderBase):
    key = "manual"

    async def create_customer(self, tenant) -> str:
        return f"manual_{tenant.id}"

    async def create_checkout_session(self, **kwargs) -> CheckoutSession:
        raise _manual_mode()

    async def change_subscription(self, external_ref, new_price_ref, seat_quantity) -> None:
        return None  # local-only state; nothing remote to sync

    async def cancel_subscription(self, external_ref, at_period_end) -> None:
        return None

    async def fetch_payment_status(self, external_ref) -> str:
        raise _manual_mode()

    def verify_webhook(self, headers, raw_body) -> ParsedWebhookEvent:
        raise _manual_mode()
