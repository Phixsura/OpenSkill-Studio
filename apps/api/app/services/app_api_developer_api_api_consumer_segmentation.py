"""App API Developer API Consumer Segmentation — segment consumers by behavior."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerSegment:
    segment_id: str
    name: str
    criteria: dict[str, str] = field(default_factory=dict)
    members: set[str] = field(default_factory=set)

class AppAPIDeveloperAPIApiConsumerSegmentation:
    def __init__(self) -> None:
        self._segments: dict[tuple[str, str], ConsumerSegment] = {}

    def create_segment(self, installation_id: str, segment_id: str, name: str, criteria: dict[str, str] | None = None) -> ConsumerSegment:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, segment_id)
        if key in self._segments: raise ValueError(f"Segment {segment_id} exists")
        s = ConsumerSegment(segment_id=segment_id, name=name, criteria=criteria or {})
        self._segments[key] = s
        return s

    def add_member(self, installation_id: str, segment_id: str, consumer_id: str) -> ConsumerSegment:
        s = self._get(installation_id, segment_id)
        s.members.add(consumer_id)
        return s

    def remove_member(self, installation_id: str, segment_id: str, consumer_id: str) -> ConsumerSegment:
        s = self._get(installation_id, segment_id)
        s.members.discard(consumer_id)
        return s

    def is_member(self, installation_id: str, segment_id: str, consumer_id: str) -> bool:
        s = self._get(installation_id, segment_id)
        return consumer_id in s.members

    def consumer_segments(self, installation_id: str, consumer_id: str) -> list[ConsumerSegment]:
        return [s for (inst, _), s in self._segments.items() if inst == installation_id and consumer_id in s.members]

    def list_segments(self, installation_id: str) -> list[ConsumerSegment]:
        return [s for (inst, _), s in self._segments.items() if inst == installation_id]

    def _get(self, installation_id: str, segment_id: str) -> ConsumerSegment:
        key = (installation_id, segment_id)
        s = self._segments.get(key)
        if s is None: raise KeyError(f"Segment {segment_id} not found")
        return s
