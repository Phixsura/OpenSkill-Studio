"""API endpoint registry — catalog all available API endpoints."""
from __future__ import annotations

ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/apps", "description": "List apps", "auth": True, "category": "apps"},
    {"method": "POST", "path": "/api/v1/apps", "description": "Create app", "auth": True, "category": "apps"},
    {"method": "GET", "path": "/api/v1/apps/:id", "description": "Get app", "auth": True, "category": "apps"},
    {"method": "PUT", "path": "/api/v1/apps/:id", "description": "Update app", "auth": True, "category": "apps"},
    {"method": "DELETE", "path": "/api/v1/apps/:id", "description": "Delete app", "auth": True, "category": "apps"},
    {"method": "GET", "path": "/api/v1/webhooks", "description": "List webhooks", "auth": True, "category": "webhooks"},
    {"method": "POST", "path": "/api/v1/webhooks", "description": "Create webhook", "auth": True, "category": "webhooks"},
    {"method": "GET", "path": "/api/v1/analytics", "description": "Get analytics", "auth": True, "category": "analytics"},
    {"method": "GET", "path": "/api/v1/health", "description": "Health check", "auth": False, "category": "system"},
    {"method": "GET", "path": "/api/v1/status", "description": "System status", "auth": False, "category": "system"},
]


def list_endpoints(*, category: str | None = None, auth_only: bool = False) -> list[dict]:
    result = ENDPOINTS
    if category:
        result = [e for e in result if e["category"] == category]
    if auth_only:
        result = [e for e in result if e["auth"]]
    return result


def search_endpoints(query: str) -> list[dict]:
    q = query.lower()
    return [e for e in ENDPOINTS if q in e["path"].lower() or q in e["description"].lower()]


def get_categories() -> list[dict]:
    cats: dict[str, int] = {}
    for e in ENDPOINTS:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(cats.items())]
