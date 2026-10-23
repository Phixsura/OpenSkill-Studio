"""Multitenancy router — route requests to tenant-specific resources."""

import re

SUBDOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def resolve_tenant(*, host: str, path: str, header_tenant: str | None = None) -> dict:
    # Strategy 1: subdomain
    parts = host.split(".")
    if len(parts) >= 3 and SUBDOMAIN_RE.match(parts[0]):
        subdomain = parts[0]
        if subdomain not in ("www", "api", "app"):
            return {"tenant_id": subdomain, "strategy": "subdomain", "resolved": True}
    # Strategy 2: path prefix
    m = re.match(r"^/t/([a-z0-9-]+)/", path)
    if m:
        return {"tenant_id": m.group(1), "strategy": "path", "resolved": True}
    # Strategy 3: header
    if header_tenant:
        return {"tenant_id": header_tenant, "strategy": "header", "resolved": True}
    return {"tenant_id": None, "strategy": None, "resolved": False,
            "error": "Could not resolve tenant"}


def list_tenant_strategies() -> dict:
    return {
        "strategies": [
            {"id": "subdomain", "label": "Subdomain", "example": "acme.marketplace.dev", "priority": 1},
            {"id": "path", "label": "Path prefix", "example": "/t/acme/...", "priority": 2},
            {"id": "header", "label": "HTTP Header", "example": "X-Tenant-ID: acme", "priority": 3},
        ],
    }
