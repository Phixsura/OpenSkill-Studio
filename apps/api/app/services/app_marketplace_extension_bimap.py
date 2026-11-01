"""Bi-directional Map — O(1) lookup in both directions.

Unlike a regular dict (key→value), BiMap supports instant value→key lookup.
Useful for: ID↔name mappings, codec tables, permission translations.

Implements:
- Forward (key→value) and inverse (value→key) O(1) lookups
- Insertion maintains both directions
- Update handles old value cleanup
- Iteration in both directions
- Bulk operations
"""
from __future__ import annotations


class BiMap:
    def __init__(self):
        self._forward: dict = {}
        self._inverse: dict = {}

    def put(self, key, value) -> None:
        """Insert or update a mapping. Enforces bijection (1:1)."""
        # Clean up old mappings if key or value already exists
        if key in self._forward:
            old_value = self._forward[key]
            del self._inverse[old_value]
        if value in self._inverse:
            old_key = self._inverse[value]
            del self._forward[old_key]

        self._forward[key] = value
        self._inverse[value] = key

    def get_by_key(self, key, default=None):
        return self._forward.get(key, default)

    def get_by_value(self, value, default=None):
        return self._inverse.get(value, default)

    def remove_by_key(self, key) -> bool:
        if key in self._forward:
            value = self._forward.pop(key)
            del self._inverse[value]
            return True
        return False

    def remove_by_value(self, value) -> bool:
        if value in self._inverse:
            key = self._inverse.pop(value)
            del self._forward[key]
            return True
        return False

    def contains_key(self, key) -> bool:
        return key in self._forward

    def contains_value(self, value) -> bool:
        return value in self._inverse

    def keys(self) -> list:
        return list(self._forward.keys())

    def values(self) -> list:
        return list(self._forward.values())

    def items(self) -> list[tuple]:
        return list(self._forward.items())

    def inverse_items(self) -> list[tuple]:
        return list(self._inverse.items())

    @property
    def size(self) -> int:
        return len(self._forward)

    def clear(self) -> None:
        self._forward.clear()
        self._inverse.clear()

    def to_dict(self) -> dict:
        return dict(self._forward)

    @classmethod
    def from_dict(cls, data: dict) -> BiMap:
        bm = cls()
        for k, v in data.items():
            bm.put(k, v)
        return bm


class BiMapService:
    def __init__(self):
        self._maps: dict[str, BiMap] = {}

    def create(self, name: str) -> BiMap:
        bm = BiMap()
        self._maps[name] = bm
        return bm

    def get(self, name: str) -> BiMap | None:
        return self._maps.get(name)
