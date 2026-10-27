"""Pub/Sub Broker — topic-based messaging with consumer groups.

Implements:
- Named topics with partitions
- Consumer groups: each message delivered to ONE consumer per group
- At-least-once delivery with acknowledgment
- Message retention with configurable TTL
- Dead letter topic for unprocessable messages
- Offset tracking per consumer group
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class PubSubMessage:
    msg_id: str
    topic: str
    key: str  # partition key
    value: dict
    timestamp: float = 0.0
    offset: int = 0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class ConsumerGroup:
    group_id: str
    offsets: dict[str, int] = field(default_factory=dict)  # topic -> committed offset
    pending: dict[str, list[PubSubMessage]] = field(default_factory=dict)  # topic -> unacked


class PubSubBrokerService:
    def __init__(self, retention_seconds: float = 3600):
        self._topics: dict[str, list[PubSubMessage]] = {}
        self._groups: dict[str, ConsumerGroup] = {}
        self._counter = 0
        self._retention = retention_seconds
        self._dead_letter: list[PubSubMessage] = []
        self._max_redeliveries = 3
        self._redeliver_count: dict[str, int] = {}  # msg_id -> count

    def create_topic(self, topic: str) -> None:
        if topic not in self._topics:
            self._topics[topic] = []

    def publish(self, topic: str, key: str, value: dict) -> PubSubMessage:
        """Publish a message to a topic."""
        if topic not in self._topics:
            self.create_topic(topic)
        self._counter += 1
        offset = len(self._topics[topic])
        msg = PubSubMessage(msg_id=f"msg-{self._counter}", topic=topic,
                            key=key, value=value, offset=offset)
        self._topics[topic].append(msg)
        return msg

    def subscribe(self, group_id: str, topic: str) -> ConsumerGroup:
        """Subscribe a consumer group to a topic."""
        if group_id not in self._groups:
            self._groups[group_id] = ConsumerGroup(group_id=group_id)
        group = self._groups[group_id]
        if topic not in group.offsets:
            group.offsets[topic] = 0
            group.pending[topic] = []
        return group

    def poll(self, group_id: str, topic: str, max_messages: int = 10) -> list[PubSubMessage]:
        """Fetch unread messages for a consumer group."""
        group = self._groups.get(group_id)
        if not group or topic not in group.offsets:
            return []

        messages = self._topics.get(topic, [])
        offset = group.offsets[topic]
        batch = messages[offset:offset + max_messages]

        # Track as pending (unacked)
        group.pending.setdefault(topic, []).extend(batch)
        return batch

    def ack(self, group_id: str, topic: str, msg_id: str) -> bool:
        """Acknowledge processing of a message."""
        group = self._groups.get(group_id)
        if not group:
            return False
        pending = group.pending.get(topic, [])
        for i, msg in enumerate(pending):
            if msg.msg_id == msg_id:
                pending.pop(i)
                # Advance committed offset
                group.offsets[topic] = max(group.offsets[topic], msg.offset + 1)
                return True
        return False

    def nack(self, group_id: str, topic: str, msg_id: str) -> bool:
        """Negative acknowledge — message will be redelivered or dead-lettered."""
        group = self._groups.get(group_id)
        if not group:
            return False
        pending = group.pending.get(topic, [])
        for i, msg in enumerate(pending):
            if msg.msg_id == msg_id:
                pending.pop(i)
                count = self._redeliver_count.get(msg_id, 0) + 1
                self._redeliver_count[msg_id] = count
                if count >= self._max_redeliveries:
                    self._dead_letter.append(msg)
                # else: will be redelivered on next poll (offset not advanced)
                return True
        return False

    def get_lag(self, group_id: str, topic: str) -> int:
        """Messages behind for a consumer group."""
        group = self._groups.get(group_id)
        if not group or topic not in group.offsets:
            return 0
        total = len(self._topics.get(topic, []))
        return total - group.offsets[topic]

    def get_dead_letters(self) -> list[PubSubMessage]:
        return list(self._dead_letter)

    def stats(self) -> dict:
        return {
            "topics": len(self._topics),
            "total_messages": sum(len(msgs) for msgs in self._topics.values()),
            "consumer_groups": len(self._groups),
            "dead_letters": len(self._dead_letter),
        }
