"""Consumer API Key Rotation Scheduler — automated key rotation with scheduling."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ApiKey:
    key_id: str
    consumer_id: str
    key_value: str
    version: int = 1
    created_at: float = 0.0
    rotation_interval_days: int = 90
    last_rotated_at: float = 0.0
    auto_rotate: bool = True
    status: str = "active"  # active, pending_rotation, revoked


@dataclass
class KeyRotationScheduler:
    """Schedule and execute API key rotations."""

    _keys: dict[str, ApiKey] = field(default_factory=dict)
    _rotation_history: list[dict] = field(default_factory=list)

    def create_key(self, consumer_id: str, rotation_interval_days: int = 90,
                   auto_rotate: bool = True, current_time: float = 0.0) -> dict:
        key_id = f"key_{secrets.token_hex(6)}"
        key_value = f"sk_{secrets.token_hex(24)}"
        key = ApiKey(
            key_id=key_id, consumer_id=consumer_id, key_value=key_value,
            created_at=current_time, last_rotated_at=current_time,
            rotation_interval_days=rotation_interval_days,
            auto_rotate=auto_rotate,
        )
        self._keys[key_id] = key
        logger.info("api_key_created", key_id=key_id, consumer_id=consumer_id)
        return {"key_id": key_id, "key_value": key_value, "version": 1}

    def rotate(self, key_id: str, current_time: float = 0.0) -> dict:
        key = self._keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        if key.status == "revoked":
            raise ValueError("Cannot rotate revoked key")
        old_value = key.key_value
        new_value = f"sk_{secrets.token_hex(24)}"
        key.key_value = new_value
        key.version += 1
        key.last_rotated_at = current_time
        self._rotation_history.append({
            "key_id": key_id, "version": key.version,
            "rotated_at": current_time, "consumer_id": key.consumer_id,
        })
        logger.info("api_key_rotated", key_id=key_id, version=key.version)
        return {"key_id": key_id, "new_key_value": new_value,
                "version": key.version, "old_prefix": old_value[:8]}

    def check_due(self, current_time: float = 0.0) -> list[dict]:
        due = []
        for key in self._keys.values():
            if key.status != "active" or not key.auto_rotate:
                continue
            days_since = (current_time - key.last_rotated_at) / 86400
            if days_since >= key.rotation_interval_days:
                due.append({
                    "key_id": key.key_id,
                    "consumer_id": key.consumer_id,
                    "days_since_rotation": round(days_since, 1),
                    "interval_days": key.rotation_interval_days,
                })
        return due

    def revoke(self, key_id: str) -> dict:
        key = self._keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        key.status = "revoked"
        return {"key_id": key_id, "revoked": True}

    def get_key_info(self, key_id: str) -> dict | None:
        key = self._keys.get(key_id)
        if not key:
            return None
        return {
            "key_id": key.key_id, "consumer_id": key.consumer_id,
            "version": key.version, "status": key.status,
            "auto_rotate": key.auto_rotate,
            "rotation_interval_days": key.rotation_interval_days,
            "key_prefix": key.key_value[:8] + "...",
        }

    def list_keys(self, consumer_id: str | None = None) -> list[dict]:
        keys = list(self._keys.values())
        if consumer_id:
            keys = [k for k in keys if k.consumer_id == consumer_id]
        return [self.get_key_info(k.key_id) for k in keys]

    def get_rotation_history(self, key_id: str | None = None, limit: int = 20) -> list[dict]:
        history = self._rotation_history
        if key_id:
            history = [h for h in history if h["key_id"] == key_id]
        return history[-limit:]

    def get_stats(self) -> dict:
        keys = list(self._keys.values())
        return {
            "total_keys": len(keys),
            "active": sum(1 for k in keys if k.status == "active"),
            "revoked": sum(1 for k in keys if k.status == "revoked"),
            "auto_rotate_enabled": sum(1 for k in keys if k.auto_rotate),
            "total_rotations": len(self._rotation_history),
        }
