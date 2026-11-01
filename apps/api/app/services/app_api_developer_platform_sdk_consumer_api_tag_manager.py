"""Endpoint Tag Manager — tag-based endpoint organization with search."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

TAG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,49}$")


@dataclass
class TagManager:
    """Organize endpoints with tags for categorization and search."""

    _endpoint_tags: dict[str, set[str]] = field(default_factory=dict)
    _tag_metadata: dict[str, dict] = field(default_factory=dict)

    def add_tag(self, endpoint_id: str, tag: str) -> dict:
        if not TAG_RE.match(tag):
            raise ValueError(f"Invalid tag format: {tag}. Use lowercase alphanumeric, hyphens, underscores.")
        self._endpoint_tags.setdefault(endpoint_id, set()).add(tag)
        self._tag_metadata.setdefault(tag, {"description": "", "color": ""})
        logger.info("tag_added", endpoint_id=endpoint_id, tag=tag)
        return {"endpoint_id": endpoint_id, "tag": tag,
                "total_tags": len(self._endpoint_tags[endpoint_id])}

    def remove_tag(self, endpoint_id: str, tag: str) -> dict:
        tags = self._endpoint_tags.get(endpoint_id, set())
        tags.discard(tag)
        return {"removed": True}

    def set_tag_metadata(self, tag: str, description: str = "", color: str = "") -> dict:
        self._tag_metadata[tag] = {"description": description, "color": color}
        return {"tag": tag, "updated": True}

    def get_endpoint_tags(self, endpoint_id: str) -> list[str]:
        return sorted(self._endpoint_tags.get(endpoint_id, set()))

    def find_by_tag(self, tag: str) -> list[str]:
        return sorted(eid for eid, tags in self._endpoint_tags.items() if tag in tags)

    def find_by_tags(self, tags: list[str], match_all: bool = False) -> list[str]:
        tag_set = set(tags)
        results = []
        for eid, etags in self._endpoint_tags.items():
            if match_all:
                if tag_set.issubset(etags):
                    results.append(eid)
            else:
                if tag_set & etags:
                    results.append(eid)
        return sorted(results)

    def list_tags(self) -> list[dict]:
        tag_counts: dict[str, int] = {}
        for tags in self._endpoint_tags.values():
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return [
            {"tag": t, "endpoint_count": c,
             **self._tag_metadata.get(t, {"description": "", "color": ""})}
            for t, c in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ]

    def merge_tags(self, old_tag: str, new_tag: str) -> dict:
        if not TAG_RE.match(new_tag):
            raise ValueError(f"Invalid tag format: {new_tag}")
        count = 0
        for eid, tags in self._endpoint_tags.items():
            if old_tag in tags:
                tags.discard(old_tag)
                tags.add(new_tag)
                count += 1
        if old_tag in self._tag_metadata:
            if new_tag not in self._tag_metadata:
                self._tag_metadata[new_tag] = self._tag_metadata[old_tag]
            del self._tag_metadata[old_tag]
        return {"old_tag": old_tag, "new_tag": new_tag, "endpoints_updated": count}

    def get_tag_cloud(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for tags in self._endpoint_tags.values():
            for tag in tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts

    def get_stats(self) -> dict:
        all_tags: set[str] = set()
        for tags in self._endpoint_tags.values():
            all_tags.update(tags)
        return {
            "total_endpoints": len(self._endpoint_tags),
            "unique_tags": len(all_tags),
            "avg_tags_per_endpoint": round(
                sum(len(t) for t in self._endpoint_tags.values()) / len(self._endpoint_tags), 1
            ) if self._endpoint_tags else 0,
        }
