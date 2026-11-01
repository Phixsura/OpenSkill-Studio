"""Consumer API Gateway Config — unified gateway configuration per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GatewayConfig:
    consumer_id: str
    timeout_ms: int = 30000
    max_request_size_bytes: int = 1048576
    compression_enabled: bool = True
    cors_enabled: bool = True
    logging_level: str = "info"  # "debug", "info", "warn", "error"
    custom_headers: dict[str, str] = field(default_factory=dict)
    blocked_paths: list[str] = field(default_factory=list)

VALID_LOG_LEVELS = {"debug", "info", "warn", "error"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], GatewayConfig] = {}

    def set_config(self, installation_id: str, config: GatewayConfig) -> GatewayConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.logging_level not in VALID_LOG_LEVELS:
            raise ValueError(f"Invalid logging_level: {config.logging_level}")
        if config.timeout_ms < 1000:
            raise ValueError("timeout_ms must be at least 1000")
        if config.max_request_size_bytes < 1024:
            raise ValueError("max_request_size_bytes must be at least 1KB")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def get_config(self, installation_id: str, consumer_id: str) -> GatewayConfig:
        return self._configs.get((installation_id, consumer_id), GatewayConfig(consumer_id=consumer_id))

    def is_path_blocked(self, installation_id: str, consumer_id: str, path: str) -> bool:
        config = self.get_config(installation_id, consumer_id)
        return any(path.startswith(bp) for bp in config.blocked_paths)

    def merge_headers(self, installation_id: str, consumer_id: str, request_headers: dict[str, str]) -> dict[str, str]:
        config = self.get_config(installation_id, consumer_id)
        merged = dict(request_headers)
        for k, v in config.custom_headers.items():
            if k.lower() not in ("host", "content-length", "transfer-encoding"):
                merged[k] = v
        return merged

    def list_configs(self, installation_id: str) -> list[GatewayConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
