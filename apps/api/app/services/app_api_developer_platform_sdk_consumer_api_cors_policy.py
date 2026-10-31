"""Consumer CORS Policy — per-consumer CORS configuration manager."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
ORIGIN_RE = re.compile(r"^https?://[\w.-]+(:\d+)?$|\*$")


@dataclass
class CorsConfig:
    consumer_id: str
    allowed_origins: list[str] = field(default_factory=list)
    allowed_methods: list[str] = field(default_factory=lambda: ["GET", "POST"])
    allowed_headers: list[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    expose_headers: list[str] = field(default_factory=list)
    max_age_seconds: int = 86400
    allow_credentials: bool = False


@dataclass
class CorsPolicyManager:
    """Manage per-consumer CORS policies."""

    _policies: dict[str, CorsConfig] = field(default_factory=dict)

    def set_policy(self, config: CorsConfig) -> dict:
        for origin in config.allowed_origins:
            if not ORIGIN_RE.match(origin):
                raise ValueError(f"Invalid origin: {origin}")
        for method in config.allowed_methods:
            if method not in VALID_METHODS:
                raise ValueError(f"Invalid method: {method}")
        if config.allow_credentials and "*" in config.allowed_origins:
            raise ValueError("Cannot use wildcard origin with credentials")
        if config.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative")
        self._policies[config.consumer_id] = config
        logger.info("cors_policy_set", consumer_id=config.consumer_id)
        return {"consumer_id": config.consumer_id, "origins": len(config.allowed_origins)}

    def check_origin(self, consumer_id: str, origin: str) -> dict:
        config = self._policies.get(consumer_id)
        if not config:
            return {"allowed": False, "reason": "no_policy"}
        if "*" in config.allowed_origins:
            return {"allowed": True, "reason": "wildcard"}
        if origin in config.allowed_origins:
            return {"allowed": True, "reason": "exact_match"}
        return {"allowed": False, "reason": "origin_not_allowed"}

    def get_headers(self, consumer_id: str, origin: str) -> dict:
        config = self._policies.get(consumer_id)
        if not config:
            return {}
        check = self.check_origin(consumer_id, origin)
        if not check["allowed"]:
            return {}
        headers = {
            "Access-Control-Allow-Origin": "*" if "*" in config.allowed_origins else origin,
            "Access-Control-Allow-Methods": ", ".join(config.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(config.allowed_headers),
            "Access-Control-Max-Age": str(config.max_age_seconds),
        }
        if config.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(config.expose_headers)
        if config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        return headers

    def get_policy(self, consumer_id: str) -> dict | None:
        config = self._policies.get(consumer_id)
        if not config:
            return None
        return {
            "consumer_id": config.consumer_id,
            "allowed_origins": config.allowed_origins,
            "allowed_methods": config.allowed_methods,
            "allowed_headers": config.allowed_headers,
            "max_age_seconds": config.max_age_seconds,
            "allow_credentials": config.allow_credentials,
        }

    def add_origin(self, consumer_id: str, origin: str) -> dict:
        config = self._policies.get(consumer_id)
        if not config:
            raise ValueError(f"No policy for {consumer_id}")
        if not ORIGIN_RE.match(origin):
            raise ValueError(f"Invalid origin: {origin}")
        if origin not in config.allowed_origins:
            config.allowed_origins.append(origin)
        return {"consumer_id": consumer_id, "origins": len(config.allowed_origins)}

    def remove_origin(self, consumer_id: str, origin: str) -> dict:
        config = self._policies.get(consumer_id)
        if not config:
            return {"removed": False}
        if origin in config.allowed_origins:
            config.allowed_origins.remove(origin)
            return {"removed": True}
        return {"removed": False}

    def list_policies(self) -> list[dict]:
        return [
            {"consumer_id": c.consumer_id, "origin_count": len(c.allowed_origins),
             "credentials": c.allow_credentials}
            for c in self._policies.values()
        ]
