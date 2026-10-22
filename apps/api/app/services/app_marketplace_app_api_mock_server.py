"""API mock server — generate mock responses for app API testing."""

import json


def create_mock_endpoint(*, path: str, method: str, status_code: int = 200,
                            response_body: dict | None = None, delay_ms: int = 0) -> dict:
    return {"path": path, "method": method.upper(), "status_code": status_code,
            "response_body": response_body or {"message": "OK"}, "delay_ms": delay_ms}


def match_request(*, mocks: list[dict], method: str, path: str) -> dict | None:
    for mock in mocks:
        if mock["method"] == method.upper() and mock["path"] == path:
            return mock
    return None


def generate_mock_data(*, schema: dict) -> dict:
    data = {}
    for field, spec in schema.get("properties", {}).items():
        ftype = spec.get("type", "string")
        if ftype == "string":
            data[field] = f"mock_{field}"
        elif ftype == "integer":
            data[field] = 42
        elif ftype == "boolean":
            data[field] = True
        elif ftype == "array":
            data[field] = []
        elif ftype == "object":
            data[field] = {}
    return data


def build_mock_server_config(*, endpoints: list[dict], port: int = 3001) -> dict:
    return {"port": port, "endpoints": endpoints, "endpoint_count": len(endpoints),
            "cors_enabled": True, "log_requests": True}
