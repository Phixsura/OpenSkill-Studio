"""App API Developer App Config — manage app-level configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AppConfig:
    app_id: str
    name: str
    settings: dict[str, str] = field(default_factory=dict)
    feature_flags: dict[str, bool] = field(default_factory=dict)

class AppAPIDeveloperAppConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], AppConfig] = {}

    def create(self, installation_id: str, app_id: str, name: str) -> AppConfig:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, app_id)
        if key in self._configs: raise ValueError(f"App {app_id} exists")
        c = AppConfig(app_id=app_id, name=name)
        self._configs[key] = c
        return c

    def set_setting(self, installation_id: str, app_id: str, key: str, value: str) -> AppConfig:
        c = self._get(installation_id, app_id)
        c.settings[key] = value
        return c

    def set_flag(self, installation_id: str, app_id: str, flag: str, enabled: bool) -> AppConfig:
        c = self._get(installation_id, app_id)
        c.feature_flags[flag] = enabled
        return c

    def get_config(self, installation_id: str, app_id: str) -> AppConfig:
        return self._get(installation_id, app_id)

    def list_apps(self, installation_id: str) -> list[AppConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def _get(self, installation_id: str, app_id: str) -> AppConfig:
        c = self._configs.get((installation_id, app_id))
        if c is None: raise KeyError(f"App {app_id} not found")
        return c
