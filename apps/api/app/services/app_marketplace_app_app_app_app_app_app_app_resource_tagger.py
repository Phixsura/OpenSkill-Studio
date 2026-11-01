"""Resource tagging system — tag, query, and organize cloud resources."""
from __future__ import annotations


class ResourceTagger:
    def __init__(self):
        self._resources: dict[str, dict] = {}

    def tag(self, resource_id: str, *, tags: dict[str, str]) -> dict:
        if resource_id not in self._resources:
            self._resources[resource_id] = {"tags": {}}
        self._resources[resource_id]["tags"].update(tags)
        return {"resource_id": resource_id, "tags": self._resources[resource_id]["tags"]}

    def untag(self, resource_id: str, *, keys: list[str]) -> dict:
        r = self._resources.get(resource_id)
        if not r:
            return {"error": "Resource not found"}
        for k in keys:
            r["tags"].pop(k, None)
        return {"resource_id": resource_id, "tags": r["tags"]}

    def query(self, *, tag_key: str, tag_value: str | None = None) -> list[str]:
        results = []
        for rid, r in self._resources.items():
            if tag_key in r["tags"]:
                if tag_value is None or r["tags"][tag_key] == tag_value:
                    results.append(rid)
        return results

    def cost_by_tag(self, tag_key: str, costs: dict[str, float]) -> dict:
        by_tag: dict[str, float] = {}
        for rid, cost in costs.items():
            r = self._resources.get(rid, {})
            val = r.get("tags", {}).get(tag_key, "untagged")
            by_tag[val] = by_tag.get(val, 0) + cost
        return {"tag_key": tag_key, "breakdown": by_tag,
                "total": round(sum(by_tag.values()), 2)}

    def stats(self) -> dict:
        all_keys: set[str] = set()
        for r in self._resources.values():
            all_keys.update(r["tags"].keys())
        return {"total_resources": len(self._resources),
                "unique_tag_keys": len(all_keys), "tag_keys": sorted(all_keys)}
