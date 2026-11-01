"""App API Developer SDK Download — track SDK download statistics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SDKDownload:
    language: str
    version: str
    download_count: int = 0

class AppAPIDeveloperSDKDownload:
    def __init__(self) -> None:
        self._downloads: dict[tuple[str, str, str], SDKDownload] = {}

    def record(self, installation_id: str, language: str, version: str) -> SDKDownload:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, language, version)
        if key not in self._downloads:
            self._downloads[key] = SDKDownload(language=language, version=version)
        self._downloads[key].download_count += 1
        return self._downloads[key]

    def top_languages(self, installation_id: str) -> list[dict]:
        lang_counts: dict[str, int] = {}
        for (inst, lang, _), d in self._downloads.items():
            if inst == installation_id:
                lang_counts[lang] = lang_counts.get(lang, 0) + d.download_count
        return sorted([{"language": l, "downloads": c} for l, c in lang_counts.items()], key=lambda x: x["downloads"], reverse=True)

    def total_downloads(self, installation_id: str) -> int:
        return sum(d.download_count for (inst, _, _), d in self._downloads.items() if inst == installation_id)

    def list_downloads(self, installation_id: str) -> list[SDKDownload]:
        return [d for (inst, _, _), d in self._downloads.items() if inst == installation_id]
