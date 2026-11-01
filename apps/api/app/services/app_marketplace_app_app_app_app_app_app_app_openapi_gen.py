"""OpenAPI spec generator — generate API documentation."""
from __future__ import annotations
import html


def generate_spec(title: str, version: str, endpoints: list[dict]) -> dict:
    paths = {}
    tags = set()
    for ep in endpoints:
        method = ep.get("method", "get").lower()
        path = ep.get("path", "/")
        tag = ep.get("tag", "default")
        tags.add(tag)
        paths.setdefault(path, {})[method] = {
            "summary": html.escape(ep.get("summary", "")),
            "tags": [tag],
            "responses": {"200": {"description": ep.get("response_desc", "Success")}},
        }
    return {"openapi": "3.0.3", "info": {"title": html.escape(title), "version": version},
            "paths": paths, "endpoint_count": len(endpoints),
            "path_count": len(paths), "tags": sorted(tags)}


def spec_stats(spec: dict) -> dict:
    methods: dict[str, int] = {}
    for path_methods in spec.get("paths", {}).values():
        for method in path_methods:
            methods[method] = methods.get(method, 0) + 1
    return {"endpoints": spec.get("endpoint_count", 0),
            "paths": spec.get("path_count", 0),
            "tags": len(spec.get("tags", [])),
            "by_method": methods}
