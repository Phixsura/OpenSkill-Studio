"""Container registry — manage container images."""
from __future__ import annotations
import hashlib
import time

_images: dict[str, dict] = {}


def push_image(name: str, tag: str, size_mb: float, layers: int = 1) -> dict:
    key = f"{name}:{tag}"
    digest = hashlib.sha256(f"{key}:{time.time()}".encode()).hexdigest()[:12]
    _images[key] = {"name": name, "tag": tag, "digest": f"sha256:{digest}",
                     "size_mb": round(size_mb, 1), "layers": layers,
                     "pushed_at": time.time()}
    return _images[key]


def list_images(name: str | None = None) -> list[dict]:
    if name:
        return [v for v in _images.values() if v["name"] == name]
    return list(_images.values())


def get_image(name: str, tag: str) -> dict | None:
    return _images.get(f"{name}:{tag}")


def delete_image(name: str, tag: str) -> dict:
    key = f"{name}:{tag}"
    if key in _images:
        del _images[key]
        return {"deleted": True}
    return {"deleted": False, "error": "not_found"}


def registry_stats() -> dict:
    total_size = sum(i["size_mb"] for i in _images.values())
    repos = len({i["name"] for i in _images.values()})
    return {"total_images": len(_images), "total_size_mb": round(total_size, 1),
            "repositories": repos}


def clear_registry() -> None:
    _images.clear()
