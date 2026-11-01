"""Trie Autocomplete — prefix tree for fast autocomplete with frequency ranking.

Implements:
- Insert words with frequency/score
- Prefix search returning top-K results by score
- Fuzzy matching with edit distance 1 (insertion, deletion, substitution)
- Word deletion
- Prefix existence check
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq


@dataclass
class TrieACNode:
    children: dict[str, TrieACNode] = field(default_factory=dict)
    is_word: bool = False
    word: str = ""
    score: float = 0.0


class TrieAutocompleteService:
    def __init__(self):
        self._root = TrieACNode()
        self._size = 0

    def insert(self, word: str, score: float = 1.0) -> None:
        node = self._root
        for ch in word.lower():
            if ch not in node.children:
                node.children[ch] = TrieACNode()
            node = node.children[ch]
        if not node.is_word:
            self._size += 1
        node.is_word = True
        node.word = word
        node.score = score

    def search(self, prefix: str, limit: int = 10) -> list[tuple[str, float]]:
        """Return top-K words matching prefix, sorted by score descending."""
        prefix = prefix.lower()
        node = self._find_node(prefix)
        if not node:
            return []

        # Collect all words under this prefix
        results: list[tuple[float, str]] = []
        self._collect(node, results)

        # Top-K by score (use min-heap of size K)
        top = heapq.nlargest(limit, results, key=lambda x: x[0])
        return [(word, score) for score, word in top]

    def _find_node(self, prefix: str) -> TrieACNode | None:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect(self, node: TrieACNode, results: list) -> None:
        if node.is_word:
            results.append((node.score, node.word))
        for child in node.children.values():
            self._collect(child, results)

    def has_prefix(self, prefix: str) -> bool:
        return self._find_node(prefix.lower()) is not None

    def contains(self, word: str) -> bool:
        node = self._find_node(word.lower())
        return node is not None and node.is_word

    def delete(self, word: str) -> bool:
        """Delete a word. Returns True if found and deleted."""
        word_lower = word.lower()
        # Find the path
        path: list[tuple[TrieACNode, str]] = []
        node = self._root
        for ch in word_lower:
            if ch not in node.children:
                return False
            path.append((node, ch))
            node = node.children[ch]
        if not node.is_word:
            return False
        node.is_word = False
        node.word = ""
        node.score = 0
        self._size -= 1

        # Clean up empty branches
        for parent, ch in reversed(path):
            child = parent.children[ch]
            if not child.children and not child.is_word:
                del parent.children[ch]
            else:
                break
        return True

    def fuzzy_search(self, query: str, max_distance: int = 1,
                     limit: int = 10) -> list[tuple[str, float, int]]:
        """Search with edit distance tolerance. Returns [(word, score, distance)]."""
        query = query.lower()
        results: list[tuple[str, float, int]] = []

        def _dfs(node: TrieACNode, built: str, remaining: str, distance: int):
            if distance > max_distance:
                return
            if not remaining:
                if node.is_word:
                    results.append((node.word, node.score, distance))
                # Deletion from query (extra chars in trie)
                if distance < max_distance:
                    for ch, child in node.children.items():
                        _dfs(child, built + ch, "", distance + 1)
                return

            ch = remaining[0]
            rest = remaining[1:]

            # Exact match
            if ch in node.children:
                _dfs(node.children[ch], built + ch, rest, distance)

            if distance < max_distance:
                # Substitution
                for c, child in node.children.items():
                    if c != ch:
                        _dfs(child, built + c, rest, distance + 1)
                # Insertion (skip a char in query)
                _dfs(node, built, rest, distance + 1)
                # Deletion (extra char in trie)
                for c, child in node.children.items():
                    _dfs(child, built + c, remaining, distance + 1)

        _dfs(self._root, "", query, 0)

        # Deduplicate and sort by score
        seen = {}
        for word, score, dist in results:
            if word not in seen or seen[word][1] > dist:
                seen[word] = (score, dist)
        sorted_results = sorted(seen.items(), key=lambda x: (-x[1][0], x[1][1]))
        return [(w, s, d) for w, (s, d) in sorted_results[:limit]]

    @property
    def size(self) -> int:
        return self._size
