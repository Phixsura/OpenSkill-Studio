"""App CORS Policy — manage Cross-Origin Resource Sharing rules.

Manages CORS policies:
- Define allowed origins, methods, headers
- Evaluate CORS preflight requests
- Per-installation scoped policies
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CORSPolicy:
    """A CORS policy configuration."""

    policy_id: str
    allowed_origins: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: list[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    allow_credentials: bool = False
    max_age_seconds: int = 3600

    @property
    def allows_all_origins(self) -> bool:
        return "*" in self.allowed_origins


class AppCORSPolicy:
    """Manage Cross-Origin Resource Sharing rules."""

    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], CORSPolicy] = {}

    def set_policy(
        self, installation_id: str, policy_id: str,
        allowed_origins: list[str], allowed_methods: list[str] | None = None,
        allowed_headers: list[str] | None = None,
        allow_credentials: bool = False, max_age_seconds: int = 3600,
    ) -> CORSPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not allowed_origins:
            raise ValueError("at least one origin required")

        # Credentials + wildcard origin is forbidden per spec
        if allow_credentials and "*" in allowed_origins:
            raise ValueError("Cannot use wildcard origin with credentials")

        policy = CORSPolicy(
            policy_id=policy_id, allowed_origins=allowed_origins,
            allowed_methods=allowed_methods or ["GET", "POST", "PUT", "DELETE"],
            allowed_headers=allowed_headers or ["Content-Type", "Authorization"],
            allow_credentials=allow_credentials, max_age_seconds=max_age_seconds,
        )
        self._policies[(installation_id, policy_id)] = policy
        return policy

    def check_origin(self, installation_id: str, origin: str) -> CORSPolicy | None:
        """Find a policy that allows this origin."""
        for (inst, _), policy in self._policies.items():
            if inst != installation_id:
                continue
            if policy.allows_all_origins or origin in policy.allowed_origins:
                return policy
        return None

    def evaluate_preflight(
        self, installation_id: str, origin: str, method: str,
        request_headers: list[str] | None = None,
    ) -> dict:
        """Evaluate a CORS preflight request. Returns response headers."""
        policy = self.check_origin(installation_id, origin)
        if policy is None:
            return {"allowed": False}

        if method.upper() not in policy.allowed_methods:
            return {"allowed": False}

        if request_headers:
            allowed_lower = [h.lower() for h in policy.allowed_headers]
            for h in request_headers:
                if h.lower() not in allowed_lower:
                    return {"allowed": False}

        return {
            "allowed": True,
            "origin": origin if not policy.allows_all_origins else "*",
            "methods": ", ".join(policy.allowed_methods),
            "headers": ", ".join(policy.allowed_headers),
            "credentials": policy.allow_credentials,
            "max_age": policy.max_age_seconds,
        }

    def list_policies(self, installation_id: str) -> list[CORSPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
