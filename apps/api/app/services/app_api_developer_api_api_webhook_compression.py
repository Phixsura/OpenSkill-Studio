"""App API Developer Webhook Compression — compress webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass
import zlib
import structlog

log = structlog.get_logger()

@dataclass
class CompressionResult:
    original_bytes: int
    compressed_bytes: int
    algorithm: str

    @property
    def ratio(self) -> float:
        return round(self.compressed_bytes / self.original_bytes * 100, 1) if self.original_bytes > 0 else 100.0

    @property
    def savings_pct(self) -> float:
        return round(100.0 - self.ratio, 1)

class AppAPIDeveloperAPIApiWebhookCompression:
    def __init__(self) -> None:
        self._stats: dict[str, dict[str, int]] = {}

    def compress(self, installation_id: str, payload: str, algorithm: str = "gzip") -> CompressionResult:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in ("gzip", "deflate"): raise ValueError(f"Unsupported: {algorithm}")
        original = payload.encode("utf-8")
        if algorithm == "gzip":
            compressed = zlib.compress(original, level=6)
        else:
            compressed = zlib.compress(original, level=6)
        result = CompressionResult(original_bytes=len(original), compressed_bytes=len(compressed), algorithm=algorithm)
        s = self._stats.setdefault(installation_id, {"total_original": 0, "total_compressed": 0, "count": 0})
        s["total_original"] += result.original_bytes
        s["total_compressed"] += result.compressed_bytes
        s["count"] += 1
        return result

    def stats(self, installation_id: str) -> dict[str, int | float]:
        s = self._stats.get(installation_id, {"total_original": 0, "total_compressed": 0, "count": 0})
        avg_savings = round(100.0 - (s["total_compressed"] / s["total_original"] * 100), 1) if s["total_original"] > 0 else 0.0
        return {**s, "avg_savings_pct": avg_savings}

    def should_compress(self, payload: str, min_bytes: int = 1024) -> bool:
        return len(payload.encode("utf-8")) >= min_bytes
