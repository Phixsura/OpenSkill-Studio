"""App API Webhook Compression — configure payload compression."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

VALID_ALGORITHMS = {"none", "gzip", "br", "deflate"}

@dataclass
class CompressionConfig:
    destination: str
    algorithm: str = "none"
    min_size_bytes: int = 1024
    bytes_saved: int = 0

class AppAPIWebhookCompression:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CompressionConfig] = {}

    def configure(self, installation_id: str, destination: str, algorithm: str = "gzip", min_size_bytes: int = 1024) -> CompressionConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in VALID_ALGORITHMS: raise ValueError(f"algorithm must be one of {VALID_ALGORITHMS}")
        c = CompressionConfig(destination=destination, algorithm=algorithm, min_size_bytes=min_size_bytes)
        self._configs[(installation_id, destination)] = c
        return c

    def record_savings(self, installation_id: str, destination: str, bytes_saved: int) -> CompressionConfig:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: raise KeyError(f"No config for {destination}")
        c.bytes_saved += bytes_saved
        return c

    def get_config(self, installation_id: str, destination: str) -> CompressionConfig | None:
        return self._configs.get((installation_id, destination))

    def list_configs(self, installation_id: str) -> list[CompressionConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
