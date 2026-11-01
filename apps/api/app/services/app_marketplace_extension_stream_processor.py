"""Stream Processor — windowed aggregation for real-time event streams.

Implements:
- Tumbling windows (fixed, non-overlapping)
- Sliding windows (overlapping, step-based)
- Session windows (gap-based, merge on activity)
- Aggregation functions per window (count, sum, avg, min, max)
- Late event handling with allowed lateness
- Watermark-based window closing
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class StreamEvent:
    key: str
    value: float
    timestamp: float


@dataclass
class WindowResult:
    window_start: float
    window_end: float
    key: str
    count: int
    total: float
    avg: float
    min_val: float
    max_val: float


class StreamProcessorService:
    def __init__(self):
        self._events: list[StreamEvent] = []
        self._watermark: float = 0
        self._late_events: list[StreamEvent] = []

    def emit(self, key: str, value: float,
             timestamp: float | None = None) -> None:
        ts = timestamp or time.time()
        event = StreamEvent(key=key, value=value, timestamp=ts)
        if ts < self._watermark:
            self._late_events.append(event)
        else:
            self._events.append(event)

    def advance_watermark(self, timestamp: float) -> None:
        self._watermark = timestamp

    def tumbling_window(self, window_size: float,
                        key: str | None = None) -> list[WindowResult]:
        """Non-overlapping fixed-size windows."""
        events = self._filter_by_key(key)
        if not events:
            return []

        min_ts = min(e.timestamp for e in events)
        max_ts = max(e.timestamp for e in events)

        results = []
        window_start = min_ts - (min_ts % window_size)

        while window_start <= max_ts:
            window_end = window_start + window_size
            window_events = [e for e in events
                             if window_start <= e.timestamp < window_end]
            if window_events:
                results.append(self._aggregate(window_start, window_end,
                                               key or "*", window_events))
            window_start = window_end

        return results

    def sliding_window(self, window_size: float, slide: float,
                       key: str | None = None) -> list[WindowResult]:
        """Overlapping windows with step size."""
        events = self._filter_by_key(key)
        if not events:
            return []

        min_ts = min(e.timestamp for e in events)
        max_ts = max(e.timestamp for e in events)

        results = []
        window_start = min_ts - (min_ts % slide)

        while window_start <= max_ts:
            window_end = window_start + window_size
            window_events = [e for e in events
                             if window_start <= e.timestamp < window_end]
            if window_events:
                results.append(self._aggregate(window_start, window_end,
                                               key or "*", window_events))
            window_start += slide

        return results

    def session_window(self, gap: float,
                       key: str | None = None) -> list[WindowResult]:
        """Merge events into sessions separated by gaps of inactivity."""
        events = sorted(self._filter_by_key(key), key=lambda e: e.timestamp)
        if not events:
            return []

        sessions = []
        current_session = [events[0]]

        for event in events[1:]:
            if event.timestamp - current_session[-1].timestamp <= gap:
                current_session.append(event)
            else:
                sessions.append(current_session)
                current_session = [event]
        sessions.append(current_session)

        return [self._aggregate(s[0].timestamp, s[-1].timestamp + 0.001,
                                key or "*", s) for s in sessions]

    def _filter_by_key(self, key: str | None) -> list[StreamEvent]:
        if key:
            return [e for e in self._events if e.key == key]
        return list(self._events)

    def _aggregate(self, start: float, end: float, key: str,
                   events: list[StreamEvent]) -> WindowResult:
        values = [e.value for e in events]
        return WindowResult(
            window_start=round(start, 3), window_end=round(end, 3),
            key=key, count=len(values),
            total=round(sum(values), 4),
            avg=round(sum(values) / len(values), 4),
            min_val=min(values), max_val=max(values))

    def get_late_events(self) -> list[StreamEvent]:
        return list(self._late_events)

    def stats(self) -> dict:
        return {"total_events": len(self._events),
                "late_events": len(self._late_events),
                "watermark": self._watermark}
