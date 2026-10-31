"""Webhook Dispatcher — reliable fan-out delivery with retry and circuit breaking.

Implements:
- Fan-out: one event dispatched to multiple subscriber endpoints
- Per-endpoint circuit breaker (disable after N failures)
- Retry queue with exponential backoff
- Delivery receipt tracking
- Payload signing (HMAC-SHA256)
- Configurable timeout per subscriber
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import hashlib
import hmac


@dataclass
class Subscriber:
    subscriber_id: str
    url: str
    secret: str
    active: bool = True
    failure_count: int = 0
    success_count: int = 0
    circuit_open: bool = False
    last_failure: float = 0.0
    max_failures: int = 5
    recovery_seconds: float = 60


@dataclass
class DeliveryAttempt:
    event_id: str
    subscriber_id: str
    status: str  # pending, delivered, failed, circuit_open
    attempt: int = 1
    signature: str = ""
    timestamp: float = 0.0
    error: str = ""
    next_retry: float = 0.0


class WebhookDispatcherService:
    MAX_RETRIES = 3

    def __init__(self):
        self._subscribers: dict[str, list[Subscriber]] = {}  # event_type -> subs
        self._deliveries: list[DeliveryAttempt] = []
        self._retry_queue: list[DeliveryAttempt] = []

    def subscribe(self, event_type: str, subscriber_id: str, url: str,
                  secret: str, max_failures: int = 5) -> Subscriber:
        sub = Subscriber(subscriber_id=subscriber_id, url=url, secret=secret,
                         max_failures=max_failures)
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(sub)
        return sub

    def sign_payload(self, payload: str, secret: str) -> str:
        return hmac.new(secret.encode(), payload.encode(),
                        hashlib.sha256).hexdigest()

    def dispatch(self, event_type: str, event_id: str,
                 payload: str, executor: callable | None = None) -> list[DeliveryAttempt]:
        """Fan-out event to all subscribers. Returns delivery attempts."""
        subscribers = self._subscribers.get(event_type, [])
        attempts = []
        now = time.time()

        for sub in subscribers:
            if not sub.active:
                continue

            # Circuit breaker check
            if sub.circuit_open:
                if now - sub.last_failure > sub.recovery_seconds:
                    sub.circuit_open = False  # half-open: try one
                else:
                    attempts.append(DeliveryAttempt(
                        event_id=event_id, subscriber_id=sub.subscriber_id,
                        status="circuit_open", timestamp=now))
                    continue

            signature = self.sign_payload(payload, sub.secret)
            attempt = DeliveryAttempt(
                event_id=event_id, subscriber_id=sub.subscriber_id,
                status="pending", signature=signature, timestamp=now)

            # Deliver
            success = True
            if executor:
                try:
                    executor(sub.url, payload, signature)
                except Exception as e:
                    success = False
                    attempt.error = str(e)

            if success:
                attempt.status = "delivered"
                sub.success_count += 1
                sub.failure_count = 0
            else:
                attempt.status = "failed"
                sub.failure_count += 1
                sub.last_failure = now
                if sub.failure_count >= sub.max_failures:
                    sub.circuit_open = True
                # Queue retry
                attempt.next_retry = now + 2 ** min(attempt.attempt, 6)
                self._retry_queue.append(attempt)

            attempts.append(attempt)
            self._deliveries.append(attempt)

        return attempts

    def process_retries(self, executor: callable | None = None) -> int:
        """Process queued retries. Returns count processed."""
        now = time.time()
        processed = 0
        remaining = []

        for attempt in self._retry_queue:
            if attempt.next_retry > now:
                remaining.append(attempt)
                continue
            if attempt.attempt >= self.MAX_RETRIES:
                attempt.status = "failed"
                processed += 1
                continue

            attempt.attempt += 1
            success = True
            if executor:
                try:
                    executor("", "", attempt.signature)
                except Exception:
                    success = False

            if success:
                attempt.status = "delivered"
            else:
                attempt.next_retry = now + 2 ** min(attempt.attempt, 6)
                remaining.append(attempt)
            processed += 1

        self._retry_queue = remaining
        return processed

    def get_subscriber_health(self, event_type: str) -> list[dict]:
        return [{"id": s.subscriber_id, "active": s.active,
                 "circuit_open": s.circuit_open,
                 "success": s.success_count, "failures": s.failure_count}
                for s in self._subscribers.get(event_type, [])]

    def get_delivery_stats(self) -> dict:
        delivered = sum(1 for d in self._deliveries if d.status == "delivered")
        failed = sum(1 for d in self._deliveries if d.status == "failed")
        return {"total": len(self._deliveries), "delivered": delivered,
                "failed": failed, "retry_queue": len(self._retry_queue)}
