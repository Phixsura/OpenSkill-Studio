"""OpenAPI validator — validate OpenAPI spec structure."""

import html


REQUIRED_FIELDS = {"openapi", "info", "paths"}
REQUIRED_INFO = {"title", "version"}


def validate_openapi(*, spec: dict) -> dict:
    errors = []
    warnings = []
    for field in REQUIRED_FIELDS:
        if field not in spec:
            errors.append(f"Missing required field: {field}")
    info = spec.get("info", {})
    for field in REQUIRED_INFO:
        if field not in info:
            errors.append(f"Missing info.{field}")
    paths = spec.get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, op in methods.items():
            if method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
                continue
            has_summary = bool(op.get("summary") or op.get("description"))
            if not has_summary:
                warnings.append(f"{method.upper()} {path} missing summary/description")
            endpoints.append({"method": method.upper(), "path": path,
                              "operation_id": op.get("operationId"),
                              "has_summary": has_summary,
                              "tags": op.get("tags", [])})
    version = spec.get("openapi", "")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "version": version, "title": html.escape(info.get("title", "")),
            "endpoint_count": len(endpoints), "endpoints": endpoints}
