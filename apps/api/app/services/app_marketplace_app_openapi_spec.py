"""OpenAPI spec — generate OpenAPI 3.0 specification for app APIs."""

import json
import re


def generate_openapi_spec(*, app_name: str, version: str, base_url: str,
                            endpoints: list[dict]) -> dict:
    safe_name = re.sub(r"[^a-zA-Z0-9 ]", "", app_name)
    paths: dict = {}
    for ep in endpoints:
        path = ep["path"]
        method = ep.get("method", "get").lower()
        operation = {
            "summary": ep.get("description", ""),
            "operationId": ep.get("operation_id", f"{method}_{path.replace('/', '_')}"),
            "responses": {"200": {"description": "Success"}},
        }
        if ep.get("parameters"):
            operation["parameters"] = ep["parameters"]
        if ep.get("request_body"):
            operation["requestBody"] = {"content": {"application/json": {"schema": ep["request_body"]}}}
        paths.setdefault(path, {})[method] = operation
    spec = {
        "openapi": "3.0.3",
        "info": {"title": safe_name, "version": version},
        "servers": [{"url": base_url}],
        "paths": paths,
    }
    return {"spec": spec, "spec_json": json.dumps(spec, indent=2),
            "endpoint_count": len(endpoints), "path_count": len(paths)}
