"""Payload compressor — compress/decompress API payloads."""
from __future__ import annotations
import zlib, base64


def compress(data: str) -> dict:
    original = len(data.encode())
    compressed = zlib.compress(data.encode(), level=6)
    encoded = base64.b64encode(compressed).decode()
    ratio = round((1 - len(compressed) / max(original, 1)) * 100, 1)
    return {"original_bytes": original, "compressed_bytes": len(compressed),
            "ratio_pct": ratio, "encoded": encoded}


def decompress(encoded: str) -> dict:
    compressed = base64.b64decode(encoded)
    data = zlib.decompress(compressed).decode()
    return {"data": data, "size_bytes": len(data.encode())}


def should_compress(size_bytes: int, content_type: str, threshold: int = 1024) -> dict:
    compressible = content_type in ("application/json", "text/plain", "text/html", "text/xml")
    return {"should_compress": size_bytes >= threshold and compressible,
            "size_bytes": size_bytes, "content_type": content_type}
