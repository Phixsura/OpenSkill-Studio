"""Log level controller — dynamic log level management per service."""
from __future__ import annotations

LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fatal": 4}


class LogLevelController:
    def __init__(self, default_level: str = "info"):
        self._default = default_level
        self._overrides: dict[str, str] = {}

    def set_level(self, service: str, level: str) -> dict:
        if level not in LEVELS:
            return {"success": False, "error": f"invalid level: {level}"}
        self._overrides[service] = level
        return {"service": service, "level": level, "success": True}

    def get_level(self, service: str) -> str:
        return self._overrides.get(service, self._default)

    def reset(self, service: str) -> dict:
        removed = service in self._overrides
        self._overrides.pop(service, None)
        return {"service": service, "reset": removed, "level": self._default}

    def reset_all(self) -> dict:
        count = len(self._overrides)
        self._overrides.clear()
        return {"reset": count, "default_level": self._default}

    def should_log(self, service: str, level: str) -> bool:
        svc_level = LEVELS.get(self.get_level(service), 1)
        msg_level = LEVELS.get(level, 1)
        return msg_level >= svc_level

    def status(self) -> dict:
        return {"default": self._default, "overrides": dict(self._overrides),
                "services_overridden": len(self._overrides)}
