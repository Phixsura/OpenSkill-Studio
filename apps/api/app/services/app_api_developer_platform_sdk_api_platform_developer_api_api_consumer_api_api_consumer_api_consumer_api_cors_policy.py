"""Consumer API CORS Policy — manage Cross-Origin Resource Sharing per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

ORIGIN_RE = re.compile(r"^https?://[a-zA-Z0-9._-]+(:\d+)?$")

@dataclass
class CORSPolicy:
    consumer_id: str
    allowed_origins: list[str] = field(default_factory=list)  # ["https://app.example.com"]
    allowed_methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: list[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    expose_headers: list[str] = field(default_factory=list)
    max_age_seconds: int = 86400
    allow_credentials: bool = False

@dataclass
class CORSCheckResult:
    allowed: bool
    origin: str
    headers: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], CORSPolicy] = {}

    def set_policy(self, installation_id: str, policy: CORSPolicy) -> CORSPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        for origin in policy.allowed_origins:
            if origin != "*" and not ORIGIN_RE.match(origin):
                raise ValueError(f"Invalid origin: {origin}")
        if policy.allow_credentials and "*" in policy.allowed_origins:
            raise ValueError("Cannot use wildcard origin with credentials")
        self._policies[(installation_id, policy.consumer_id)] = policy
        return policy

    def check(self, installation_id: str, consumer_id: str, origin: str, method: str) -> CORSCheckResult:
        policy = self._policies.get((installation_id, consumer_id))
        if not policy:
            return CORSCheckResult(allowed=False, origin=origin)
        # Check origin
        origin_ok = "*" in policy.allowed_origins or origin in policy.allowed_origins
        if not origin_ok:
            return CORSCheckResult(allowed=False, origin=origin)
        # Check method
        if method.upper() not in [m.upper() for m in policy.allowed_methods]:
            return CORSCheckResult(allowed=False, origin=origin)
        headers: dict[str, str] = {
            "Access-Control-Allow-Origin": origin if policy.allow_credentials else ("*" if "*" in policy.allowed_origins else origin),
            "Access-Control-Allow-Methods": ", ".join(policy.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(policy.allowed_headers),
            "Access-Control-Max-Age": str(policy.max_age_seconds),
        }
        if policy.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        if policy.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(policy.expose_headers)
        return CORSCheckResult(allowed=True, origin=origin, headers=headers)

    def get_policy(self, installation_id: str, consumer_id: str) -> CORSPolicy | None:
        return self._policies.get((installation_id, consumer_id))
