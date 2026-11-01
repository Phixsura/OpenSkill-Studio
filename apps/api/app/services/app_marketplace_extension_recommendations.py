"""Extension Recommendations — personalized extension suggestions."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class ExtInfo:
    extension_id: str
    name: str
    category: str
    tags: list[str] = field(default_factory=list)
    installs: int = 0
    rating: float = 0.0


class ExtRecommendationsService:
    def __init__(self):
        self._extensions: dict[str, ExtInfo] = {}
        self._user_installs: dict[str, set[str]] = {}  # user_id -> ext_ids

    def register(self, ext: ExtInfo) -> None:
        self._extensions[ext.extension_id] = ext

    def record_install(self, user_id: str, extension_id: str) -> None:
        if user_id not in self._user_installs:
            self._user_installs[user_id] = set()
        self._user_installs[user_id].add(extension_id)

    def recommend(self, user_id: str, limit: int = 5) -> list[ExtInfo]:
        installed = self._user_installs.get(user_id, set())
        if not installed:
            return self._popular(limit)

        # Find preferred categories/tags
        cat_counter: Counter[str] = Counter()
        tag_counter: Counter[str] = Counter()
        for eid in installed:
            ext = self._extensions.get(eid)
            if ext:
                cat_counter[ext.category] += 1
                for t in ext.tags:
                    tag_counter[t] += 1

        # Score uninstalled extensions
        scored: list[tuple[float, ExtInfo]] = []
        for ext in self._extensions.values():
            if ext.extension_id in installed:
                continue
            score = 0.0
            score += cat_counter.get(ext.category, 0) * 3
            for t in ext.tags:
                score += tag_counter.get(t, 0) * 2
            score += ext.rating
            score += min(ext.installs / 100, 5)
            scored.append((score, ext))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:limit]]

    def _popular(self, limit: int) -> list[ExtInfo]:
        return sorted(self._extensions.values(), key=lambda e: e.installs, reverse=True)[:limit]

    def similar(self, extension_id: str, limit: int = 5) -> list[ExtInfo]:
        target = self._extensions.get(extension_id)
        if not target: return []
        scored = []
        for ext in self._extensions.values():
            if ext.extension_id == extension_id: continue
            score = 0.0
            if ext.category == target.category: score += 5
            score += len(set(ext.tags) & set(target.tags)) * 2
            if score > 0:
                scored.append((score, ext))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:limit]]
