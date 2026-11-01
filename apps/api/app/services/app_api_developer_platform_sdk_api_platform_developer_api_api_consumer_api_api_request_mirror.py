"""API Consumer Request Mirror — mirror API requests to secondary endpoints for testing."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog
from urllib.parse import urlparse

log = structlog.get_logger()

@dataclass
class MirrorConfig:
    consumer_id: str
    mirror_url: str
    sample_rate: float = 1.0  # 0.0-1.0
    enabled: bool = True
    include_body: bool = True

@dataclass
class MirrorResult:
    request_id: str
    mirrored: bool
    mirror_status: int = 0
    mirror_latency_ms: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirror:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], MirrorConfig] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def configure(self, installation_id: str, config: MirrorConfig) -> MirrorConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0.0 <= config.sample_rate <= 1.0: raise ValueError("sample_rate must be 0.0-1.0")
        parsed = urlparse(config.mirror_url)
        if parsed.scheme not in ("https",): raise ValueError("mirror_url must use HTTPS")
        if not parsed.hostname: raise ValueError("mirror_url must have a hostname")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def should_mirror(self, installation_id: str, consumer_id: str, request_hash: int) -> bool:
        config = self._configs.get((installation_id, consumer_id))
        if config is None or not config.enabled: return False
        if config.sample_rate >= 1.0: return True
        return (request_hash % 10000) < int(config.sample_rate * 10000)

    def record_mirror(self, installation_id: str, result: MirrorResult) -> None:
        stats = self._stats.setdefault(installation_id, {"mirrored": 0, "failed": 0})
        if result.mirrored:
            stats["mirrored"] += 1
            if result.mirror_status >= 400: stats["failed"] += 1

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"mirrored": 0, "failed": 0})

    def list_configs(self, installation_id: str) -> list[MirrorConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
