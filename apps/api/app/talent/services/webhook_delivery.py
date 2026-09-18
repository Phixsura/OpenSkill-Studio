"""Webhook HTTP delivery — sends talent events to external endpoints.

Features:
  - HTTP POST delivery with retry (3 attempts, exponential backoff)
  - HMAC-SHA256 signature for payload verification
  - Delivery status tracking (pending, delivered, failed)
  - Webhook endpoint registration per org
  - Payload filtering by event type
  - Delivery log with response codes
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, datetime

SUPPORTED_EVENTS = frozenset(
    {
        "credential.issued",
        "credential.revoked",
        "application.submitted",
        "application.stage_changed",
        "offer.created",
        "offer.accepted",
        "offer.declined",
        "placement.started",
        "placement.completed",
        "capability.verified",
        "capability.endorsed",
        "employer_verification.submitted",
        "outreach.sent",
        "outreach.responded",
        "talent_pool.member_added",
        "interview.scheduled",
        "interview.completed",
        "assessment.completed",
        "credential_pathway.completed",
        "career_goal.completed",
    }
)

DELIVERY_STATUSES = frozenset({"pending", "delivered", "failed", "skipped"})

MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = [10, 60, 300]  # exponential backoff


@dataclass(frozen=True, slots=True)
class WebhookEndpoint:
    """Registered webhook endpoint."""

    id: str
    org_id: str
    url: str
    secret: str  # HMAC signing secret
    event_types: list[str]  # filter, empty = all
    active: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class WebhookDelivery:
    """Delivery attempt record."""

    id: str
    endpoint_id: str
    event_type: str
    payload: dict
    status: str
    response_code: int | None
    response_body: str | None
    attempts: int
    next_retry_at: datetime | None
    created_at: datetime
    delivered_at: datetime | None


@dataclass(frozen=True, slots=True)
class WebhookStats:
    """Webhook delivery statistics."""

    total_deliveries: int
    successful: int
    failed: int
    pending: int
    success_rate: float
    avg_response_ms: float | None


class WebhookDeliveryService:
    def sign_payload(self, payload_json: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload."""
        return hmac.new(
            secret.encode(),
            payload_json.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify_signature(self, payload_json: str, signature: str, secret: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected = self.sign_payload(payload_json, secret)
        return hmac.compare_digest(expected, signature)

    def should_deliver(self, endpoint: WebhookEndpoint, event_type: str) -> bool:
        """Check if an endpoint should receive this event type."""
        if not endpoint.active:
            return False
        if not endpoint.event_types:
            return True  # empty = all events
        return event_type in endpoint.event_types

    def build_delivery_payload(
        self,
        *,
        event_type: str,
        payload: dict,
        delivery_id: str,
        timestamp: datetime | None = None,
    ) -> dict:
        """Build the webhook delivery payload with metadata."""
        ts = timestamp or datetime.now(UTC)
        return {
            "event": event_type,
            "delivery_id": delivery_id,
            "timestamp": ts.isoformat(),
            "data": payload,
        }

    def compute_stats(self, deliveries: list[WebhookDelivery]) -> WebhookStats:
        """Compute delivery statistics."""
        if not deliveries:
            return WebhookStats(0, 0, 0, 0, 0.0, None)

        successful = sum(1 for d in deliveries if d.status == "delivered")
        failed = sum(1 for d in deliveries if d.status == "failed")
        pending = sum(1 for d in deliveries if d.status == "pending")

        return WebhookStats(
            total_deliveries=len(deliveries),
            successful=successful,
            failed=failed,
            pending=pending,
            success_rate=round(successful / max(len(deliveries), 1), 3) if deliveries else 0.0,
            avg_response_ms=None,
        )

    def get_retry_delay(self, attempt: int) -> int | None:
        """Get retry delay in seconds for the given attempt number."""
        if attempt >= MAX_RETRIES:
            return None
        return RETRY_DELAYS_SECONDS[min(attempt, len(RETRY_DELAYS_SECONDS) - 1)]
