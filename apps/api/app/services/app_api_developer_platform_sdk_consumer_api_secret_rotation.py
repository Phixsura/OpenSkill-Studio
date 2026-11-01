"""Webhook Secret Rotation — automated secret rotation with grace period."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class SecretVersion:
    version: int
    secret: str
    created_at: float
    expires_at: float | None = None
    status: str = "active"  # active, grace, expired


@dataclass
class SecretRotation:
    """Manage webhook secret rotation with grace periods."""

    _webhooks: dict[str, list[SecretVersion]] = field(default_factory=dict)
    _grace_period_seconds: float = 3600.0  # 1 hour default

    def configure_grace(self, seconds: float) -> dict:
        if seconds < 0:
            raise ValueError("Grace period must be non-negative")
        self._grace_period_seconds = seconds
        return {"grace_period_seconds": seconds}

    def initialize(self, webhook_id: str, secret: str | None = None) -> dict:
        if webhook_id in self._webhooks and self._webhooks[webhook_id]:
            raise ValueError(f"Webhook {webhook_id} already initialized")
        actual_secret = secret or secrets.token_hex(32)
        version = SecretVersion(version=1, secret=actual_secret, created_at=0.0)
        self._webhooks[webhook_id] = [version]
        logger.info("secret_initialized", webhook_id=webhook_id)
        return {"webhook_id": webhook_id, "version": 1, "secret_prefix": actual_secret[:8]}

    def rotate(self, webhook_id: str, current_time: float = 0.0,
               new_secret: str | None = None) -> dict:
        versions = self._webhooks.get(webhook_id)
        if not versions:
            raise ValueError(f"Webhook {webhook_id} not initialized")
        # Move current active to grace
        for v in versions:
            if v.status == "active":
                v.status = "grace"
                v.expires_at = current_time + self._grace_period_seconds
        actual_secret = new_secret or secrets.token_hex(32)
        new_version = SecretVersion(
            version=versions[-1].version + 1,
            secret=actual_secret,
            created_at=current_time,
        )
        versions.append(new_version)
        logger.info("secret_rotated", webhook_id=webhook_id, version=new_version.version)
        return {"webhook_id": webhook_id, "new_version": new_version.version,
                "secret_prefix": actual_secret[:8],
                "grace_versions": sum(1 for v in versions if v.status == "grace")}

    def validate(self, webhook_id: str, secret: str, current_time: float = 0.0) -> dict:
        versions = self._webhooks.get(webhook_id)
        if not versions:
            return {"valid": False, "reason": "webhook_not_found"}
        # Expire grace period secrets
        for v in versions:
            if v.status == "grace" and v.expires_at and current_time > v.expires_at:
                v.status = "expired"
        # Check active first, then grace
        for v in versions:
            if v.status in ("active", "grace") and v.secret == secret:
                return {"valid": True, "version": v.version, "status": v.status}
        return {"valid": False, "reason": "secret_mismatch"}

    def get_versions(self, webhook_id: str) -> list[dict]:
        versions = self._webhooks.get(webhook_id, [])
        return [
            {"version": v.version, "status": v.status,
             "secret_prefix": v.secret[:8] + "...",
             "created_at": v.created_at}
            for v in versions
        ]

    def cleanup_expired(self, webhook_id: str, current_time: float = 0.0) -> dict:
        versions = self._webhooks.get(webhook_id, [])
        before = len(versions)
        for v in versions:
            if v.status == "grace" and v.expires_at and current_time > v.expires_at:
                v.status = "expired"
        self._webhooks[webhook_id] = [v for v in versions if v.status != "expired"]
        removed = before - len(self._webhooks[webhook_id])
        return {"removed": removed, "remaining": len(self._webhooks[webhook_id])}

    def get_active_secret(self, webhook_id: str) -> dict | None:
        versions = self._webhooks.get(webhook_id, [])
        for v in versions:
            if v.status == "active":
                return {"version": v.version, "secret": v.secret}
        return None
