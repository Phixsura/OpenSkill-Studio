"""API playground — interactive API explorer for developers."""

import json
import secrets
from datetime import datetime


ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/apps", "description": "List all apps", "auth_required": False},
    {"method": "GET", "path": "/api/v1/apps/{app_id}", "description": "Get app details", "auth_required": False},
    {"method": "POST", "path": "/api/v1/apps", "description": "Create new app", "auth_required": True},
    {"method": "PUT", "path": "/api/v1/apps/{app_id}", "description": "Update app", "auth_required": True},
    {"method": "DELETE", "path": "/api/v1/apps/{app_id}", "description": "Delete app", "auth_required": True},
    {"method": "GET", "path": "/api/v1/apps/{app_id}/reviews", "description": "List reviews", "auth_required": False},
    {"method": "POST", "path": "/api/v1/webhooks", "description": "Create webhook", "auth_required": True},
]


def list_playground_endpoints(*, auth: bool | None = None) -> dict:
    results = ENDPOINTS
    if auth is not None:
        results = [e for e in results if e["auth_required"] == auth]
    methods = sorted(set(e["method"] for e in results))
    return {"endpoints": results, "total": len(results), "methods": methods}


def simulate_request(*, method: str, path: str, body: dict | None = None,
                       api_key: str | None = None) -> dict:
    endpoint = next((e for e in ENDPOINTS if e["method"] == method and e["path"] == path), None)
    if not endpoint:
        return {"status": 404, "body": {"error": {"code": "NOT_FOUND", "message": "Endpoint not found"}}}
    if endpoint["auth_required"] and not api_key:
        return {"status": 401, "body": {"error": {"code": "UNAUTHORIZED", "message": "API key required"}}}
    request_id = secrets.token_urlsafe(12)
    return {
        "status": 200,
        "body": {"data": {"message": f"Simulated {method} {path}", "request_id": request_id}},
        "headers": {"X-Request-Id": request_id, "Content-Type": "application/json"},
        "latency_ms": 42,
    }
