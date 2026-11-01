"""Container image registry — manage container images and tags."""
from __future__ import annotations


class ImageRegistry:
    def __init__(self):
        self._images: dict[str, list[dict]] = {}

    def push(self, name: str, tag: str, size_mb: float, digest: str) -> dict:
        self._images.setdefault(name, [])
        entry = {"tag": tag, "size_mb": round(size_mb, 1), "digest": digest}
        self._images[name] = [e for e in self._images[name] if e["tag"] != tag]
        self._images[name].append(entry)
        return {"name": name, "tag": tag, "pushed": True}

    def pull(self, name: str, tag: str = "latest") -> dict:
        tags = self._images.get(name, [])
        for t in tags:
            if t["tag"] == tag:
                return {"name": name, "tag": tag, "found": True, "digest": t["digest"], "size_mb": t["size_mb"]}
        return {"name": name, "tag": tag, "found": False}

    def list_tags(self, name: str) -> list[str]:
        return [t["tag"] for t in self._images.get(name, [])]

    def stats(self) -> dict:
        total_images = len(self._images)
        total_tags = sum(len(t) for t in self._images.values())
        total_size = sum(t["size_mb"] for tags in self._images.values() for t in tags)
        return {"images": total_images, "tags": total_tags, "total_size_mb": round(total_size, 1)}
