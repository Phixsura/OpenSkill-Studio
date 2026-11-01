"""API docs generator — auto-generate comprehensive API documentation from routes."""


def generate_api_docs(*, routes: list[dict], base_url: str = "https://api.openskill.dev") -> dict:
    groups = {}
    for route in routes:
        tag = route.get("tag", "default")
        groups.setdefault(tag, []).append({
            "method": route.get("method", "GET").upper(),
            "path": route.get("path", "/"),
            "summary": route.get("summary", ""),
            "auth_required": route.get("auth_required", True),
            "parameters": route.get("parameters", []),
            "response_codes": route.get("response_codes", [200]),
        })
    return {
        "title": "OpenSkill Developer Platform API",
        "version": "v2",
        "base_url": base_url,
        "groups": groups,
        "total_endpoints": len(routes),
        "group_count": len(groups),
    }


def generate_curl_examples(*, routes: list[dict], base_url: str = "https://api.openskill.dev") -> list[dict]:
    examples = []
    for r in routes[:20]:
        method = r.get("method", "GET").upper()
        path = r.get("path", "/")
        curl = f"curl -X {method} {base_url}{path}"
        if r.get("auth_required", True):
            curl += ' -H "Authorization: Bearer $TOKEN"'
        if method in ("POST", "PUT", "PATCH"):
            curl += ' -H "Content-Type: application/json"'
        examples.append({"method": method, "path": path, "curl": curl})
    return examples


def build_api_reference_page(*, docs: dict, examples: list[dict]) -> dict:
    return {
        "page_type": "api_reference",
        "title": docs["title"],
        "version": docs["version"],
        "endpoint_count": docs["total_endpoints"],
        "groups": list(docs["groups"].keys()),
        "examples": examples[:10],
        "search_enabled": True,
        "try_it_enabled": True,
    }
