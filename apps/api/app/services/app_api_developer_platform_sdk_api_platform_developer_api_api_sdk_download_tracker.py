"""API SDK Download Tracker — track SDK downloads and version adoption."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DownloadRecord:
    sdk_name: str
    version: str
    language: str  # "python", "typescript", "go", "java", "ruby"
    platform: str = ""  # "npm", "pypi", "maven", "rubygems"
    downloads: int = 0

VALID_LANGUAGES = {"python", "typescript", "javascript", "go", "java", "ruby", "csharp", "php", "rust", "swift"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTracker:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], DownloadRecord] = {}

    def record_download(self, installation_id: str, sdk_name: str, version: str, language: str, count: int = 1, platform: str = "") -> DownloadRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if language not in VALID_LANGUAGES: raise ValueError(f"Invalid language: {language}")
        if count < 1: raise ValueError("count must be >= 1")
        key = (installation_id, sdk_name, version)
        rec = self._records.get(key)
        if rec is None:
            rec = DownloadRecord(sdk_name=sdk_name, version=version, language=language, platform=platform)
            self._records[key] = rec
        rec.downloads += count
        return rec

    def total_downloads(self, installation_id: str, sdk_name: str | None = None) -> int:
        return sum(r.downloads for (inst, name, _), r in self._records.items()
                   if inst == installation_id and (sdk_name is None or name == sdk_name))

    def by_version(self, installation_id: str, sdk_name: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for (inst, name, ver), r in self._records.items():
            if inst == installation_id and name == sdk_name:
                result[ver] = r.downloads
        return result

    def by_language(self, installation_id: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for (inst, _, _), r in self._records.items():
            if inst == installation_id:
                result[r.language] = result.get(r.language, 0) + r.downloads
        return result

    def latest_version(self, installation_id: str, sdk_name: str) -> str | None:
        versions = [v for (inst, name, v) in self._records if inst == installation_id and name == sdk_name]
        return sorted(versions)[-1] if versions else None

    def sdk_count(self, installation_id: str) -> int:
        return len({name for (inst, name, _) in self._records if inst == installation_id})
