"""API Consumer Health Check Config — configure health check parameters per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class HealthCheckConfig:
    consumer_id: str
    check_interval_s: int = 30
    timeout_ms: int = 5000
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    check_path: str = "/health"
    expected_status: int = 200

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], HealthCheckConfig] = {}

    def configure(self, installation_id: str, config: HealthCheckConfig) -> HealthCheckConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.check_interval_s < 5: raise ValueError("interval must be >= 5s")
        if config.timeout_ms < 100: raise ValueError("timeout must be >= 100ms")
        if config.healthy_threshold < 1: raise ValueError("healthy_threshold must be >= 1")
        if config.unhealthy_threshold < 1: raise ValueError("unhealthy_threshold must be >= 1")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def get_config(self, installation_id: str, consumer_id: str) -> HealthCheckConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def update_interval(self, installation_id: str, consumer_id: str, interval_s: int) -> HealthCheckConfig:
        cfg = self._configs.get((installation_id, consumer_id))
        if cfg is None: raise KeyError(f"No config for {consumer_id}")
        if interval_s < 5: raise ValueError("interval must be >= 5s")
        cfg.check_interval_s = interval_s
        return cfg

    def list_configs(self, installation_id: str) -> list[HealthCheckConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
