"""API mock server — create mock API endpoints for development."""

import json
import secrets


def create_mock_endpoint(*, path: str, method: str = "GET",
                           status_code: int = 200, response_body: dict | None = None,
                           delay_ms: int = 0) -> dict:
    if delay_ms > 10000:
        return {"error": "Max delay is 10000ms"}
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
    if method.upper() not in valid_methods:
        return {"error": f"Invalid method. Valid: {', '.join(sorted(valid_methods))}"}
    mock_id = f"mock_{secrets.token_urlsafe(6)}"
    return {
        "mock_id": mock_id,
        "path": path,
        "method": method.upper(),
        "status_code": status_code,
        "response_body": response_body or {"message": "Mock response"},
        "delay_ms": delay_ms,
        "url": f"https://mock.openskill.dev/{mock_id}{path}",
    }


def create_mock_collection(*, name: str, endpoints: list[dict]) -> dict:
    results = [create_mock_endpoint(**ep) for ep in endpoints]
    errors = [r for r in results if "error" in r]
    valid = [r for r in results if "error" not in r]
    base_url = f"https://mock.openskill.dev/col_{secrets.token_urlsafe(6)}"
    return {
        "collection_name": name,
        "base_url": base_url,
        "endpoints": valid,
        "errors": errors,
        "total_created": len(valid),
    }
