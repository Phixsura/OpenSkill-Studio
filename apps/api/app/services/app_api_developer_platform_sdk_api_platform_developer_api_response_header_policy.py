"""API Response Header Policy — manage custom response headers per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class HeaderPolicy:
    policy_id: str
    endpoint: str
    headers: dict[str, str] = field(default_factory=dict)
    remove_headers: list[str] = field(default_factory=list)

_FORBIDDEN_HEADERS = {"transfer-encoding", "content-length", "host", "connection", "set-cookie", "access-control-allow-origin", "access-control-allow-credentials", "content-security-policy", "strict-transport-security", "x-frame-options"}
_HEADER_NAME_RE = re.compile(r"^[A-Za-z0-9\-]+$")
_HEADER_VALUE_RE = re.compile(r"^[\x20-\x7E\t]*$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], HeaderPolicy] = {}

    def set_policy(self, installation_id: str, endpoint: str, policy_id: str, headers: dict[str, str] | None = None, remove_headers: list[str] | None = None) -> HeaderPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        add_h = headers or {}
        rem_h = remove_headers or []
        for name in list(add_h.keys()) + rem_h:
            if not _HEADER_NAME_RE.match(name): raise ValueError(f"Invalid header name: {name}")
            if name.lower() in _FORBIDDEN_HEADERS: raise ValueError(f"Cannot modify forbidden header: {name}")
        for value in add_h.values():
            if not _HEADER_VALUE_RE.match(value): raise ValueError(f"Invalid header value (contains control chars)")
        policy = HeaderPolicy(policy_id=policy_id, endpoint=endpoint, headers=add_h, remove_headers=rem_h)
        self._policies[(installation_id, endpoint)] = policy
        return policy

    def apply_headers(self, installation_id: str, endpoint: str, response_headers: dict[str, str]) -> dict[str, str]:
        policy = self._policies.get((installation_id, endpoint))
        if policy is None: return dict(response_headers)
        result = dict(response_headers)
        for name in policy.remove_headers:
            result.pop(name, None)
            # Case-insensitive removal
            to_remove = [k for k in result if k.lower() == name.lower()]
            for k in to_remove: result.pop(k, None)
        result.update(policy.headers)
        return result

    def get_policy(self, installation_id: str, endpoint: str) -> HeaderPolicy | None:
        return self._policies.get((installation_id, endpoint))

    def list_policies(self, installation_id: str) -> list[HeaderPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]

    def remove_policy(self, installation_id: str, endpoint: str) -> bool:
        key = (installation_id, endpoint)
        if key in self._policies: del self._policies[key]; return True
        return False
