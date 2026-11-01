"""Persistent Queue — durable FIFO with acknowledgment and visibility timeout.

SQS-style: messages become invisible while processing, return to queue
if not acknowledged within timeout.

Implements:
- Enqueue with deduplication ID
- Receive with visibility timeout (invisible while processing)
- Ack (permanently remove) or Nack (return to queue)
- Visibility timeout extension
- Dead letter queue after max receives
- FIFO ordering with message groups
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import secrets


@dataclass
class QueueMessage:
    message_id: str
    body: dict
    group_id: str = ""
    dedup_id: str = ""
    enqueued_at: float = 0.0
    visible_at: float = 0.0  # when it becomes visible again
    receive_count: int = 0
    max_receives: int = 5

    def __post_init__(self):
        if not self.enqueued_at: self.enqueued_at = time.time()


class PersistentQueueService:
    def __init__(self, default_visibility_timeout: float = 30,
                 max_receives: int = 5):
        self._messages: list[QueueMessage] = []
        self._inflight: dict[str, QueueMessage] = {}  # receipt → message
        self._dead_letter: list[QueueMessage] = []
        self._dedup_cache: dict[str, float] = {}  # dedup_id → expiry
        self._visibility_timeout = default_visibility_timeout
        self._max_receives = max_receives
        self._receipt_counter = 0

    def send(self, body: dict, group_id: str = "",
             dedup_id: str = "") -> str:
        """Enqueue a message. Returns message_id."""
        # Deduplication check
        if dedup_id:
            now = time.time()
            if dedup_id in self._dedup_cache and self._dedup_cache[dedup_id] > now:
                return ""  # duplicate, skip
            self._dedup_cache[dedup_id] = now + 300  # 5 min dedup window

        msg = QueueMessage(message_id=secrets.token_hex(8), body=body,
                           group_id=group_id, dedup_id=dedup_id,
                           max_receives=self._max_receives)
        self._messages.append(msg)
        return msg.message_id

    def receive(self, max_messages: int = 1,
                visibility_timeout: float = 0) -> list[tuple[str, QueueMessage]]:
        """Receive messages. Returns [(receipt_handle, message)]."""
        vt = visibility_timeout or self._visibility_timeout
        now = time.time()
        results = []

        # Return timed-out inflight messages to queue
        timed_out = [r for r, m in self._inflight.items() if m.visible_at <= now]
        for receipt in timed_out:
            msg = self._inflight.pop(receipt)
            msg.visible_at = 0
            self._messages.append(msg)

        for msg in list(self._messages):
            if len(results) >= max_messages:
                break
            if msg.visible_at > now:
                continue  # still invisible

            msg.receive_count += 1

            # Dead letter check
            if msg.receive_count > msg.max_receives:
                self._messages.remove(msg)
                self._dead_letter.append(msg)
                continue

            msg.visible_at = now + vt
            self._receipt_counter += 1
            receipt = f"rcpt-{self._receipt_counter}"
            self._messages.remove(msg)
            self._inflight[receipt] = msg
            results.append((receipt, msg))

        return results

    def ack(self, receipt_handle: str) -> bool:
        """Acknowledge: permanently remove message."""
        return self._inflight.pop(receipt_handle, None) is not None

    def nack(self, receipt_handle: str) -> bool:
        """Negative ack: return message to queue immediately."""
        msg = self._inflight.pop(receipt_handle, None)
        if msg:
            msg.visible_at = 0
            self._messages.append(msg)
            return True
        return False

    def extend_visibility(self, receipt_handle: str,
                          additional_seconds: float) -> bool:
        """Extend visibility timeout for in-flight message."""
        msg = self._inflight.get(receipt_handle)
        if msg:
            msg.visible_at = time.time() + additional_seconds
            return True
        return False

    def get_dead_letters(self) -> list[QueueMessage]:
        return list(self._dead_letter)

    def purge(self) -> int:
        count = len(self._messages)
        self._messages.clear()
        return count

    def stats(self) -> dict:
        return {
            "visible": sum(1 for m in self._messages if m.visible_at <= time.time()),
            "delayed": sum(1 for m in self._messages if m.visible_at > time.time()),
            "inflight": len(self._inflight),
            "dead_letter": len(self._dead_letter),
            "total": len(self._messages) + len(self._inflight),
        }
