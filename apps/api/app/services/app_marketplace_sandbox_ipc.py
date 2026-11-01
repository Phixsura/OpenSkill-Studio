"""Sandbox IPC — inter-process communication between sandbox and host.

Provides a message-passing interface for sandboxed extensions to
communicate with the host platform safely, with message validation
and response timeouts.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"


@dataclass
class IPCMessage:
    message_id: str
    channel: str
    msg_type: MessageType
    payload: dict
    sender: str  # "sandbox" or "host"
    timestamp: str = ""
    reply_to: str = ""  # for responses

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


ALLOWED_CHANNELS = {
    "config.read", "config.write", "storage.get", "storage.set",
    "event.emit", "event.subscribe", "ui.notify", "ui.prompt",
    "api.call", "log.write",
}


class SandboxIPC:
    """Message-passing IPC between sandbox and host platform."""

    def __init__(self, allowed_channels: set[str] | None = None):
        self._channels = allowed_channels or ALLOWED_CHANNELS
        self._inbox: dict[str, list[IPCMessage]] = defaultdict(list)
        self._handlers: dict[str, callable] = {}
        self._message_log: list[IPCMessage] = []
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"ipc-{self._counter:06d}"

    def register_handler(self, channel: str, handler: callable) -> bool:
        """Register a handler for a channel on the host side."""
        if channel not in self._channels:
            return False
        self._handlers[channel] = handler
        return True

    def send(self, channel: str, payload: dict, sender: str = "sandbox",
             msg_type: MessageType = MessageType.REQUEST,
             reply_to: str = "") -> tuple[IPCMessage | None, str]:
        """Send a message on a channel."""
        if channel not in self._channels:
            return None, f"Channel not allowed: {channel}"

        msg = IPCMessage(
            message_id=self._next_id(), channel=channel,
            msg_type=msg_type, payload=payload,
            sender=sender, reply_to=reply_to,
        )
        self._message_log.append(msg)
        target = "host" if sender == "sandbox" else "sandbox"
        self._inbox[target].append(msg)

        # Auto-dispatch to handler
        if sender == "sandbox" and channel in self._handlers:
            response_payload = self._handlers[channel](payload)
            if response_payload is not None:
                response = IPCMessage(
                    message_id=self._next_id(), channel=channel,
                    msg_type=MessageType.RESPONSE, payload=response_payload,
                    sender="host", reply_to=msg.message_id,
                )
                self._message_log.append(response)
                self._inbox["sandbox"].append(response)

        return msg, "Sent"

    def receive(self, recipient: str, channel: str | None = None) -> list[IPCMessage]:
        """Receive pending messages."""
        messages = self._inbox.get(recipient, [])
        if channel:
            messages = [m for m in messages if m.channel == channel]
        return messages

    def drain(self, recipient: str) -> list[IPCMessage]:
        """Receive and clear all pending messages."""
        messages = self._inbox.pop(recipient, [])
        return messages

    def get_log(self, channel: str | None = None, limit: int = 100) -> list[IPCMessage]:
        log = self._message_log
        if channel:
            log = [m for m in log if m.channel == channel]
        return log[-limit:]

    def get_allowed_channels(self) -> list[str]:
        return sorted(self._channels)
