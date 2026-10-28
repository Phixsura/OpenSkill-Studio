"""App Resource Tag — tag and categorize resources.

Manages resource tagging:
- Add/remove tags on resources
- Query resources by tag
- Tag usage statistics
- Per-installation scoped tags
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TaggedResource:
    """A tagged resource."""

    resource_id: str
    resource_type: str
    tags: set[str] = field(default_factory=set)


class AppResourceTag:
    """Tag and categorize resources."""

    def __init__(self) -> None:
        self._resources: dict[tuple[str, str], TaggedResource] = {}

    def tag(
        self, installation_id: str, resource_id: str, resource_type: str,
        tags: list[str],
    ) -> TaggedResource:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not tags:
            raise ValueError("at least one tag required")

        # Normalize tags
        normalized = {t.strip().lower() for t in tags if t.strip()}
        if not normalized:
            raise ValueError("tags cannot be empty strings")

        key = (installation_id, resource_id)
        if key in self._resources:
            self._resources[key].tags.update(normalized)
        else:
            self._resources[key] = TaggedResource(
                resource_id=resource_id, resource_type=resource_type,
                tags=normalized,
            )
        return self._resources[key]

    def untag(
        self, installation_id: str, resource_id: str, tags: list[str],
    ) -> TaggedResource:
        key = (installation_id, resource_id)
        r = self._resources.get(key)
        if r is None:
            raise KeyError(f"Resource {resource_id} not found")
        normalized = {t.strip().lower() for t in tags}
        r.tags -= normalized
        return r

    def find_by_tag(self, installation_id: str, tag: str) -> list[TaggedResource]:
        normalized = tag.strip().lower()
        return [
            r for (inst, _), r in self._resources.items()
            if inst == installation_id and normalized in r.tags
        ]

    def all_tags(self, installation_id: str) -> list[dict]:
        """All tags with usage counts."""
        counts: dict[str, int] = {}
        for (inst, _), r in self._resources.items():
            if inst != installation_id:
                continue
            for t in r.tags:
                counts[t] = counts.get(t, 0) + 1
        return sorted(
            [{"tag": t, "count": c} for t, c in counts.items()],
            key=lambda x: x["count"], reverse=True,
        )

    def get_tags(self, installation_id: str, resource_id: str) -> set[str]:
        key = (installation_id, resource_id)
        r = self._resources.get(key)
        if r is None:
            return set()
        return r.tags
