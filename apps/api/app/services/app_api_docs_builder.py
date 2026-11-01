"""API docs builder — generate API documentation for developer portal."""


def build_endpoint_docs(endpoints: list[dict]) -> list[dict]:
    """Build formatted endpoint documentation."""
    docs = []
    for ep in endpoints:
        doc = {
            "method": ep.get("method", "GET").upper(),
            "path": ep.get("path", ""),
            "summary": ep.get("summary", ""),
            "description": ep.get("description", ""),
            "auth_required": ep.get("auth_required", True),
            "scopes": ep.get("scopes", []),
            "parameters": ep.get("parameters", []),
            "request_body": ep.get("request_body"),
            "responses": ep.get("responses", {"200": "Success", "401": "Unauthorized"}),
            "example_curl": _build_curl(ep),
        }
        docs.append(doc)
    return docs


def _build_curl(ep: dict) -> str:
    method = ep.get("method", "GET").upper()
    path = ep.get("path", "/")
    curl = f'curl -X {method} "https://api.openskill.studio/api/v1{path}"'
    curl += ' \\\n  -H "Authorization: Bearer $TOKEN"'
    if method in ("POST", "PUT", "PATCH"):
        curl += ' \\\n  -H "Content-Type: application/json"'
        curl += " \\\n  -d '{}'"
    return curl


def build_docs_toc(endpoints: list[dict]) -> list[dict]:
    """Build table of contents grouped by resource."""
    resources: dict[str, list] = {}
    for ep in endpoints:
        parts = ep.get("path", "/").strip("/").split("/")
        resource = parts[0] if parts else "other"
        if resource not in resources:
            resources[resource] = []
        resources[resource].append({"method": ep.get("method", "GET"), "path": ep.get("path"), "summary": ep.get("summary")})
    return [{"resource": r, "endpoints": eps} for r, eps in sorted(resources.items())]
