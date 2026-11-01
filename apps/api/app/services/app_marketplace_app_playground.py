"""Playground — interactive API testing environment for developers."""

import json


def create_playground_session(*, app_id: str, developer_id: str, api_base: str) -> dict:
    return {
        "app_id": app_id, "developer_id": developer_id, "api_base": api_base,
        "status": "active", "history": [],
    }


def execute_playground_request(*, session: dict, method: str, path: str,
                                  headers: dict | None = None, body: str | None = None) -> dict:
    full_url = f"{session['api_base']}{path}"
    # Simulated response
    return {
        "request": {"method": method, "url": full_url, "headers": headers or {}, "body": body},
        "response": {"status_code": 200, "body": json.dumps({"message": "OK"}), "headers": {"content-type": "application/json"}},
        "duration_ms": 42,
    }


def build_curl_command(*, method: str, url: str, headers: dict | None = None, body: str | None = None) -> str:
    parts = [f"curl -X {method}"]
    for k, v in (headers or {}).items():
        parts.append(f'-H "{k}: {v}"')
    if body:
        parts.append(f"-d '{body}'")
    parts.append(f'"{url}"')
    return " \\\n  ".join(parts)
