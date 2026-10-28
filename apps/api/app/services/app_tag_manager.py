"""App Tag Manager — manage tags and labels for app resources.

Provides tagging for installed app resources:
- Add/remove tags on any resource
- List resources by tag
- Tag hierarchy (namespaced: category:value)
- Bulk tag operations
- Per-installation scoped tags
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TaggedResource:
    """A resource with its tags."""

    resource_type: str
    resource_id: str
    tags: set[str] = field(default_factory=set)


class AppTagManager:
    """Manage tags and labels for app resources."""

    def __init__(self) -> None:
        # (installation_id, resource_type, resource_id) → TaggedResource
        self._resources: dict[tuple[str, str, str], TaggedResource] = {}

    def add_tags(
        self,
        installation_id: str,
        resource_type: str,
        resource_id: str,
        tags: list[str],
    ) -> TaggedResource:
        """Add tags to a resource."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not resource_type:
            raise ValueError("resource_type is required")
        if not resource_id:
            raise ValueError("resource_id is required")
        if not tags:
            raise ValueError("at least one tag is required")

        # Validate tag format
        for tag in tags:
            if not tag or len(tag) > 100:
                raise ValueError(f"Invalid tag: {tag!r}")

        key = (installation_id, resource_type, resource_id)
        resource = self._resources.get(key)
        if resource is None:
            resource = TaggedResource(resource_type=resource_type, resource_id=resource_id)
            self._resources[key] = resource

        resource.tags.update(tags)
        return resource

    def remove_tags(
        self,
        installation_id: str,
        resource_type: str,
        resource_id: str,
        tags: list[str],
    ) -> TaggedResource:
        """Remove tags from a resource."""
        key = (installation_id, resource_type, resource_id)
        resource = self._resources.get(key)
        if resource is None:
            raise KeyError(f"Resource {resource_type}/{resource_id} not found")

        resource.tags -= set(tags)
        return resource

    def get_tags(
        self,
        installation_id: str,
        resource_type: str,
        resource_id: str,
    ) -> set[str]:
        """Get tags for a resource."""
        key = (installation_id, resource_type, resource_id)
        resource = self._resources.get(key)
        if resource is None:
            return set()
        return set(resource.tags)

    def find_by_tag(
        self,
        installation_id: str,
        tag: str,
        resource_type: str | None = None,
    ) -> list[TaggedResource]:
        """Find resources with a specific tag."""
        results = []
        for (inst, rtype, _), resource in self._resources.items():
            if inst != installation_id:
                continue
            if resource_type and rtype != resource_type:
                continue
            if tag in resource.tags:
                results.append(resource)
        return results

    def find_by_prefix(
        self,
        installation_id: str,
        prefix: str,
    ) -> list[TaggedResource]:
        """Find resources with tags matching a prefix (e.g. 'env:')."""
        results = []
        for (inst, _, _), resource in self._resources.items():
            if inst != installation_id:
                continue
            if any(t.startswith(prefix) for t in resource.tags):
                results.append(resource)
        return results

    def all_tags(self, installation_id: str) -> list[str]:
        """List all unique tags across all resources."""
        tags: set[str] = set()
        for (inst, _, _), resource in self._resources.items():
            if inst == installation_id:
                tags.update(resource.tags)
        return sorted(tags)

    def tag_counts(self, installation_id: str) -> dict[str, int]:
        """Count resources per tag."""
        counts: dict[str, int] = {}
        for (inst, _, _), resource in self._resources.items():
            if inst != installation_id:
                continue
            for tag in resource.tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts
