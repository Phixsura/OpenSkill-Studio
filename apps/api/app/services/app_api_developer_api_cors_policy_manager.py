"""App API Developer CORS Policy Manager — manage cross-origin access policies."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_ORIGIN_RE = re.compile(r"^https?://[a-zA-Z0-9\-.:]+$")

@dataclass
class CORSPolicy:
    policy_id: str
    allowed_origins: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=lambda: ["GET"])
    allowed_headers: list[str] = field(default_factory=list)
    allow_credentials: bool = False
    max_age_seconds: int = 3600

class AppAPIDeveloperAPICORSPolicyManager:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], CORSPolicy] = {}

    def create(self, installation_id: str, policy_id: str, allowed_origins: list[str], allowed_methods: list[str] | None = None, allow_credentials: bool = False, max_age_seconds: int = 3600) -> CORSPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, policy_id)
        if key in self._policies: raise ValueError(f"Policy {policy_id} already exists")
        for origin in allowed_origins:
            if origin != "*" and not _ORIGIN_RE.match(origin):
                raise ValueError(f"Invalid origin: {origin}")
        if allow_credentials and "*" in allowed_origins:
            raise ValueError("Cannot use wildcard origin with credentials")
        p = CORSPolicy(policy_id=policy_id, allowed_origins=allowed_origins, allowed_methods=allowed_methods or ["GET"], allow_credentials=allow_credentials, max_age_seconds=max_age_seconds)
        self._policies[key] = p
        return p

    def check_origin(self, installation_id: str, policy_id: str, origin: str) -> bool:
        p = self._get(installation_id, policy_id)
        return "*" in p.allowed_origins or origin in p.allowed_origins

    def list_policies(self, installation_id: str) -> list[CORSPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]

    def delete(self, installation_id: str, policy_id: str) -> bool:
        key = (installation_id, policy_id)
        if key in self._policies:
            del self._policies[key]
            return True
        return False

    def _get(self, installation_id: str, policy_id: str) -> CORSPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None: raise KeyError(f"Policy {policy_id} not found")
        return p
