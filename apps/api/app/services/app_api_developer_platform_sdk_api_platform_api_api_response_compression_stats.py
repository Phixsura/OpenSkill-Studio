"""App API Developer API Response Compression Stats — track compression savings."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CompressionStats:
    endpoint: str
    total_responses: int = 0
    compressed_count: int = 0
    original_bytes: int = 0
    compressed_bytes: int = 0

    @property
    def compression_rate(self) -> float:
        return round(self.compressed_count / self.total_responses * 100, 1) if self.total_responses > 0 else 0.0

    @property
    def savings_pct(self) -> float:
        return round((1 - self.compressed_bytes / self.original_bytes) * 100, 1) if self.original_bytes > 0 else 0.0

    @property
    def bandwidth_saved_bytes(self) -> int:
        return self.original_bytes - self.compressed_bytes

class AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str], CompressionStats] = {}

    def record(self, installation_id: str, endpoint: str, original_bytes: int, compressed_bytes: int, compressed: bool) -> CompressionStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._stats:
            self._stats[key] = CompressionStats(endpoint=endpoint)
        s = self._stats[key]
        s.total_responses += 1
        s.original_bytes += original_bytes
        s.compressed_bytes += compressed_bytes
        if compressed: s.compressed_count += 1
        return s

    def total_savings(self, installation_id: str) -> int:
        return sum(s.bandwidth_saved_bytes for (inst, _), s in self._stats.items() if inst == installation_id)

    def best_savings(self, installation_id: str, limit: int = 5) -> list[CompressionStats]:
        stats = [s for (inst, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: s.savings_pct, reverse=True)[:limit]

    def all_stats(self, installation_id: str) -> list[CompressionStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id]
