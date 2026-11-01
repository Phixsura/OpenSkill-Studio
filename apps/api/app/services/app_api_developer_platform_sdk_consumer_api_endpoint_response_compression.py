"""Consumer API Endpoint Response Compression — manage per-endpoint compression settings."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CompressionConfig:
    endpoint_path: str
    algorithm: str = "gzip"  # "gzip", "br", "deflate", "none"
    min_size_bytes: int = 1024
    level: int = 6  # 1-9
    content_types: list[str] = field(default_factory=lambda: ["application/json", "text/plain"])

@dataclass
class CompressionStats:
    endpoint_path: str
    total_responses: int
    compressed_count: int
    total_original_bytes: int
    total_compressed_bytes: int
    savings_pct: float

VALID_ALGORITHMS = {"gzip", "br", "deflate", "none"}

class AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CompressionConfig] = {}
        self._stats: dict[tuple[str, str], CompressionStats] = {}

    def configure(self, installation_id: str, config: CompressionConfig) -> CompressionConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.algorithm not in VALID_ALGORITHMS:
            raise ValueError(f"Invalid algorithm: {config.algorithm}")
        if not (1 <= config.level <= 9):
            raise ValueError("level must be 1-9")
        self._configs[(installation_id, config.endpoint_path)] = config
        return config

    def should_compress(self, installation_id: str, endpoint_path: str, content_type: str, body_size: int) -> bool:
        config = self._configs.get((installation_id, endpoint_path))
        if not config or config.algorithm == "none":
            return False
        if body_size < config.min_size_bytes:
            return False
        base_type = content_type.split(";")[0].strip()
        return base_type in config.content_types

    def record_compression(self, installation_id: str, endpoint_path: str, original_bytes: int, compressed_bytes: int) -> None:
        key = (installation_id, endpoint_path)
        stats = self._stats.get(key)
        if not stats:
            stats = CompressionStats(endpoint_path=endpoint_path, total_responses=0, compressed_count=0, total_original_bytes=0, total_compressed_bytes=0, savings_pct=0)
            self._stats[key] = stats
        stats.total_responses += 1
        stats.compressed_count += 1
        stats.total_original_bytes += original_bytes
        stats.total_compressed_bytes += compressed_bytes
        stats.savings_pct = round((1 - stats.total_compressed_bytes / max(stats.total_original_bytes, 1)) * 100, 1)

    def get_stats(self, installation_id: str, endpoint_path: str) -> CompressionStats | None:
        return self._stats.get((installation_id, endpoint_path))

    def list_configs(self, installation_id: str) -> list[CompressionConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
