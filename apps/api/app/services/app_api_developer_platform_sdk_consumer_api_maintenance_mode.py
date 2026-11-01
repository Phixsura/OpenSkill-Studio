"""Consumer API Maintenance Mode — maintenance mode toggle with bypass keys."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class MaintenanceConfig:
    enabled: bool = False
    message: str = "Service is under maintenance"
    estimated_end: str = ""
    allowed_ips: list[str] = field(default_factory=list)
    bypass_keys: set[str] = field(default_factory=set)
    started_at: str = ""


@dataclass
class MaintenanceModeManager:
    """Manage API maintenance mode with bypass keys and IP allowlists."""

    _config: MaintenanceConfig = field(default_factory=MaintenanceConfig)
    _history: list[dict] = field(default_factory=list)

    def enable(self, message: str = "Service is under maintenance",
               estimated_end: str = "") -> dict:
        self._config.enabled = True
        self._config.message = message
        self._config.estimated_end = estimated_end
        self._config.started_at = datetime.now(timezone.utc).isoformat()
        self._history.append({"action": "enabled", "timestamp": self._config.started_at})
        logger.info("maintenance_enabled")
        return {"enabled": True, "message": message, "estimated_end": estimated_end}

    def disable(self) -> dict:
        was_enabled = self._config.enabled
        self._config.enabled = False
        self._config.started_at = ""
        self._history.append({"action": "disabled",
                               "timestamp": datetime.now(timezone.utc).isoformat()})
        logger.info("maintenance_disabled")
        return {"disabled": True, "was_enabled": was_enabled}

    def is_maintenance(self) -> bool:
        return self._config.enabled

    def check_access(self, ip: str = "", bypass_key: str = "") -> dict:
        if not self._config.enabled:
            return {"allowed": True, "reason": "not_in_maintenance"}
        if bypass_key and bypass_key in self._config.bypass_keys:
            return {"allowed": True, "reason": "bypass_key"}
        if ip and ip in self._config.allowed_ips:
            return {"allowed": True, "reason": "allowed_ip"}
        return {"allowed": False, "reason": "maintenance",
                "message": self._config.message,
                "estimated_end": self._config.estimated_end}

    def generate_bypass_key(self) -> dict:
        key = f"maint_{secrets.token_hex(16)}"
        self._config.bypass_keys.add(key)
        return {"bypass_key": key, "total_keys": len(self._config.bypass_keys)}

    def revoke_bypass_key(self, key: str) -> dict:
        self._config.bypass_keys.discard(key)
        return {"revoked": True}

    def add_allowed_ip(self, ip: str) -> dict:
        if ip not in self._config.allowed_ips:
            self._config.allowed_ips.append(ip)
        return {"ip": ip, "total_ips": len(self._config.allowed_ips)}

    def remove_allowed_ip(self, ip: str) -> dict:
        if ip in self._config.allowed_ips:
            self._config.allowed_ips.remove(ip)
            return {"removed": True}
        return {"removed": False}

    def get_status(self) -> dict:
        return {
            "enabled": self._config.enabled,
            "message": self._config.message,
            "estimated_end": self._config.estimated_end,
            "started_at": self._config.started_at,
            "allowed_ips": len(self._config.allowed_ips),
            "bypass_keys": len(self._config.bypass_keys),
        }

    def get_history(self, limit: int = 20) -> list[dict]:
        return self._history[-limit:]
