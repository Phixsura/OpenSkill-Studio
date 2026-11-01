"""Build artifact registry — store and track build outputs."""
from __future__ import annotations
import hashlib
import time

_artifacts: dict[str, dict] = {}


def store_artifact(name: str, version: str, size_mb: float, build_id: str) -> dict:
    key = f"{name}:{version}"
    digest = hashlib.sha256(f"{key}:{time.time()}".encode()).hexdigest()[:12]
    _artifacts[key] = {"name": name, "version": version, "size_mb": round(size_mb, 1),
                        "build_id": build_id, "digest": f"sha256:{digest}",
                        "created_at": time.time(), "downloads": 0}
    return _artifacts[key]


def download_artifact(name: str, version: str) -> dict:
    key = f"{name}:{version}"
    a = _artifacts.get(key)
    if not a:
        return {"found": False, "error": "not_found"}
    a["downloads"] += 1
    return {"found": True, "name": a["name"], "version": a["version"],
            "size_mb": a["size_mb"], "digest": a["digest"]}


def artifact_stats() -> dict:
    total_size = sum(a["size_mb"] for a in _artifacts.values())
    total_downloads = sum(a["downloads"] for a in _artifacts.values())
    return {"total": len(_artifacts), "total_size_mb": round(total_size, 1),
            "total_downloads": total_downloads}


def clear_artifacts() -> None:
    _artifacts.clear()
