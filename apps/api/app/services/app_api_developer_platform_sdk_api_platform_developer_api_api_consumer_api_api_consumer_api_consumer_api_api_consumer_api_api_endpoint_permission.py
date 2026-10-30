"""Consumer API Endpoint Permission — fine-grained endpoint access control."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointPermission:
    permission_id: str
    consumer_id: str
    endpoint_path: str
    method: str  # "GET", "POST", etc. or "*" for all
    allowed: bool = True
    rate_limit_override: int | None = None  # per-consumer per-endpoint override

@dataclass
class PermissionCheckResult:
    allowed: bool
    consumer_id: str
    endpoint: str
    method: str
    reason: str
    rate_limit: int | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiEndpointPermission:
    def __init__(self, default_allowed: bool = True) -> None:
        self._permissions: dict[tuple[str, str, str, str], EndpointPermission] = {}
        self._default = default_allowed

    def set_permission(self, installation_id: str, perm: EndpointPermission) -> EndpointPermission:
        if not installation_id:
            raise ValueError("installation_id is required")
        if perm.method != "*" and perm.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {perm.method}")
        key = (installation_id, perm.consumer_id, perm.endpoint_path, perm.method.upper())
        self._permissions[key] = perm
        return perm

    def check(self, installation_id: str, consumer_id: str, endpoint_path: str, method: str) -> PermissionCheckResult:
        # Check specific method first
        key = (installation_id, consumer_id, endpoint_path, method.upper())
        perm = self._permissions.get(key)
        if perm:
            return PermissionCheckResult(allowed=perm.allowed, consumer_id=consumer_id, endpoint=endpoint_path, method=method, reason="explicit" if perm.allowed else "denied", rate_limit=perm.rate_limit_override)
        # Check wildcard method
        wildcard_key = (installation_id, consumer_id, endpoint_path, "*")
        perm = self._permissions.get(wildcard_key)
        if perm:
            return PermissionCheckResult(allowed=perm.allowed, consumer_id=consumer_id, endpoint=endpoint_path, method=method, reason="wildcard" if perm.allowed else "wildcard_denied", rate_limit=perm.rate_limit_override)
        # Default
        return PermissionCheckResult(allowed=self._default, consumer_id=consumer_id, endpoint=endpoint_path, method=method, reason="default_allow" if self._default else "default_deny")

    def revoke(self, installation_id: str, consumer_id: str, endpoint_path: str, method: str) -> None:
        key = (installation_id, consumer_id, endpoint_path, method.upper())
        if key not in self._permissions:
            raise ValueError("Permission not found")
        del self._permissions[key]

    def list_permissions(self, installation_id: str, consumer_id: str) -> list[EndpointPermission]:
        return [p for (inst, cid, _, _), p in self._permissions.items() if inst == installation_id and cid == consumer_id]
