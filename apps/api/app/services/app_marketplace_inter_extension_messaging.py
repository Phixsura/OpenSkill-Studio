"""Inter-Extension Messaging — secure communication between extensions.

Enables extensions to exchange messages through typed channels with
access control, ensuring only authorized extensions can communicate.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ExtMessage:
    message_id: str
    channel: str
    sender_id: str
    payload: dict
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class Channel:
    channel_id: str
    name: str
    owner_id: str
    allowed_senders: set[str] = field(default_factory=set)
    allowed_receivers: set[str] = field(default_factory=set)


class InterExtensionMessaging:
    """Manages secure message passing between extensions."""

    def __init__(self):
        self._channels: dict[str, Channel] = {}
        self._queues: dict[str, list[ExtMessage]] = defaultdict(list)  # channel -> messages
        self._counter = 0

    def create_channel(self, channel_id: str, name: str, owner_id: str,
                       senders: list[str] | None = None,
                       receivers: list[str] | None = None) -> Channel:
        ch = Channel(
            channel_id=channel_id, name=name, owner_id=owner_id,
            allowed_senders=set(senders or [owner_id]),
            allowed_receivers=set(receivers or []),
        )
        self._channels[channel_id] = ch
        return ch

    def grant_access(self, channel_id: str, requester_id: str, extension_id: str,
                     can_send: bool = False, can_receive: bool = False) -> bool:
        ch = self._channels.get(channel_id)
        if not ch or requester_id != ch.owner_id:
            return False
        if can_send:
            ch.allowed_senders.add(extension_id)
        if can_receive:
            ch.allowed_receivers.add(extension_id)
        return True

    def send(self, channel_id: str, sender_id: str, payload: dict) -> tuple[ExtMessage | None, str]:
        ch = self._channels.get(channel_id)
        if not ch or requester_id != ch.owner_id:
            return None, "Channel not found"
        if sender_id not in ch.allowed_senders:
            return None, "Sender not authorized"

        self._counter += 1
        msg = ExtMessage(
            message_id=f"msg-{self._counter}",
            channel=channel_id, sender_id=sender_id, payload=payload,
        )
        self._queues[channel_id].append(msg)
        return msg, "Sent"

    def receive(self, channel_id: str, receiver_id: str,
                limit: int = 50) -> tuple[list[ExtMessage], str]:
        ch = self._channels.get(channel_id)
        if not ch or requester_id != ch.owner_id:
            return [], "Channel not found"
        if receiver_id not in ch.allowed_receivers and receiver_id != ch.owner_id:
            return [], "Receiver not authorized"
        return self._queues.get(channel_id, [])[-limit:], "OK"

    def consume(self, channel_id: str, receiver_id: str,
                count: int = 1) -> list[ExtMessage]:
        """Receive and remove messages from queue."""
        ch = self._channels.get(channel_id)
        if not ch or (receiver_id not in ch.allowed_receivers and receiver_id != ch.owner_id):
            return []
        queue = self._queues.get(channel_id, [])
        consumed = queue[:count]
        self._queues[channel_id] = queue[count:]
        return consumed

    def get_channel(self, channel_id: str) -> Channel | None:
        return self._channels.get(channel_id)

    def list_channels(self, extension_id: str) -> list[Channel]:
        """List channels where extension is owner, sender, or receiver."""
        return [
            ch for ch in self._channels.values()
            if extension_id == ch.owner_id
            or extension_id in ch.allowed_senders
            or extension_id in ch.allowed_receivers
        ]

    def get_queue_depth(self, channel_id: str) -> int:
        return len(self._queues.get(channel_id, []))
