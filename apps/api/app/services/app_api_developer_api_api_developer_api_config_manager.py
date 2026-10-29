"""App API Developer API Config Manager — manage runtime API configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
import copy
import time
import structlog

log = structlog.get_logger()

@dataclass
class ConfigSnapshot:
    version: int
    config: dict
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiConfigManager:
    def __init__(self) -> None:
        self._configs: dict[str, dict] = {}
        self._history: dict[str, list[ConfigSnapshot]] = {}
        self._version: dict[str, int] = {}

    def set(self, installation_id: str, key: str, value) -> dict:
        if not installation_id: raise ValueError("installation_id is required")
        config = self._configs.setdefault(installation_id, {})
        config[key] = value
        self._bump_version(installation_id)
        return config

    def get(self, installation_id: str, key: str, default=None):
        return self._configs.get(installation_id, {}).get(key, default)

    def get_all(self, installation_id: str) -> dict:
        return dict(self._configs.get(installation_id, {}))

    def delete(self, installation_id: str, key: str) -> bool:
        config = self._configs.get(installation_id, {})
        if key in config:
            del config[key]
            self._bump_version(installation_id)
            return True
        return False

    def snapshot(self, installation_id: str) -> ConfigSnapshot:
        ver = self._version.get(installation_id, 0)
        config = copy.deepcopy(self._configs.get(installation_id, {}))
        snap = ConfigSnapshot(version=ver, config=config)
        self._history.setdefault(installation_id, []).append(snap)
        return snap

    def history(self, installation_id: str, limit: int = 10) -> list[ConfigSnapshot]:
        return list(reversed(self._history.get(installation_id, [])[-limit:]))

    def version(self, installation_id: str) -> int:
        return self._version.get(installation_id, 0)

    def _bump_version(self, installation_id: str) -> None:
        self._version[installation_id] = self._version.get(installation_id, 0) + 1
