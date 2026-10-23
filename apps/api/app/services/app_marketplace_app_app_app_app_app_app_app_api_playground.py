"""API playground — build, validate, and simulate API requests."""
from __future__ import annotations
import json
import re
from urllib.parse import urlparse


METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")


def build_request(*, method: str, path: str, headers: dict | None = None,
                   body: str | None = None, base_url: str = "https://api.openskill.io") -> dict:
    method = method.upper()
    if method not in METHODS:
        return {"valid": False, "error": f"Invalid method: {method}"}
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        return {"valid": False, "error": "Invalid base URL scheme"}
    if not path.startswith("/"):
        path = f"/{path}"
    full_url = f"{base_url.rstrip('/')}{path}"
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    hdrs.update(headers or {})
    parsed_body = None
    if body and method in ("POST", "PUT", "PATCH"):
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError:
            return {"valid": False, "error": "Invalid JSON body"}
    curl = f"curl -X {method} '{full_url}'"
    for k, v in hdrs.items():
        curl += f" -H '{k}: {v}'"
    if parsed_body is not None:
        curl += f" -d '{json.dumps(parsed_body)}'"
    return {"valid": True, "method": method, "url": full_url, "headers": hdrs,
            "body": parsed_body, "curl": curl}


def simulate_response(request: dict) -> dict:
    if not request.get("valid"):
        return {"status": 400, "body": {"error": request.get("error", "Invalid request")}}
    method = request["method"]
    if method == "GET":
        return {"status": 200, "body": {"data": [], "meta": {"total": 0, "page": 1}},
                "headers": {"X-Request-Id": "sim-001"}}
    if method == "POST":
        return {"status": 201, "body": {"data": {"id": "sim_01JTEST", "created": True}},
                "headers": {"X-Request-Id": "sim-002"}}
    if method == "DELETE":
        return {"status": 204, "body": None, "headers": {"X-Request-Id": "sim-003"}}
    return {"status": 200, "body": {"data": {"updated": True}},
            "headers": {"X-Request-Id": "sim-004"}}
