"""Billing provider adapters (ADR-014 §6.2).

Provider-neutral by design (issue §19): the domain never talks to Stripe
directly — it talks to BillingProviderBase. Manual (offline), Mock
(dev/tests, HMAC-forgeable webhooks) and Stripe (thin SDK wrapper) ship.
"""

from app.controlplane.services.billing_providers.base import (
    BillingProviderBase,
    ParsedWebhookEvent,
)
from app.controlplane.services.billing_providers.manual import ManualProvider
from app.controlplane.services.billing_providers.mock import MockProvider
from app.controlplane.services.billing_providers.stripe import StripeProvider

_PROVIDERS: dict[str, BillingProviderBase] = {
    "manual": ManualProvider(),
    "mock": MockProvider(),
    "stripe": StripeProvider(),
}


def get_billing_provider(key: str) -> BillingProviderBase | None:
    return _PROVIDERS.get(key)


__all__ = [
    "BillingProviderBase",
    "ParsedWebhookEvent",
    "get_billing_provider",
]
