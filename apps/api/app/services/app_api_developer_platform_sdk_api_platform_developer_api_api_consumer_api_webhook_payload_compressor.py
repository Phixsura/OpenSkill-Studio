"""API Consumer Webhook Payload Compressor — compress webhook payloads for delivery."""
from __future__ import annotations
from dataclasses import dataclass
import zlib
import structlog

log = structlog.get_logger()

@dataclass
class CompressionResult:
    original_size: int
    compressed_size: int
    algorithm: str
    compression_ratio: float

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor:
    def __init__(self) -> None:
        self._stats: dict[str, dict[str, int]] = {}

    def compress(self, installation_id: str, payload: str, algorithm: str = "gzip") -> CompressionResult:
        if not installation_id: raise ValueError("installation_id is required")
        if algorithm not in ("gzip", "deflate"): raise ValueError(f"Invalid algorithm: {algorithm}")
        original = len(payload.encode("utf-8"))
        if algorithm == "gzip":
            compressed = len(zlib.compress(payload.encode("utf-8")))
        else:
            compressed = len(zlib.compress(payload.encode("utf-8"), level=6))
        ratio = round(1 - compressed / original, 3) if original > 0 else 0.0
        stats = self._stats.setdefault(installation_id, {"total_original": 0, "total_compressed": 0, "count": 0})
        stats["total_original"] += original
        stats["total_compressed"] += compressed
        stats["count"] += 1
        return CompressionResult(original_size=original, compressed_size=compressed, algorithm=algorithm, compression_ratio=ratio)

    def savings(self, installation_id: str) -> dict[str, object]:
        stats = self._stats.get(installation_id, {"total_original": 0, "total_compressed": 0, "count": 0})
        saved = stats["total_original"] - stats["total_compressed"]
        ratio = round(saved / stats["total_original"] * 100, 1) if stats["total_original"] > 0 else 0.0
        return {"total_original_bytes": stats["total_original"], "total_compressed_bytes": stats["total_compressed"], "saved_bytes": saved, "savings_pct": ratio, "payloads_compressed": stats["count"]}
