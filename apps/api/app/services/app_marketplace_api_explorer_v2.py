"""API explorer v2 — endpoint testing with response schema validation."""


def build_endpoint_card(*, method: str, path: str, summary: str,
                           parameters: list[dict], auth_required: bool) -> dict:
    return {"method": method.upper(), "path": path, "summary": summary,
            "parameters": parameters, "auth_required": auth_required,
            "curl_example": _build_curl(method, path, auth_required)}


def _build_curl(method: str, path: str, auth: bool) -> str:
    cmd = f"curl -X {method.upper()} https://api.openskill.dev{path}"
    if auth:
        cmd += ' -H "Authorization: Bearer $TOKEN"'
    return cmd


def validate_response_schema(*, response: dict, expected_schema: dict) -> dict:
    errors = []
    for field, spec in expected_schema.get("properties", {}).items():
        if spec.get("required") and field not in response:
            errors.append(f"Missing required field: {field}")
        if field in response:
            expected_type = spec.get("type", "string")
            actual_type = type(response[field]).__name__
            type_map = {"string": "str", "integer": "int", "boolean": "bool", "array": "list", "object": "dict"}
            if type_map.get(expected_type) and actual_type != type_map[expected_type]:
                errors.append(f"Field '{field}': expected {expected_type}, got {actual_type}")
    return {"valid": len(errors) == 0, "errors": errors}


def generate_sample_request(*, endpoint: dict) -> dict:
    params = {}
    for p in endpoint.get("parameters", []):
        ptype = p.get("type", "string")
        if ptype == "string":
            params[p["name"]] = f"example_{p['name']}"
        elif ptype == "integer":
            params[p["name"]] = 1
        elif ptype == "boolean":
            params[p["name"]] = True
    return {"method": endpoint.get("method", "GET"), "path": endpoint.get("path", "/"),
            "params": params, "headers": {"Content-Type": "application/json"}}
