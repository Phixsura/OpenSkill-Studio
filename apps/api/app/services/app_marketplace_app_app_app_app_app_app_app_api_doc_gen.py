"""API documentation generator — build OpenAPI-style docs from endpoint definitions."""
from __future__ import annotations
import html


def generate_docs(endpoints: list[dict], *, title: str = "API",
                   version: str = "1.0.0", base_url: str = "") -> dict:
    paths: dict[str, dict] = {}
    tags: set[str] = set()
    for ep in endpoints:
        path = ep["path"]
        method = ep.get("method", "get").lower()
        tag = ep.get("tag", "default")
        tags.add(tag)
        if path not in paths:
            paths[path] = {}
        paths[path][method] = {
            "summary": html.escape(ep.get("summary", "")),
            "description": html.escape(ep.get("description", "")),
            "tag": tag,
            "parameters": ep.get("parameters", []),
            "responses": ep.get("responses", {"200": {"description": "Success"}}),
            "auth_required": ep.get("auth_required", True),
        }
    return {
        "title": title, "version": version, "base_url": base_url,
        "paths": paths, "path_count": len(paths),
        "operation_count": sum(len(v) for v in paths.values()),
        "tags": sorted(tags),
    }


def generate_curl_examples(endpoints: list[dict], base_url: str = "https://api.example.com") -> list[dict]:
    examples = []
    for ep in endpoints:
        method = ep.get("method", "GET").upper()
        path = ep["path"]
        curl = f"curl -X {method} '{base_url}{path}'"
        if ep.get("auth_required", True):
            curl += " -H 'Authorization: Bearer YOUR_TOKEN'"
        curl += " -H 'Content-Type: application/json'"
        examples.append({"path": path, "method": method, "curl": curl})
    return examples
