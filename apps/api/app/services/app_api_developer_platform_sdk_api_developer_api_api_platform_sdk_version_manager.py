"""App API Developer Platform SDK Version Manager — manage SDK releases and adoption."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SDKVersion:
    version: str
    language: str
    status: str = "stable"  # "stable", "beta", "deprecated", "eol"
    downloads: int = 0
    active_users: int = 0
    released_at: float = 0.0

    @property
    def adoption_score(self) -> int:
        return self.downloads + self.active_users * 10

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str, str], SDKVersion] = {}

    def register(self, installation_id: str, version: str, language: str, status: str = "stable") -> SDKVersion:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("stable", "beta", "deprecated", "eol"): raise ValueError("invalid status")
        key = (installation_id, language, version)
        v = SDKVersion(version=version, language=language, status=status)
        self._versions[key] = v
        return v

    def record_download(self, installation_id: str, language: str, version: str) -> SDKVersion:
        key = (installation_id, language, version)
        v = self._versions.get(key)
        if v is None: raise KeyError(f"No SDK {language} {version}")
        v.downloads += 1
        return v

    def latest_stable(self, installation_id: str, language: str) -> SDKVersion | None:
        versions = [v for (inst, lang, _), v in self._versions.items() if inst == installation_id and lang == language and v.status == "stable"]
        return max(versions, key=lambda v: v.version) if versions else None

    def deprecated_in_use(self, installation_id: str) -> list[SDKVersion]:
        return [v for (inst, _, _), v in self._versions.items() if inst == installation_id and v.status in ("deprecated", "eol") and v.active_users > 0]

    def by_language(self, installation_id: str) -> dict[str, list[SDKVersion]]:
        result: dict[str, list[SDKVersion]] = {}
        for (inst, lang, _), v in self._versions.items():
            if inst == installation_id: result.setdefault(lang, []).append(v)
        return result

    def all_versions(self, installation_id: str) -> list[SDKVersion]:
        return [v for (inst, _, _), v in self._versions.items() if inst == installation_id]
