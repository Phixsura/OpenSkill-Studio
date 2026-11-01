"""OpenAPI generator — auto-generate OpenAPI specs from app endpoint definitions."""


def generate_openapi_spec(*, app: dict, endpoints: list[dict], version: str = "3.0.3") -> dict:
    paths = {}
    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "get").lower()
        paths.setdefault(path, {})[method] = {
            "summary": ep.get("summary", ""),
            "operationId": ep.get("operation_id", f"{method}_{path.replace('/', '_').strip('_')}"),
            "parameters": ep.get("parameters", []),
            "responses": {"200": {"description": ep.get("success_description", "Success")}},
            "tags": ep.get("tags", []),
        }
    return {
        "openapi": version,
        "info": {"title": f"{app['name']} API", "version": app.get("version", "1.0.0"),
                  "description": app.get("description", "")},
        "paths": paths,
        "servers": [{"url": f"https://api.openskill.dev/apps/{app.get('slug', '')}/v1"}],
    }


def validate_openapi_spec(*, spec: dict) -> dict:
    errors = []
    if "openapi" not in spec:
        errors.append("Missing 'openapi' version field")
    if "info" not in spec:
        errors.append("Missing 'info' section")
    elif "title" not in spec.get("info", {}):
        errors.append("Missing 'info.title'")
    if "paths" not in spec:
        errors.append("Missing 'paths' section")
    return {"valid": len(errors) == 0, "errors": errors, "endpoint_count": len(spec.get("paths", {}))}


def render_openapi_yaml_header(*, spec: dict) -> str:
    info = spec.get("info", {})
    lines = [f"openapi: '{spec.get('openapi', '3.0.3')}'", "info:",
             f"  title: '{info.get('title', '')}'", f"  version: '{info.get('version', '1.0.0')}'",
             f"  description: '{info.get('description', '')}'",
             f"paths: # {len(spec.get('paths', {}))} endpoints"]
    return "\n".join(lines)
