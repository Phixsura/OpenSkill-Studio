"""Inter-Service Communication — secure message passing between extensions.

Enables extensions to communicate via typed messages with routing,
access control, request/response patterns, and message queuing.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    BROADCAST = "broadcast"


class DeliveryStatus(str, Enum):
    QUEUED = "queued"
    DELIVERED = "delivered"
    EXPIRED = "expired"
    REJECTED = "rejected"


@dataclass
class ServiceMessage:
    message_id: str
    from_extension: str
    to_extension: str
    message_type: MessageType
    channel: str
    payload: dict = field(default_factory=dict)
    status: DeliveryStatus = DeliveryStatus.QUEUED
    correlation_id: str = ""  # links request/response
    ttl_seconds: int = 300
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class InterServiceCommService:
    """Manages secure inter-extension messaging."""

    def __init__(self):
        self._queues: dict[str, list[ServiceMessage]] = defaultdict(list)
        self._access: dict[str, set[str]] = defaultdict(set)  # ext_id -> allowed_channels
        self._subscriptions: dict[str, set[str]] = defaultdict(set)  # channel -> ext_ids

    def grant_access(self, extension_id: str, channels: list[str]) -> None:
        self._access[extension_id].update(channels)

    def subscribe(self, extension_id: str, channel: str) -> bool:
        if channel not in self._access.get(extension_id, set()):
            return False
        self._subscriptions[channel].add(extension_id)
        return True

    def send(self, from_ext: str, to_ext: str, channel: str,
             payload: dict, message_type: MessageType = MessageType.REQUEST,
             correlation_id: str = "", ttl: int = 300) -> ServiceMessage | dict:
        if channel not in self._access.get(from_ext, set()):
            return {"error": f"No access to channel: {channel}"}

        msg = ServiceMessage(
            message_id=f"msg_{secrets.token_urlsafe(10)}",
            from_extension=from_ext, to_extension=to_ext,
            message_type=message_type, channel=channel,
            payload=payload, correlation_id=correlation_id,
            ttl_seconds=ttl,
        )
        self._queues[to_ext].append(msg)
        msg.status = DeliveryStatus.DELIVERED
        return msg

    def broadcast(self, from_ext: str, channel: str,
                  payload: dict) -> list[ServiceMessage]:
        if channel not in self._access.get(from_ext, set()):
            return []
        subscribers = self._subscriptions.get(channel, set())
        messages = []
        for ext_id in subscribers:
            if ext_id != from_ext:
                msg = self.send(from_ext, ext_id, channel, payload,
                                MessageType.BROADCAST)
                if isinstance(msg, ServiceMessage):
                    messages.append(msg)
        return messages

    def receive(self, extension_id: str, channel: str | None = None,
                limit: int = 50) -> list[ServiceMessage]:
        now = time.time()
        queue = self._queues.get(extension_id, [])
        # Filter expired
        valid = [m for m in queue if now - m.created_at < m.ttl_seconds]
        if channel:
            valid = [m for m in valid if m.channel == channel]
        self._queues[extension_id] = [m for m in queue if now - m.created_at < m.ttl_seconds]
        return valid[-limit:]

    def reply(self, from_ext: str, original_msg_id: str,
              payload: dict) -> ServiceMessage | dict:
        # Find original message to get routing info
        for ext_id, queue in self._queues.items():
            for msg in queue:
                if msg.message_id == original_msg_id:
                    return self.send(
                        from_ext, msg.from_extension, msg.channel,
                        payload, MessageType.RESPONSE,
                        correlation_id=msg.message_id,
                    )
        return {"error": "Original message not found"}

    def get_stats(self, extension_id: str) -> dict:
        sent = sum(1 for q in self._queues.values()
                   for m in q if m.from_extension == extension_id)
        received = len(self._queues.get(extension_id, []))
        return {"sent": sent, "received": received,
                "channels": sorted(self._access.get(extension_id, set()))}
