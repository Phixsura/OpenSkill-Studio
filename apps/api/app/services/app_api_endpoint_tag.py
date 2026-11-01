"""App API Endpoint Tag — tag and categorize API endpoints.

Manages endpoint tags:
- Tag endpoints by method+path
- Group endpoints by tag
- Tag usage statistics
- Per-installation scoped tags
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TaggedEndpoint:
    """A tagged API endpoint."""

    method: str
    path: str
    tags: set[str] = field(default_factory=set)


class AppAPIEndpointTag:
    """Tag and categorize API endpoints."""

    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str], TaggedEndpoint] = {}

    def tag(
        self, installation_id: str, method: str, path: str, tags: list[str],
    ) -> TaggedEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), path)
        if key not in self._endpoints:
            self._endpoints[key] = TaggedEndpoint(method=method.upper(), path=path)
        ep = self._endpoints[key]
        ep.tags.update(t.lower() for t in tags if t.strip())
        return ep

    def find_by_tag(self, installation_id: str, tag: str) -> list[TaggedEndpoint]:
        return [
            ep for (inst, _, _), ep in self._endpoints.items()
            if inst == installation_id and tag.lower() in ep.tags
        ]

    def all_tags(self, installation_id: str) -> list[dict]:
        counts: dict[str, int] = {}
        for (inst, _, _), ep in self._endpoints.items():
            if inst != installation_id:
                continue
            for t in ep.tags:
                counts[t] = counts.get(t, 0) + 1
        return sorted([{"tag": t, "count": c} for t, c in counts.items()], key=lambda x: x["count"], reverse=True)

    def list_endpoints(self, installation_id: str) -> list[TaggedEndpoint]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id]
