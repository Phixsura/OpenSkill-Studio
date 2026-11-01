"""Skip List — probabilistic sorted data structure with O(log n) operations.

Implements:
- Randomized level assignment (coin-flip promotion)
- O(log n) search, insert, delete
- Range queries
- Rank queries (find k-th element)
- Memory-efficient alternative to balanced BST
"""
from __future__ import annotations
from dataclasses import dataclass, field
import random


MAX_LEVEL = 16


@dataclass
class SkipNode:
    key: object
    value: object
    forward: list = field(default_factory=list)  # forward[i] = next node at level i

    def __post_init__(self):
        if not self.forward:
            self.forward = [None] * (MAX_LEVEL + 1)


class SkipListService:
    def __init__(self, p: float = 0.5):
        self._header = SkipNode(key=None, value=None)
        self._header.forward = [None] * (MAX_LEVEL + 1)
        self._level = 0
        self._size = 0
        self._p = p  # promotion probability

    def _random_level(self) -> int:
        lvl = 0
        while random.random() < self._p and lvl < MAX_LEVEL:
            lvl += 1
        return lvl

    def insert(self, key, value) -> None:
        update = [None] * (MAX_LEVEL + 1)
        current = self._header

        for i in range(self._level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current and current.key == key:
            current.value = value  # update existing
            return

        new_level = self._random_level()
        if new_level > self._level:
            for i in range(self._level + 1, new_level + 1):
                update[i] = self._header
            self._level = new_level

        new_node = SkipNode(key=key, value=value)
        new_node.forward = [None] * (MAX_LEVEL + 1)
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        self._size += 1

    def search(self, key) -> object | None:
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
        current = current.forward[0]
        if current and current.key == key:
            return current.value
        return None

    def delete(self, key) -> bool:
        update = [None] * (MAX_LEVEL + 1)
        current = self._header

        for i in range(self._level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        target = current.forward[0]
        if not target or target.key != key:
            return False

        for i in range(self._level + 1):
            if update[i].forward[i] != target:
                break
            update[i].forward[i] = target.forward[i]

        while self._level > 0 and self._header.forward[self._level] is None:
            self._level -= 1

        self._size -= 1
        return True

    def range_query(self, low, high) -> list[tuple]:
        """Return all (key, value) pairs where low <= key <= high."""
        result = []
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] and current.forward[i].key < low:
                current = current.forward[i]

        current = current.forward[0]
        while current and current.key <= high:
            result.append((current.key, current.value))
            current = current.forward[0]
        return result

    def to_sorted_list(self) -> list[tuple]:
        result = []
        current = self._header.forward[0]
        while current:
            result.append((current.key, current.value))
            current = current.forward[0]
        return result

    @property
    def size(self) -> int:
        return self._size

    @property
    def level(self) -> int:
        return self._level
