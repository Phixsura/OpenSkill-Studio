"""App API Developer SDK Version Tracker — track SDK versions across consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class SDKVersionInfo:
    consumer_id: str
    sdk_name: str
    sdk_version: str
    language: str
    last_seen_at: float = field(default_factory=time.time)
    request_count: int = 0

class AppAPIDeveloperAPISDKVersionTracker:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], SDKVersionInfo] = {}

    def track(self, installation_id: str, consumer_id: str, sdk_name: str, sdk_version: str, language: str) -> SDKVersionInfo:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._versions:
            self._versions[key] = SDKVersionInfo(consumer_id=consumer_id, sdk_name=sdk_name, sdk_version=sdk_version, language=language)
        v = self._versions[key]
        v.sdk_version = sdk_version
        v.last_seen_at = time.time()
        v.request_count += 1
        return v

    def by_version(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), v in self._versions.items():
            if inst == installation_id:
                counts[v.sdk_version] = counts.get(v.sdk_version, 0) + 1
        return counts

    def outdated(self, installation_id: str, latest_version: str) -> list[SDKVersionInfo]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id and v.sdk_version != latest_version]

    def by_language(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), v in self._versions.items():
            if inst == installation_id:
                counts[v.language] = counts.get(v.language, 0) + 1
        return counts
