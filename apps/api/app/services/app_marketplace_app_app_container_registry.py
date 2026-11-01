"""Container registry — Docker image management and tagging."""

import html
import re
from datetime import datetime, timezone

IMAGE_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,127}$")
TAG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")


def validate_image_ref(*, image: str, tag: str = "latest") -> dict:
    errors = []
    if not IMAGE_RE.match(image):
        errors.append("Invalid image name")
    if not TAG_RE.match(tag):
        errors.append("Invalid tag format")
    ref = f"{image}:{tag}"
    return {"valid": len(errors) == 0, "ref": ref, "image": image, "tag": tag, "errors": errors}


def build_image_list(*, images: list[dict]) -> dict:
    items = []
    total_size = 0
    for img in images:
        size_mb = img.get("size_mb", 0)
        total_size += size_mb
        items.append({
            "name": html.escape(img.get("name", "")),
            "tag": img.get("tag", "latest"),
            "digest": img.get("digest", ""),
            "size_mb": size_mb,
            "pushed_at": img.get("pushed_at", ""),
            "pull_count": img.get("pull_count", 0),
        })
    items.sort(key=lambda x: x.get("pushed_at", ""), reverse=True)
    return {"images": items, "total": len(items), "total_size_mb": round(total_size, 1)}
