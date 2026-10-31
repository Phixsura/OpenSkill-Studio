"""App Webhook Secret Rotation — rotate webhook signing secrets.

Manages secret rotation:
- Schedule rotations with grace period
- Track rotation status
- Old secret remains valid during grace
- Per-installation scoped rotations
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SecretRotation:
    """A webhook secret rotation."""

    rotation_id: str
    old_secret_hash: str
    new_secret_hash: str
    grace_until: float
    completed: bool = False
    created_at: float = field(default_factory=time.time)

    @property
    def in_grace_period(self) -> bool:
        return not self.completed and time.time() < self.grace_until


class AppWebhookSecretRotation:
    """Rotate webhook signing secrets."""

    def __init__(self) -> None:
        self._rotations: dict[tuple[str, str], SecretRotation] = {}
        self._current_secrets: dict[str, str] = {}

    def initialize_secret(self, installation_id: str) -> str:
        """Generate initial secret. Returns raw secret."""
        if not installation_id:
            raise ValueError("installation_id is required")
        import hashlib
        raw = secrets.token_urlsafe(32)
        self._current_secrets[installation_id] = hashlib.sha256(raw.encode()).hexdigest()
        return raw

    def rotate(
        self, installation_id: str, rotation_id: str, grace_seconds: int = 3600,
    ) -> tuple[SecretRotation, str]:
        """Rotate to a new secret. Returns (rotation, new_raw_secret)."""
        import hashlib
        old_hash = self._current_secrets.get(installation_id)
        if old_hash is None:
            raise ValueError("No existing secret to rotate")
        if grace_seconds < 0:
            raise ValueError("grace_seconds must be non-negative")

        new_raw = secrets.token_urlsafe(32)
        new_hash = hashlib.sha256(new_raw.encode()).hexdigest()

        rotation = SecretRotation(
            rotation_id=rotation_id, old_secret_hash=old_hash,
            new_secret_hash=new_hash, grace_until=time.time() + grace_seconds,
        )
        self._rotations[(installation_id, rotation_id)] = rotation
        self._current_secrets[installation_id] = new_hash
        return rotation, new_raw

    def complete(self, installation_id: str, rotation_id: str) -> SecretRotation:
        key = (installation_id, rotation_id)
        r = self._rotations.get(key)
        if r is None:
            raise KeyError(f"Rotation {rotation_id} not found")
        r.completed = True
        return r

    def list_rotations(self, installation_id: str) -> list[SecretRotation]:
        return [r for (inst, _), r in self._rotations.items() if inst == installation_id]
