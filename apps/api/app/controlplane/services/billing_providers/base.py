"""Billing provider contract (ADR-014 §6.2). Never store raw card data."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedWebhookEvent:
    external_event_id: str
    event_type: str
    data: dict


@dataclass(frozen=True)
class CheckoutSession:
    url: str
    session_ref: str


class BillingProviderBase(ABC):
    key: str = ""

    @abstractmethod
    async def create_customer(self, tenant) -> str:
        """Create/resolve the provider-side customer; returns external ref."""

    @abstractmethod
    async def create_checkout_session(
        self,
        *,
        tenant,
        kind: str,  # "subscription" | "credit_topup" | "purchase"
        plan_price=None,
        amount_minor: int | None = None,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> CheckoutSession:
        """Start a hosted checkout; the webhook completes the flow."""

    @abstractmethod
    async def change_subscription(
        self, external_ref: str, new_price_ref: str, seat_quantity: int
    ) -> None: ...

    @abstractmethod
    async def cancel_subscription(self, external_ref: str, at_period_end: bool) -> None: ...

    @abstractmethod
    async def fetch_payment_status(self, external_ref: str) -> str: ...

    @abstractmethod
    def verify_webhook(self, headers: dict, raw_body: bytes) -> ParsedWebhookEvent:
        """Verify signature and parse. Raises on invalid signature."""
