"""Webhook Retry Queue — exponential backoff delivery with dead-letter handling.

Implements a reliable webhook delivery pipeline:
- Exponential backoff: 10s, 30s, 90s, 270s, 810s (5 attempts)
- Jitter: ±20% to prevent thundering herd
- Dead-letter queue after max retries exhausted
- Delivery receipt tracking with latency metrics
- Circuit breaker per endpoint (pause after 10 consecutive failures)
"""

import hashlib
import random
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"
    CANCELLED = "cancelled"


@dataclass
class DeliveryAttempt:
    """Record of a single webhook delivery attempt."""

    attempt_number: int
    started_at: datetime
    completed_at: datetime | None = None
    status_code: int | None = None
    latency_ms: float | None = None
    error: str | None = None
    success: bool = False


@dataclass
class WebhookTask:
    """A webhook delivery task with retry state."""

    task_id: str
    webhook_url: str
    payload: dict
    event_type: str
    secret: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempt_count: int = 0
    max_attempts: int = 5
    next_retry_at: datetime | None = None
    attempts: list[DeliveryAttempt] = field(default_factory=list)
    dead_lettered_at: datetime | None = None
    idempotency_key: str | None = None


# ── Backoff configuration ────────────────────────────────

BASE_DELAY_SECONDS = 10
BACKOFF_MULTIPLIER = 3
JITTER_FACTOR = 0.2
MAX_ATTEMPTS = 5
CIRCUIT_BREAKER_THRESHOLD = 10
CIRCUIT_BREAKER_COOLDOWN_SECONDS = 300


def compute_backoff(attempt: int, base: float = BASE_DELAY_SECONDS,
                    multiplier: float = BACKOFF_MULTIPLIER,
                    jitter: float = JITTER_FACTOR) -> float:
    """Compute exponential backoff delay with jitter.

    attempt 1 → ~10s, 2 → ~30s, 3 → ~90s, 4 → ~270s, 5 → ~810s
    Jitter adds ±20% randomness to prevent thundering herd.
    """
    delay = base * (multiplier ** (attempt - 1))
    jitter_range = delay * jitter
    delay += random.uniform(-jitter_range, jitter_range)
    return max(1.0, delay)


