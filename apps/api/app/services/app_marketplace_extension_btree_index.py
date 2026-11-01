"""B-Tree Index — ordered key-value store with range queries.

Implements:
- B-Tree with configurable order (max children per node)
- Insert with node splitting when full
- Point lookup, range queries, prefix scan
- In-order traversal for sorted iteration
- Min/max queries
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BTreeNode:
    keys: list = field(default_factory=list)
    values: list = field(default_factory=list)
    children: list = field(default_factory=list)
    leaf: bool = True


class BTreeIndexService:
    def __init__(self, order: int = 4):
        """order = max keys per node (splits at order)."""
        self._root = BTreeNode()
        self._order = order
        self._size = 0

    def insert(self, key, value) -> None:
        root = self._root
        if len(root.keys) == self._order:
            # Root is full — split
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self._root)
            self._split_child(new_root, 0)
            self._root = new_root
        self._insert_non_full(self._root, key, value)
        self._size += 1

    def _insert_non_full(self, node: BTreeNode, key, value) -> None:
        i = len(node.keys) - 1

        if node.leaf:
            # Find position and insert
            while i >= 0 and key < node.keys[i]:
                i -= 1
            # Update if key exists
            if i >= 0 and node.keys[i] == key:
                node.values[i] = value
                self._size -= 1  # not a new key
                return
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            if i >= 0 and node.keys[i] == key:
                node.values[i] = value
                self._size -= 1
                return
            i += 1
            if len(node.children[i].keys) == self._order:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, index: int) -> None:
        child = parent.children[index]
        mid = self._order // 2
        new_node = BTreeNode(leaf=child.leaf)

        parent.keys.insert(index, child.keys[mid])
        parent.values.insert(index, child.values[mid])
        parent.children.insert(index + 1, new_node)

        new_node.keys = child.keys[mid + 1:]
        new_node.values = child.values[mid + 1:]
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]

        if not child.leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

    def get(self, key) -> object | None:
        return self._search(self._root, key)

    def _search(self, node: BTreeNode, key) -> object | None:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        if node.leaf:
            return None
        return self._search(node.children[i], key)

    def range_query(self, low, high) -> list[tuple]:
        """Return all (key, value) pairs where low <= key <= high."""
        result = []
        self._range_collect(self._root, low, high, result)
        return result

    def _range_collect(self, node: BTreeNode, low, high, result: list) -> None:
        for i, key in enumerate(node.keys):
            if not node.leaf and i < len(node.children):
                if key >= low:
                    self._range_collect(node.children[i], low, high, result)
            if low <= key <= high:
                result.append((key, node.values[i]))
        if not node.leaf and len(node.children) > len(node.keys):
            last_key = node.keys[-1] if node.keys else low
            if last_key <= high:
                self._range_collect(node.children[-1], low, high, result)

    def min_key(self) -> tuple | None:
        node = self._root
        if not node.keys:
            return None
        while not node.leaf:
            node = node.children[0]
        return (node.keys[0], node.values[0]) if node.keys else None

    def max_key(self) -> tuple | None:
        node = self._root
        if not node.keys:
            return None
        while not node.leaf:
            node = node.children[-1]
        return (node.keys[-1], node.values[-1]) if node.keys else None

    def in_order(self) -> list[tuple]:
        """Return all entries in sorted order."""
        result = []
        self._in_order(self._root, result)
        return result

    def _in_order(self, node: BTreeNode, result: list) -> None:
        for i, key in enumerate(node.keys):
            if not node.leaf and i < len(node.children):
                self._in_order(node.children[i], result)
            result.append((key, node.values[i]))
        if not node.leaf and len(node.children) > len(node.keys):
            self._in_order(node.children[-1], result)

    @property
    def size(self) -> int:
        return self._size
