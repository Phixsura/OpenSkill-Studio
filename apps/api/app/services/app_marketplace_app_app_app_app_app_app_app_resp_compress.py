"""API response compressor — compress responses based on Accept-Encoding."""
from __future__ import annotations
import zlib


def should_compress(content_length: int, content_type: str, accept_encoding: str,
                    min_size: int = 1024) -> dict:
    compressible_types = {"application/json", "text/html", "text/plain", "text/xml", "text/css", "application/javascript"}
    supports_gzip = "gzip" in accept_encoding.lower()
    is_compressible = content_type in compressible_types
    large_enough = content_length >= min_size
    should = supports_gzip and is_compressible and large_enough
    return {"should_compress": should, "encoding": "gzip" if should else "identity",
            "content_length": content_length, "content_type": content_type}


def compress_stats(total_requests: int, compressed: int, bytes_saved: int) -> dict:
    compression_rate = round(compressed / max(total_requests, 1) * 100, 1)
    return {"total_requests": total_requests, "compressed": compressed,
            "bytes_saved": bytes_saved, "compression_rate": compression_rate,
            "saved_mb": round(bytes_saved / 1048576, 2)}
