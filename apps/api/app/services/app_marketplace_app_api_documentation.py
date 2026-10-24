"""API documentation — generate and serve interactive API docs."""

import html


def build_api_docs(*, title: str, version: str, endpoints: list[dict],
                     base_url: str) -> dict:
    safe_title = html.escape(title)
    sections: dict[str, list] = {}
    for ep in endpoints:
        tag = ep.get("tag", "default")
        sections.setdefault(tag, []).append({
            "method": ep["method"].upper(),
            "path": ep["path"],
            "summary": ep.get("summary", ""),
            "parameters": ep.get("parameters", []),
            "responses": ep.get("responses", {"200": "Success"}),
            "auth_required": ep.get("auth_required", False),
        })
    return {
        "title": safe_title,
        "version": version,
        "base_url": base_url,
        "sections": [{"tag": k, "endpoints": v} for k, v in sections.items()],
        "total_endpoints": len(endpoints),
        "total_tags": len(sections),
    }


def search_docs(*, query: str, endpoints: list[dict]) -> dict:
    q = query.lower()
    matches = [ep for ep in endpoints
               if q in ep.get("path", "").lower() or q in ep.get("summary", "").lower()]
    return {"results": matches[:10], "total": len(matches), "query": query}
