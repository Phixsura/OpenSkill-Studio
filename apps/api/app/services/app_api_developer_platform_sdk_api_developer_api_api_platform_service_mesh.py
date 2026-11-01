"""App API Developer Platform Service Mesh — manage service-to-service communication."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ServiceRoute:
    source: str
    destination: str
    protocol: str = "https"
    latency_ms: float = 0.0
    request_count: int = 0
    error_count: int = 0

    @property
    def error_rate(self) -> float:
        return round(self.error_count / self.request_count * 100, 1) if self.request_count > 0 else 0.0

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str, str], ServiceRoute] = {}

    def register_route(self, installation_id: str, source: str, destination: str, protocol: str = "https") -> ServiceRoute:
        if not installation_id: raise ValueError("installation_id is required")
        if protocol not in ("https", "grpc", "http2"): raise ValueError("invalid protocol")
        key = (installation_id, source, destination)
        r = ServiceRoute(source=source, destination=destination, protocol=protocol)
        self._routes[key] = r
        return r

    def record_traffic(self, installation_id: str, source: str, destination: str, latency_ms: float, success: bool) -> ServiceRoute:
        key = (installation_id, source, destination)
        r = self._routes.get(key)
        if r is None: raise KeyError(f"No route {source} → {destination}")
        r.request_count += 1
        if not success: r.error_count += 1
        r.latency_ms = latency_ms
        return r

    def routes_from(self, installation_id: str, source: str) -> list[ServiceRoute]:
        return [r for (inst, s, _), r in self._routes.items() if inst == installation_id and s == source]

    def unhealthy_routes(self, installation_id: str, threshold: float = 5.0) -> list[ServiceRoute]:
        return [r for (inst, _, _), r in self._routes.items() if inst == installation_id and r.error_rate >= threshold]

    def all_routes(self, installation_id: str) -> list[ServiceRoute]:
        return [r for (inst, _, _), r in self._routes.items() if inst == installation_id]
