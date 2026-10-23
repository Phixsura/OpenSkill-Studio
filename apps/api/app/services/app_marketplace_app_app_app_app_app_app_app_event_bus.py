"""Event bus — publish/subscribe event system."""
from __future__ import annotations
import time

_subscribers: dict[str, list[str]] = {}
_events: list[dict] = []


def subscribe(topic: str, handler: str) -> dict:
    _subscribers.setdefault(topic, [])
    if handler not in _subscribers[topic]:
        _subscribers[topic].append(handler)
    return {"subscribed": True, "topic": topic, "handler": handler,
            "subscriber_count": len(_subscribers[topic])}


def publish(topic: str, payload: dict) -> dict:
    handlers = _subscribers.get(topic, [])
    event = {"topic": topic, "payload": payload, "timestamp": time.time(),
             "delivered_to": len(handlers)}
    _events.append(event)
    return event


def get_subscriptions() -> dict:
    total = sum(len(h) for h in _subscribers.values())
    return {"topics": dict(_subscribers), "topic_count": len(_subscribers),
            "total_subscriptions": total}


def event_history(limit: int = 20) -> list[dict]:
    return list(reversed(_events[-limit:]))


def clear_bus() -> None:
    _subscribers.clear()
    _events.clear()
