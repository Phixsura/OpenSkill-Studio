"""Resource tagging — tag and filter resources by labels."""
from __future__ import annotations

_resources: dict[str, dict] = {}


def tag_resource(resource_id: str, tags: dict[str, str]) -> dict:
    existing = _resources.get(resource_id, {"id": resource_id, "tags": {}})
    existing["tags"].update(tags)
    _resources[resource_id] = existing
    return {"id": resource_id, "tags": existing["tags"], "tag_count": len(existing["tags"])}


def find_by_tag(key: str, value: str | None = None) -> list[dict]:
    results = []
    for res in _resources.values():
        if key in res["tags"]:
            if value is None or res["tags"][key] == value:
                results.append(res)
    return results


def tag_stats() -> dict:
    all_keys: dict[str, int] = {}
    for res in _resources.values():
        for k in res["tags"]:
            all_keys[k] = all_keys.get(k, 0) + 1
    return {"total_resources": len(_resources), "unique_tags": len(all_keys),
            "tag_distribution": dict(sorted(all_keys.items(), key=lambda x: -x[1]))}


def clear_resources() -> None:
    _resources.clear()