def compute_signature(payload_bytes: bytes, secret: str) -> str:
    """HMAC-SHA256 signature for webhook payload verification."""
    import hmac
    return "sha256=" + hmac.new(
        secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()


# ── Circuit breaker ──────────────────────────────────────


@dataclass
class EndpointCircuitBreaker:
    """Per-endpoint circuit breaker to pause deliveries after repeated failures."""

    endpoint_url: str
    consecutive_failures: int = 0
    last_failure_at: datetime | None = None
    opened_at: datetime | None = None
    is_open: bool = False

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False
        self.opened_at = None

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.last_failure_at = datetime.now(UTC)
        if self.consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self.is_open = True
            self.opened_at = datetime.now(UTC)
            log.warning(
                "webhook.circuit_breaker_opened",
                endpoint=self.endpoint_url,
                failures=self.consecutive_failures,
            )

    def should_allow(self) -> bool:
        if not self.is_open:
            return True
        # Allow half-open probe after cooldown
        if self.opened_at and (
            datetime.now(UTC) - self.opened_at
        ).total_seconds() >= CIRCUIT_BREAKER_COOLDOWN_SECONDS:
            return True
        return False


# ── Retry queue ──────────────────────────────────────────


class WebhookRetryQueue:
    """In-memory webhook retry queue with backoff and dead-letter support.

    Production deployments should back this with Redis/Postgres for durability.
    This implementation provides the core algorithm and is suitable for
    single-process or test environments.
    """

    def __init__(self, max_attempts: int = MAX_ATTEMPTS):
        self.max_attempts = max_attempts
        self._queue: dict[str, WebhookTask] = {}
        self._dead_letter: dict[str, WebhookTask] = {}
        self._circuit_breakers: dict[str, EndpointCircuitBreaker] = {}
        self._delivery_stats = DeliveryStats()

    def enqueue(self, task: WebhookTask) -> WebhookTask:
        """Add a webhook task to the retry queue."""
        task.max_attempts = self.max_attempts
        task.status = DeliveryStatus.PENDING
        self._queue[task.task_id] = task
        self._delivery_stats.total_enqueued += 1
        log.info(
            "webhook.enqueued",
            task_id=task.task_id,
            event_type=task.event_type,
            url=task.webhook_url,
        )
        return task

    def get_pending(self, now: datetime | None = None) -> list[WebhookTask]:
        """Return tasks ready for delivery (pending or retry-ready)."""
        now = now or datetime.now(UTC)
        ready = []
        for task in self._queue.values():
            if task.status == DeliveryStatus.PENDING:
                ready.append(task)
            elif task.status == DeliveryStatus.RETRYING:
                if task.next_retry_at and task.next_retry_at <= now:
                    ready.append(task)
        return sorted(ready, key=lambda t: t.created_at)

    def record_attempt(self, task_id: str, status_code: int | None,
                       latency_ms: float, error: str | None = None) -> WebhookTask:
        """Record a delivery attempt result and compute next action."""
        task = self._queue.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found in queue")

        task.attempt_count += 1
        success = status_code is not None and 200 <= status_code < 300

        attempt = DeliveryAttempt(
            attempt_number=task.attempt_count,
            started_at=datetime.now(UTC) - timedelta(milliseconds=latency_ms),
            completed_at=datetime.now(UTC),
            status_code=status_code,
            latency_ms=latency_ms,
            error=error,
            success=success,
        )
        task.attempts.append(attempt)

        # Update circuit breaker
        cb = self._get_circuit_breaker(task.webhook_url)

        if success:
            task.status = DeliveryStatus.DELIVERED
            cb.record_success()
            self._delivery_stats.total_delivered += 1
            self._delivery_stats.total_latency_ms += latency_ms
            log.info(
                "webhook.delivered",
                task_id=task_id,
                attempt=task.attempt_count,
                status_code=status_code,
                latency_ms=round(latency_ms, 1),
            )
        elif task.attempt_count >= task.max_attempts:
            # Exhausted retries → dead-letter
            task.status = DeliveryStatus.DEAD_LETTER
            task.dead_lettered_at = datetime.now(UTC)
            self._dead_letter[task_id] = task
            del self._queue[task_id]
            cb.record_failure()
            self._delivery_stats.total_dead_lettered += 1
            log.warning(
                "webhook.dead_lettered",
                task_id=task_id,
                attempts=task.attempt_count,
                url=task.webhook_url,
            )
        else:
            # Schedule retry
            delay = compute_backoff(task.attempt_count)
            task.status = DeliveryStatus.RETRYING
            task.next_retry_at = datetime.now(UTC) + timedelta(seconds=delay)
            cb.record_failure()
            self._delivery_stats.total_retries += 1
            log.info(
                "webhook.retry_scheduled",
                task_id=task_id,
                attempt=task.attempt_count,
                next_retry_seconds=round(delay, 1),
            )

        return task

    def cancel(self, task_id: str) -> WebhookTask | None:
        """Cancel a pending/retrying task."""
        task = self._queue.get(task_id)
        if task and task.status in (DeliveryStatus.PENDING, DeliveryStatus.RETRYING):
            task.status = DeliveryStatus.CANCELLED
            del self._queue[task_id]
            return task
        return None

    def get_dead_letter_tasks(self) -> list[WebhookTask]:
        """Return all dead-lettered tasks."""
        return list(self._dead_letter.values())

    def replay_dead_letter(self, task_id: str) -> WebhookTask | None:
        """Move a dead-lettered task back to the queue for retry."""
        task = self._dead_letter.pop(task_id, None)
        if task is None:
            return None
        task.status = DeliveryStatus.PENDING
        task.attempt_count = 0
        task.attempts = []
        task.dead_lettered_at = None
        task.next_retry_at = None
        self._queue[task_id] = task
        log.info("webhook.dead_letter_replayed", task_id=task_id)
        return task

    def is_circuit_open(self, url: str) -> bool:
        """Check if the circuit breaker for an endpoint is open."""
        cb = self._circuit_breakers.get(url)
        return cb is not None and cb.is_open and not cb.should_allow()

    def get_stats(self) -> "DeliveryStats":
        return self._delivery_stats

    def queue_size(self) -> int:
        return len(self._queue)

    def dead_letter_size(self) -> int:
        return len(self._dead_letter)

    def _get_circuit_breaker(self, url: str) -> EndpointCircuitBreaker:
        if url not in self._circuit_breakers:
            self._circuit_breakers[url] = EndpointCircuitBreaker(endpoint_url=url)
        return self._circuit_breakers[url]


@dataclass
class DeliveryStats:
    """Aggregate delivery statistics."""

    total_enqueued: int = 0
    total_delivered: int = 0
    total_retries: int = 0
    total_dead_lettered: int = 0
    total_latency_ms: float = 0.0

    @property
    def delivery_rate(self) -> float:
        """Fraction of enqueued tasks successfully delivered."""
        return self.total_delivered / self.total_enqueued if self.total_enqueued > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.total_delivered if self.total_delivered > 0 else 0.0
