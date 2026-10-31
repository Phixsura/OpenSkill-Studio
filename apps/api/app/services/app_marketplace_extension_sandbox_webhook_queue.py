"""Sandbox Webhook Queue — priority queue for outbound webhook delivery.

Manages webhook delivery with priority, retry scheduling, payload
compression detection, delivery confirmation, and queue depth monitoring.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class WebhookPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


PRIORITY_WEIGHT = {WebhookPriority.LOW: 0, WebhookPriority.NORMAL: 1,
                   WebhookPriority.HIGH: 2, WebhookPriority.CRITICAL: 3}


class DeliveryState(str, Enum):
    QUEUED = "queued"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class QueuedWebhook:
    webhook_id: str
    sandbox_id: str
    url: str
    payload: str
    priority: WebhookPriority = WebhookPriority.NORMAL
    state: DeliveryState = DeliveryState.QUEUED
    attempt: int = 0
    max_attempts: int = 5
    payload_size: int = 0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        self.payload_size = len(self.payload.encode())


class SandboxWebhookQueueService:
    """Priority webhook delivery queue with retry."""

    MAX_QUEUE_SIZE = 1000
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB

    def __init__(self):
        self._queues: dict[str, list[QueuedWebhook]] = defaultdict(list)

    def enqueue(self, sandbox_id: str, url: str, payload: str,
                priority: WebhookPriority = WebhookPriority.NORMAL,
                max_attempts: int = 5) -> QueuedWebhook | dict:
        if len(payload.encode()) > self.MAX_PAYLOAD_SIZE:
            return {"error": "Payload too large"}
        queue = self._queues[sandbox_id]
        if len([w for w in queue if w.state in (DeliveryState.QUEUED, DeliveryState.RETRY)]) >= self.MAX_QUEUE_SIZE:
            return {"error": "Queue full"}

        webhook = QueuedWebhook(
            webhook_id=f"wq_{secrets.token_urlsafe(8)}",
            sandbox_id=sandbox_id, url=url, payload=payload,
            priority=priority, max_attempts=max_attempts,
        )
        queue.append(webhook)
        return webhook

    def dequeue(self, sandbox_id: str) -> QueuedWebhook | None:
        queue = self._queues.get(sandbox_id, [])
        pending = [w for w in queue if w.state in (DeliveryState.QUEUED, DeliveryState.RETRY)]
        if not pending:
            return None
        pending.sort(key=lambda w: PRIORITY_WEIGHT.get(w.priority, 0), reverse=True)
        best = pending[0]
        best.state = DeliveryState.DELIVERING
        best.attempt += 1
        return best

    def confirm(self, webhook_id: str, sandbox_id: str) -> bool:
        for w in self._queues.get(sandbox_id, []):
            if w.webhook_id == webhook_id and w.state == DeliveryState.DELIVERING:
                w.state = DeliveryState.DELIVERED
                return True
        return False

    def fail(self, webhook_id: str, sandbox_id: str) -> DeliveryState:
        for w in self._queues.get(sandbox_id, []):
            if w.webhook_id == webhook_id:
                if w.attempt >= w.max_attempts:
                    w.state = DeliveryState.FAILED
                else:
                    w.state = DeliveryState.RETRY
                return w.state
        return DeliveryState.FAILED

    def get_depth(self, sandbox_id: str) -> dict:
        queue = self._queues.get(sandbox_id, [])
        by_state: dict[str, int] = defaultdict(int)
        for w in queue:
            by_state[w.state.value] += 1
        pending = by_state.get("queued", 0) + by_state.get("retry", 0)
        return {"total": len(queue), "pending": pending, "by_state": dict(by_state)}

    def get_by_priority(self, sandbox_id: str) -> dict[str, int]:
        queue = self._queues.get(sandbox_id, [])
        pending = [w for w in queue if w.state in (DeliveryState.QUEUED, DeliveryState.RETRY)]
        by_pri: dict[str, int] = defaultdict(int)
        for w in pending:
            by_pri[w.priority.value] += 1
        return dict(by_pri)
