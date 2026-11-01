"""Extension Event Bus — publish/subscribe event system for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class Event:
    event_id: str
    topic: str
    payload: dict
    publisher_id: str
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


class ExtEventBusService:
    def __init__(self):
        self._subscribers: dict[str, list[str]] = defaultdict(list)  # topic -> [ext_ids]
        self._events: list[Event] = []
        self._dead_letter: list[Event] = []
        self._counter = 0

    def subscribe(self, extension_id: str, topic: str) -> None:
        if extension_id not in self._subscribers[topic]:
            self._subscribers[topic].append(extension_id)

    def unsubscribe(self, extension_id: str, topic: str) -> bool:
        subs = self._subscribers.get(topic, [])
        if extension_id in subs:
            subs.remove(extension_id)
            return True
        return False

    def publish(self, publisher_id: str, topic: str, payload: dict) -> Event:
        self._counter += 1
        evt = Event(event_id=f"evt-{self._counter}", topic=topic,
                    payload=payload, publisher_id=publisher_id)
        self._events.append(evt)
        if not self._subscribers.get(topic):
            self._dead_letter.append(evt)
        return evt

    def get_events(self, topic: str, limit: int = 50) -> list[Event]:
        return [e for e in reversed(self._events) if e.topic == topic][:limit]

    def get_subscribers(self, topic: str) -> list[str]:
        return list(self._subscribers.get(topic, []))

    def get_topics(self) -> list[str]:
        return list(self._subscribers.keys())

    def get_dead_letters(self) -> list[Event]:
        return list(self._dead_letter)
