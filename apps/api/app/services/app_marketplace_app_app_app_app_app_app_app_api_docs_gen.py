"""API documentation generator — generate OpenAPI-style docs from endpoints."""
from __future__ import annotations


def generate_docs(endpoints: list[dict], title: str = "API", version: str = "1.0") -> dict:
    paths = {}
    tags = set()
    for ep in endpoints:
        path = ep["path"]
        method = ep.get("method", "GET").lower()
        tag = ep.get("tag", "default")
        tags.add(tag)
        if path not in paths:
            paths[path] = {}
        paths[path][method] = {
            "summary": ep.get("summary", ""),
            "tag": tag,
            "parameters": ep.get("parameters", []),
            "responses": ep.get("responses", {"200": {"description": "Success"}}),
        }
    return {"title": title, "version": version, "paths": paths,
            "total_endpoints": len(endpoints), "tags": sorted(tags)}


def coverage_report(endpoints: list[dict]) -> dict:
    documented = sum(1 for e in endpoints if e.get("summary"))
    with_examples = sum(1 for e in endpoints if e.get("example"))
    total = len(endpoints)
    return {"total": total, "documented": documented,
            "with_examples": with_examples,
            "doc_coverage_pct": round(documented / max(total, 1) * 100, 1),
            "example_coverage_pct": round(with_examples / max(total, 1) * 100, 1)}
