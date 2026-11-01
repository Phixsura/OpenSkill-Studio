"""Resource tagging manager — tag and query infrastructure resources."""
from __future__ import annotations
from collections import defaultdict


class ResourceTagger:
    def __init__(self):
        self._resources: dict[str, dict] = {}

    def tag(self, resource_id: str, tags: dict[str, str]) -> dict:
        existing = self._resources.get(resource_id, {"id": resource_id, "tags": {}})
        existing["tags"].update(tags)
        self._resources[resource_id] = existing
        return {"resource_id": resource_id, "tags": existing["tags"]}

    def untag(self, resource_id: str, keys: list[str]) -> dict:
        if resource_id in self._resources:
            for k in keys:
                self._resources[resource_id]["tags"].pop(k, None)
        return {"resource_id": resource_id, "removed": keys}

    def query(self, tag_key: str, tag_value: str = "") -> list[dict]:
        results = []
        for r in self._resources.values():
            if tag_key in r["tags"]:
                if not tag_value or r["tags"][tag_key] == tag_value:
                    results.append(r)
        return results

    def untagged(self, required_keys: list[str]) -> list[str]:
        missing = []
        for rid, r in self._resources.items():
            for key in required_keys:
                if key not in r["tags"]:
                    missing.append(rid)
                    break
        return sorted(missing)

    def tag_summary(self) -> dict:
        tag_counts: dict[str, int] = defaultdict(int)
        for r in self._resources.values():
            for k in r["tags"]:
                tag_counts[k] += 1
        return {"total_resources": len(self._resources),
                "tag_keys": dict(tag_counts)}
