"""API endpoint catalog — searchable registry of all API endpoints."""
from __future__ import annotations


def build_catalog(endpoints: list[dict]) -> dict:
    by_tag: dict[str, int] = {}
    by_method: dict[str, int] = {}
    for ep in endpoints:
        tag = ep.get("tag", "default")
        method = ep.get("method", "GET")
        by_tag[tag] = by_tag.get(tag, 0) + 1
        by_method[method] = by_method.get(method, 0) + 1
    return {"endpoints": endpoints, "total": len(endpoints),
            "by_tag": by_tag, "by_method": by_method,
            "tags": sorted(by_tag.keys())}


def search_endpoints(catalog: dict, query: str) -> list[dict]:
    q = query.lower()
    return [ep for ep in catalog["endpoints"]
            if q in ep.get("path", "").lower() or q in ep.get("description", "").lower()]
