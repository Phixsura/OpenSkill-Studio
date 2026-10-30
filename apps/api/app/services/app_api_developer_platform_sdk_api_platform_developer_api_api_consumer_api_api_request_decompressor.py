"""API Consumer Request Decompressor — decompress incoming compressed request bodies."""
from __future__ import annotations
from dataclasses import dataclass
import zlib
import structlog

log = structlog.get_logger()

@dataclass
class DecompressionResult:
    original_size: int
    decompressed_size: int
    encoding: str
    ratio: float

VALID_ENCODINGS = {"gzip", "deflate", "identity"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor:
    def __init__(self, max_decompressed_bytes: int = 10485760) -> None:
        self._max = max(1024, max_decompressed_bytes)
        self._stats: dict[str, dict[str, int]] = {}

    def decompress(self, installation_id: str, data: bytes, encoding: str = "gzip") -> DecompressionResult:
        if not installation_id: raise ValueError("installation_id is required")
        if encoding not in VALID_ENCODINGS: raise ValueError(f"Unsupported encoding: {encoding}")
        original_size = len(data)
        if encoding == "identity":
            decompressed_size = original_size
        else:
            try:
                decompressed = zlib.decompress(data, zlib.MAX_WBITS | 16 if encoding == "gzip" else -zlib.MAX_WBITS)
            except zlib.error as e:
                raise ValueError(f"Decompression failed: {e}") from e
            decompressed_size = len(decompressed)
        if decompressed_size > self._max:
            raise ValueError(f"Decompressed size {decompressed_size} exceeds max {self._max}")
        ratio = round(decompressed_size / original_size, 2) if original_size > 0 else 1.0
        stats = self._stats.setdefault(installation_id, {"decompressed": 0, "total_in": 0, "total_out": 0})
        stats["decompressed"] += 1
        stats["total_in"] += original_size
        stats["total_out"] += decompressed_size
        return DecompressionResult(original_size=original_size, decompressed_size=decompressed_size, encoding=encoding, ratio=ratio)

    def savings(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"decompressed": 0, "total_in": 0, "total_out": 0})
