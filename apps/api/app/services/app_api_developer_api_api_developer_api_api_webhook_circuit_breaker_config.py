"""App API Developer Webhook Circuit Breaker Config — per-destination circuit breaker settings."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CircuitBreakerConfig:
    destination: str
    failure_threshold: int
    recovery_timeout_seconds: int
    half_open_max_requests: int = 3
    success_threshold: int = 2  # successes needed in half-open to close
    enabled: bool = True

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookCircuitBreakerConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CircuitBreakerConfig] = {}

    def configure(self, installation_id: str, destination: str, failure_threshold: int, recovery_timeout_seconds: int, half_open_max_requests: int = 3, success_threshold: int = 2) -> CircuitBreakerConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if failure_threshold < 1: raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout_seconds < 1: raise ValueError("recovery_timeout must be >= 1")
        if success_threshold > half_open_max_requests: raise ValueError("success_threshold must be <= half_open_max_requests")
        key = (installation_id, destination)
        c = CircuitBreakerConfig(destination=destination, failure_threshold=failure_threshold, recovery_timeout_seconds=recovery_timeout_seconds, half_open_max_requests=half_open_max_requests, success_threshold=success_threshold)
        self._configs[key] = c
        return c

    def get(self, installation_id: str, destination: str) -> CircuitBreakerConfig | None:
        return self._configs.get((installation_id, destination))

    def toggle(self, installation_id: str, destination: str, enabled: bool) -> CircuitBreakerConfig:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No config for {destination}")
        c.enabled = enabled
        return c

    def all_configs(self, installation_id: str) -> list[CircuitBreakerConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def enabled_configs(self, installation_id: str) -> list[CircuitBreakerConfig]:
        return [c for c in self.all_configs(installation_id) if c.enabled]
