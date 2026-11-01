"""API explorer — interactive API documentation with try-it-out functionality."""


def build_api_explorer(*, endpoints: list[dict], base_url: str) -> dict:
    groups: dict[str, list] = {}
    for ep in endpoints:
        tag = ep.get("tag", "default")
        groups.setdefault(tag, []).append({
            "method": ep.get("method", "GET").upper(),
            "path": ep.get("path", "/"),
            "summary": ep.get("summary", ""),
            "parameters": ep.get("parameters", []),
            "try_url": f"{base_url}{ep.get('path', '/')}",
        })
    return {"groups": groups, "total_endpoints": len(endpoints), "base_url": base_url}


def generate_example_request(*, endpoint: dict) -> dict:
    params = {}
    for p in endpoint.get("parameters", []):
        if p.get("type") == "string":
            params[p["name"]] = f"example_{p['name']}"
        elif p.get("type") == "integer":
            params[p["name"]] = 1
        elif p.get("type") == "boolean":
            params[p["name"]] = True
    return {"method": endpoint.get("method", "GET"), "url": endpoint.get("try_url", ""),
            "params": params, "headers": {"Authorization": "Bearer <token>"}}


def generate_example_response(*, status: int = 200, schema: dict | None = None) -> dict:
    body = {}
    if schema:
        for field, spec in schema.get("properties", {}).items():
            t = spec.get("type", "string")
            body[field] = f"example_{field}" if t == "string" else 0 if t == "integer" else True if t == "boolean" else None
    return {"status": status, "body": body or {"message": "OK"}}
