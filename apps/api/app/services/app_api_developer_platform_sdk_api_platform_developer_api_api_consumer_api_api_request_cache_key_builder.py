"""API Consumer Cache Key Builder — build deterministic cache keys for API responses."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class CacheKeyConfig:
    consumer_id: str
    include_query_params: bool = True
    include_headers: list[str] = field(default_factory=list)
    ignore_params: list[str] = field(default_factory=list)  # params to exclude
    prefix: str = "api"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCacheKeyBuilder:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CacheKeyConfig] = {}

    def configure(self, installation_id: str, config: CacheKeyConfig) -> CacheKeyConfig:
        if not installation_id: raise ValueError("installation_id is required")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def build_key(self, installation_id: str, consumer_id: str, method: str, path: str, query_params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> str:
        config = self._configs.get((installation_id, consumer_id))
        parts = [installation_id, consumer_id, config.prefix if config else "api", method.upper(), path]
        if query_params and (config is None or config.include_query_params):
            ignore = set(config.ignore_params) if config else set()
            filtered = {k: v for k, v in sorted(query_params.items()) if k not in ignore}
            if filtered: parts.append("&".join(f"{k}={v}" for k, v in filtered.items()))
        if headers and config and config.include_headers:
            for h in sorted(config.include_headers):
                val = headers.get(h, "")
                if val: parts.append(f"{h}:{val}")
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def get_config(self, installation_id: str, consumer_id: str) -> CacheKeyConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def list_configs(self, installation_id: str) -> list[CacheKeyConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
