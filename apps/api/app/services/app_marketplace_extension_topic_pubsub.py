"""Topic Pub/Sub — topic-based messaging with wildcard subscriptions.

MQTT/NATS-style: topic hierarchy with wildcard pattern matching.

Implements:
- Hierarchical topics: "events.user.login"
- Single-level wildcard (+): "events.user.+" matches events.user.login
- Multi-level wildcard (#): "events.#" matches events.user.login.failed
- Subscriber groups (competing consumers)
- Message retention per topic
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import re
from collections import defaultdict


@dataclass
class TopicMessage:
    msg_id: str
    topic: str
    payload: dict
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class Subscription:
    sub_id: str
    pattern: str
    group: str = ""  # empty = broadcast, non-empty = competing consumer
    callback_name: str = ""


class TopicPubSubService:
    def __init__(self, retention: int = 1000):
        self._subscriptions: list[Subscription] = []
        self._messages: dict[str, list[TopicMessage]] = defaultdict(list)
        self._retention = retention
        self._counter = 0
        self._delivered: dict[str, list[str]] = defaultdict(list)  # sub_id -> [msg_ids]
        self._group_idx: dict[str, int] = {}  # group -> round robin index

    def subscribe(self, pattern: str, sub_id: str = "",
                  group: str = "") -> Subscription:
        self._counter += 1
        if not sub_id:
            sub_id = f"sub-{self._counter}"
        sub = Subscription(sub_id=sub_id, pattern=pattern, group=group)
        self._subscriptions.append(sub)
        return sub

    def unsubscribe(self, sub_id: str) -> bool:
        for i, sub in enumerate(self._subscriptions):
            if sub.sub_id == sub_id:
                self._subscriptions.pop(i)
                return True
        return False

    def publish(self, topic: str, payload: dict) -> dict:
        """Publish to a topic. Returns delivery info."""
        self._counter += 1
        msg = TopicMessage(msg_id=f"msg-{self._counter}", topic=topic,
                           payload=payload)
        self._messages[topic].append(msg)
        # Trim retention
        if len(self._messages[topic]) > self._retention:
            self._messages[topic] = self._messages[topic][-self._retention:]

        # Find matching subscriptions
        matching = [s for s in self._subscriptions if self._matches(s.pattern, topic)]

        # Group by subscription group
        groups: dict[str, list[Subscription]] = defaultdict(list)
        broadcast = []
        for sub in matching:
            if sub.group:
                groups[sub.group].append(sub)
            else:
                broadcast.append(sub)

        delivered_to = []

        # Broadcast: deliver to ALL non-grouped subscribers
        for sub in broadcast:
            self._delivered[sub.sub_id].append(msg.msg_id)
            delivered_to.append(sub.sub_id)

        # Grouped: deliver to ONE per group (round-robin)
        for group_name, subs in groups.items():
            idx = self._group_idx.get(group_name, 0) % len(subs)
            chosen = subs[idx]
            self._delivered[chosen.sub_id].append(msg.msg_id)
            delivered_to.append(chosen.sub_id)
            self._group_idx[group_name] = idx + 1

        return {"msg_id": msg.msg_id, "topic": topic,
                "delivered_to": delivered_to, "count": len(delivered_to)}

    def _matches(self, pattern: str, topic: str) -> bool:
        """Match topic against subscription pattern with wildcards."""
        pattern_parts = pattern.split(".")
        topic_parts = topic.split(".")

        pi = 0
        ti = 0
        while pi < len(pattern_parts) and ti < len(topic_parts):
            if pattern_parts[pi] == "#":
                return True  # matches everything after
            if pattern_parts[pi] == "+" or pattern_parts[pi] == topic_parts[ti]:
                pi += 1
                ti += 1
            else:
                return False

        # Both exhausted = match; pattern has trailing # = match
        if pi == len(pattern_parts) and ti == len(topic_parts):
            return True
        if pi < len(pattern_parts) and pattern_parts[pi] == "#":
            return True
        return False

    def get_messages(self, sub_id: str) -> list[TopicMessage]:
        """Get all delivered messages for a subscriber."""
        msg_ids = self._delivered.get(sub_id, [])
        msgs = []
        for topic_msgs in self._messages.values():
            for msg in topic_msgs:
                if msg.msg_id in msg_ids:
                    msgs.append(msg)
        return msgs

    def get_topics(self) -> list[str]:
        return sorted(self._messages.keys())
