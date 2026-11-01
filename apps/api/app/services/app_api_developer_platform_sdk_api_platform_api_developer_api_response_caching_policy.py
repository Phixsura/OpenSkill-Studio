"""App API Developer API Response Caching Policy — manage caching policies per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CachingPolicy:
    endpoint: str
    ttl_seconds: int
    cache_control: str  # "public", "private", "no-cache", "no-store"
    vary_headers: list[str]
    stale_while_revalidate: int = 0

    @property
    def is_cacheable(self) -> bool:
        return self.cache_control not in ("no-cache", "no-store")

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], CachingPolicy] = {}

    def set_policy(self, installation_id: str, endpoint: str, ttl_seconds: int, cache_control: str = "public", vary_headers: list[str] | None = None, stale_while_revalidate: int = 0) -> CachingPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if cache_control not in ("public", "private", "no-cache", "no-store"): raise ValueError("invalid cache_control")
        if ttl_seconds < 0: raise ValueError("ttl must be non-negative")
        key = (installation_id, endpoint)
        p = CachingPolicy(endpoint=endpoint, ttl_seconds=ttl_seconds, cache_control=cache_control, vary_headers=vary_headers or [], stale_while_revalidate=stale_while_revalidate)
        self._policies[key] = p
        return p

    def get_policy(self, installation_id: str, endpoint: str) -> CachingPolicy | None:
        return self._policies.get((installation_id, endpoint))

    def cacheable_endpoints(self, installation_id: str) -> list[CachingPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id and p.is_cacheable]

    def generate_header(self, installation_id: str, endpoint: str) -> str:
        p = self._policies.get((installation_id, endpoint))
        if p is None: return "no-store"
        parts = [p.cache_control, f"max-age={p.ttl_seconds}"]
        if p.stale_while_revalidate: parts.append(f"stale-while-revalidate={p.stale_while_revalidate}")
        return ", ".join(parts)

    def all_policies(self, installation_id: str) -> list[CachingPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
