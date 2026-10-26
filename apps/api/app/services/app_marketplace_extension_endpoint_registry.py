"""Endpoint Registry — centralized registry of all extension API endpoints.

Registers endpoints with metadata, versioning, deprecation, usage
tracking, and provides endpoint discovery and documentation.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Endpoint:
    path: str
    method: str
    version: str
    extension_id: str
    handler: str
    description: str = ""
    deprecated: bool = False
    auth_required: bool = True
    rate_limit: int = 0
    call_count: int = 0
    avg_latency_ms: float = 0.0
    tags: list[str] = field(default_factory=list)


class EndpointRegistryService:
    """Centralized endpoint registry with discovery."""

    def __init__(self):
        self._endpoints: dict[str, Endpoint] = {}

    def _key(self, method: str, path: str, version: str) -> str:
        return f"{method.upper()}:{version}:{path}"

    def register(self, path: str, method: str, version: str,
                 extension_id: str, handler: str, description: str = "",
                 auth_required: bool = True, rate_limit: int = 0,
                 tags: list[str] | None = None) -> Endpoint:
        key = self._key(method, path, version)
        ep = Endpoint(path=path, method=method.upper(), version=version,
                      extension_id=extension_id, handler=handler,
                      description=description, auth_required=auth_required,
                      rate_limit=rate_limit, tags=tags or [])
        self._endpoints[key] = ep
        return ep

    def record_call(self, method: str, path: str, version: str,
                    latency_ms: float) -> None:
        key = self._key(method, path, version)
        ep = self._endpoints.get(key)
        if ep:
            total_latency = ep.avg_latency_ms * ep.call_count + latency_ms
            ep.call_count += 1
            ep.avg_latency_ms = round(total_latency / ep.call_count, 1)

    def deprecate(self, method: str, path: str, version: str) -> bool:
        key = self._key(method, path, version)
        ep = self._endpoints.get(key)
        if ep:
            ep.deprecated = True
            return True
        return False

    def discover(self, extension_id: str | None = None,
                 version: str | None = None,
                 tag: str | None = None,
                 include_deprecated: bool = False) -> list[Endpoint]:
        eps = list(self._endpoints.values())
        if extension_id:
            eps = [e for e in eps if e.extension_id == extension_id]
        if version:
            eps = [e for e in eps if e.version == version]
        if tag:
            eps = [e for e in eps if tag in e.tags]
        if not include_deprecated:
            eps = [e for e in eps if not e.deprecated]
        return eps

    def get_most_used(self, limit: int = 10) -> list[Endpoint]:
        return sorted(self._endpoints.values(), key=lambda e: e.call_count, reverse=True)[:limit]

    def get_slowest(self, limit: int = 10) -> list[Endpoint]:
        return sorted(self._endpoints.values(), key=lambda e: e.avg_latency_ms, reverse=True)[:limit]

    def get_stats(self) -> dict:
        eps = list(self._endpoints.values())
        return {
            "total": len(eps),
            "deprecated": sum(1 for e in eps if e.deprecated),
            "total_calls": sum(e.call_count for e in eps),
            "versions": sorted({e.version for e in eps}),
            "extensions": len({e.extension_id for e in eps}),
        }
