"""App API Developer Sandbox Metrics — track sandbox environment usage and performance."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SandboxMetrics:
    sandbox_id: str
    total_requests: int = 0
    unique_developers: int = 0
    avg_response_ms: float = 0.0
    errors: int = 0
    active: bool = True

    @property
    def error_rate(self) -> float:
        return round(self.errors / self.total_requests * 100, 1) if self.total_requests > 0 else 0.0

    @property
    def health(self) -> str:
        if self.error_rate > 10: return "unhealthy"
        if self.error_rate > 5: return "degraded"
        return "healthy"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], SandboxMetrics] = {}

    def update(self, installation_id: str, sandbox_id: str, **kwargs) -> SandboxMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, sandbox_id)
        m = SandboxMetrics(sandbox_id=sandbox_id)
        for k, v in kwargs.items():
            if hasattr(m, k): setattr(m, k, v)
        self._metrics[key] = m
        return m

    def unhealthy(self, installation_id: str) -> list[SandboxMetrics]:
        return [m for (inst, _), m in self._metrics.items() if inst == installation_id and m.health != "healthy"]

    def all_sandboxes(self, installation_id: str) -> list[SandboxMetrics]:
        return [m for (inst, _), m in self._metrics.items() if inst == installation_id]
