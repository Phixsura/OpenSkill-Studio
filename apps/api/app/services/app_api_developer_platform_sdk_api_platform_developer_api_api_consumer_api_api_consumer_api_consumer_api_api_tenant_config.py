"""Consumer API Tenant Config — manage per-tenant configuration overrides."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class TenantConfig:
    consumer_id: str
    config: dict[str, str | int | bool] = field(default_factory=dict)
    version: int = 1
    updated_at: datetime | None = None
    updated_by: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], TenantConfig] = {}
        self._history: dict[tuple[str, str], list[TenantConfig]] = {}

    def set(self, installation_id: str, consumer_id: str, key: str, value: str | int | bool, updated_by: str = "", now: datetime | None = None) -> TenantConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if isinstance(value, bool):
            pass  # bool check before int since isinstance(True, int) is True
        elif not isinstance(value, (str, int)):
            raise ValueError("Value must be str, int, or bool")
        k = (installation_id, consumer_id)
        if k not in self._configs:
            self._configs[k] = TenantConfig(consumer_id=consumer_id)
        cfg = self._configs[k]
        cfg.config[key] = value
        cfg.version += 1
        cfg.updated_at = now or datetime.utcnow()
        cfg.updated_by = updated_by
        # Track history
        if k not in self._history:
            self._history[k] = []
        self._history[k].append(TenantConfig(consumer_id=consumer_id, config=dict(cfg.config), version=cfg.version, updated_at=cfg.updated_at, updated_by=updated_by))
        return cfg

    def get(self, installation_id: str, consumer_id: str, key: str, default: str | int | bool | None = None) -> str | int | bool | None:
        cfg = self._configs.get((installation_id, consumer_id))
        if not cfg:
            return default
        return cfg.config.get(key, default)

    def get_all(self, installation_id: str, consumer_id: str) -> dict[str, str | int | bool]:
        cfg = self._configs.get((installation_id, consumer_id))
        return dict(cfg.config) if cfg else {}

    def delete(self, installation_id: str, consumer_id: str, key: str) -> None:
        cfg = self._configs.get((installation_id, consumer_id))
        if not cfg or key not in cfg.config:
            raise ValueError(f"Key {key} not found")
        del cfg.config[key]

    def get_version(self, installation_id: str, consumer_id: str) -> int:
        cfg = self._configs.get((installation_id, consumer_id))
        return cfg.version if cfg else 0

    def get_history(self, installation_id: str, consumer_id: str, limit: int = 10) -> list[TenantConfig]:
        return self._history.get((installation_id, consumer_id), [])[-limit:]
