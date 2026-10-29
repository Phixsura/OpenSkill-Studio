"""API CORS Policy — manage Cross-Origin Resource Sharing per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class CorsPolicy:
    policy_id: str
    endpoint: str
    allowed_origins: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: list[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    expose_headers: list[str] = field(default_factory=list)
    max_age_s: int = 86400
    allow_credentials: bool = False

_ORIGIN_RE = re.compile(r"^https?://[a-zA-Z0-9\-.:]+$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], CorsPolicy] = {}

    def set_policy(self, installation_id: str, policy: CorsPolicy) -> CorsPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if policy.allow_credentials and "*" in policy.allowed_origins:
            raise ValueError("Cannot use wildcard origin with credentials")
        for origin in policy.allowed_origins:
            if origin != "*" and not _ORIGIN_RE.match(origin):
                raise ValueError(f"Invalid origin: {origin}")
        if policy.max_age_s < 0: raise ValueError("max_age must be non-negative")
        self._policies[(installation_id, policy.endpoint)] = policy
        return policy

    def check_origin(self, installation_id: str, endpoint: str, origin: str) -> dict[str, str]:
        policy = self._policies.get((installation_id, endpoint))
        if policy is None: return {}
        if "*" in policy.allowed_origins or origin in policy.allowed_origins:
            headers = {
                "Access-Control-Allow-Origin": origin if policy.allow_credentials else (origin if "*" not in policy.allowed_origins else "*"),
                "Access-Control-Allow-Methods": ", ".join(policy.allowed_methods),
                "Access-Control-Allow-Headers": ", ".join(policy.allowed_headers),
                "Access-Control-Max-Age": str(policy.max_age_s),
            }
            if policy.allow_credentials: headers["Access-Control-Allow-Credentials"] = "true"
            if policy.expose_headers: headers["Access-Control-Expose-Headers"] = ", ".join(policy.expose_headers)
            return headers
        return {}

    def get_policy(self, installation_id: str, endpoint: str) -> CorsPolicy | None:
        return self._policies.get((installation_id, endpoint))

    def list_policies(self, installation_id: str) -> list[CorsPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
