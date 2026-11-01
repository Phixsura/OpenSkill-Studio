"""App API Developer SDK Download Tracker — track SDK downloads by version/language."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SDKDownload:
    sdk_name: str
    version: str
    language: str
    downloads: int = 0

class AppAPIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTracker:
    def __init__(self) -> None:
        self._downloads: dict[tuple[str, str, str, str], SDKDownload] = {}

    def record(self, installation_id: str, sdk_name: str, version: str, language: str, count: int = 1) -> SDKDownload:
        if not installation_id: raise ValueError("installation_id is required")
        if count < 1: raise ValueError("count must be positive")
        key = (installation_id, sdk_name, version, language)
        if key not in self._downloads:
            self._downloads[key] = SDKDownload(sdk_name=sdk_name, version=version, language=language)
        self._downloads[key].downloads += count
        return self._downloads[key]

    def total_downloads(self, installation_id: str) -> int:
        return sum(d.downloads for k, d in self._downloads.items() if k[0] == installation_id)

    def by_language(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for k, d in self._downloads.items():
            if k[0] == installation_id: counts[d.language] = counts.get(d.language, 0) + d.downloads
        return counts

    def by_version(self, installation_id: str, sdk_name: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for k, d in self._downloads.items():
            if k[0] == installation_id and d.sdk_name == sdk_name: counts[d.version] = counts.get(d.version, 0) + d.downloads
        return counts

    def popular_sdks(self, installation_id: str, limit: int = 5) -> list[tuple[str, int]]:
        sdk_totals: dict[str, int] = {}
        for k, d in self._downloads.items():
            if k[0] == installation_id: sdk_totals[d.sdk_name] = sdk_totals.get(d.sdk_name, 0) + d.downloads
        return sorted(sdk_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
