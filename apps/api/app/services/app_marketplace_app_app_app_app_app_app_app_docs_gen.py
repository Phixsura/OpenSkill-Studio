"""Developer docs generator — auto-generate API documentation."""
from __future__ import annotations
import html


def generate_endpoint_doc(method: str, path: str, description: str,
                           params: list[dict], responses: dict) -> dict:
    param_docs = []
    for p in params:
        param_docs.append({"name": p["name"], "type": p.get("type", "string"),
                           "required": p.get("required", False),
                           "description": html.escape(p.get("description", ""))})
    resp_docs = {str(code): html.escape(desc) for code, desc in responses.items()}
    return {"method": method.upper(), "path": path,
            "description": html.escape(description),
            "parameters": param_docs, "responses": resp_docs,
            "param_count": len(param_docs)}


def build_docs_index(endpoints: list[dict]) -> dict:
    by_tag: dict[str, list[str]] = {}
    for ep in endpoints:
        tag = ep.get("tag", "default")
        by_tag.setdefault(tag, []).append(f"{ep['method']} {ep['path']}")
    return {"endpoints": endpoints, "total": len(endpoints),
            "tags": sorted(by_tag.keys()), "by_tag": by_tag,
            "tag_count": len(by_tag)}
