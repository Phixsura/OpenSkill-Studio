"""Error Code Registry — standardized error codes for the platform."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ErrorCode:
    code: str
    message: str
    http_status: int
    category: str
    docs_url: str = ""

_CODES: dict[str, ErrorCode] = {}

def register(code: str, message: str, http_status: int, category: str, docs: str = "") -> ErrorCode:
    ec = ErrorCode(code=code, message=message, http_status=http_status, category=category, docs_url=docs)
    _CODES[code] = ec
    return ec

def lookup(code: str) -> ErrorCode | None:
    return _CODES.get(code)

def list_by_category(category: str) -> list[ErrorCode]:
    return [c for c in _CODES.values() if c.category == category]

def get_all() -> list[ErrorCode]:
    return list(_CODES.values())

# Register standard codes
register("EXT_NOT_FOUND", "Extension not found", 404, "extension")
register("EXT_FORBIDDEN", "Access denied to extension", 403, "extension")
register("SANDBOX_LIMIT", "Sandbox resource limit exceeded", 429, "sandbox")
register("API_RATE_LIMIT", "API rate limit exceeded", 429, "api")
register("MANIFEST_INVALID", "Invalid manifest format", 400, "manifest")
register("AUTH_EXPIRED", "Authentication token expired", 401, "auth")
register("WEBHOOK_TIMEOUT", "Webhook delivery timeout", 504, "webhook")
register("DEPLOY_FAILED", "Deployment failed", 500, "deploy")
