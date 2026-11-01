"""API Consumer Request Tracing Config — configure distributed tracing per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TracingConfig:
    consumer_id: str
    enabled: bool = True
    sample_rate: float = 1.0  # 0.0-1.0
    propagation_format: str = "w3c"  # "w3c", "b3", "jaeger"
    export_format: str = "otlp"  # "otlp", "jaeger", "zipkin"
    max_spans_per_trace: int = 100
    tags: dict[str, str] = field(default_factory=dict)

VALID_PROPAGATION = {"w3c", "b3", "jaeger"}
VALID_EXPORTS = {"otlp", "jaeger", "zipkin"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], TracingConfig] = {}

    def configure(self, installation_id: str, config: TracingConfig) -> TracingConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0.0 <= config.sample_rate <= 1.0: raise ValueError("sample_rate must be 0.0-1.0")
        if config.propagation_format not in VALID_PROPAGATION: raise ValueError(f"Invalid propagation: {config.propagation_format}")
        if config.export_format not in VALID_EXPORTS: raise ValueError(f"Invalid export: {config.export_format}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def get_config(self, installation_id: str, consumer_id: str) -> TracingConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def is_tracing_enabled(self, installation_id: str, consumer_id: str) -> bool:
        cfg = self._configs.get((installation_id, consumer_id))
        return cfg is not None and cfg.enabled and cfg.sample_rate > 0

    def list_configs(self, installation_id: str) -> list[TracingConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
