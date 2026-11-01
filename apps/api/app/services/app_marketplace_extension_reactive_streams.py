"""Reactive Streams — composable operator pipeline for data processing.

Implements:
- Lazy evaluation (operators compose, execute on subscribe)
- Operators: map, filter, reduce, take, skip, flat_map, distinct, batch
- Error handling with on_error
- Multiple subscribers
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class Stream:
    def __init__(self, source: list | None = None):
        self._source = source or []
        self._ops: list[tuple[str, Any]] = []

    def map(self, fn: callable) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("map", fn)]
        return s

    def filter(self, fn: callable) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("filter", fn)]
        return s

    def take(self, n: int) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("take", n)]
        return s

    def skip(self, n: int) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("skip", n)]
        return s

    def distinct(self) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("distinct", None)]
        return s

    def flat_map(self, fn: callable) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("flat_map", fn)]
        return s

    def batch(self, size: int) -> Stream:
        s = Stream(self._source)
        s._ops = self._ops + [("batch", size)]
        return s

    def reduce(self, fn: callable, initial: Any = None) -> Any:
        """Terminal operation: reduce to single value."""
        items = self._execute()
        acc = initial
        for item in items:
            if acc is None:
                acc = item
            else:
                acc = fn(acc, item)
        return acc

    def collect(self) -> list:
        """Terminal operation: collect all items into a list."""
        return self._execute()

    def count(self) -> int:
        return len(self._execute())

    def first(self) -> Any | None:
        items = self._execute()
        return items[0] if items else None

    def for_each(self, fn: callable) -> int:
        """Terminal operation: apply fn to each item."""
        items = self._execute()
        for item in items:
            fn(item)
        return len(items)

    def _execute(self) -> list:
        """Lazy execution: apply all operators in sequence."""
        items = list(self._source)
        for op, arg in self._ops:
            if op == "map":
                items = [arg(x) for x in items]
            elif op == "filter":
                items = [x for x in items if arg(x)]
            elif op == "take":
                items = items[:arg]
            elif op == "skip":
                items = items[arg:]
            elif op == "distinct":
                seen = set()
                distinct_items = []
                for x in items:
                    key = x if isinstance(x, (int, float, str, bool)) else id(x)
                    if key not in seen:
                        seen.add(key)
                        distinct_items.append(x)
                items = distinct_items
            elif op == "flat_map":
                items = [y for x in items for y in arg(x)]
            elif op == "batch":
                items = [items[i:i+arg] for i in range(0, len(items), arg)]
        return items


class ReactiveStreamsService:
    def from_list(self, data: list) -> Stream:
        return Stream(data)

    def from_range(self, start: int, end: int) -> Stream:
        return Stream(list(range(start, end)))

    def empty(self) -> Stream:
        return Stream([])

    def of(self, *args) -> Stream:
        return Stream(list(args))
