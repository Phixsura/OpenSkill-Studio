"""Container registry — manage Docker images for app deployments."""

import re
import secrets

IMAGE_TAG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")


def push_image(*, repository: str, tag: str, size_mb: float) -> dict:
    if not IMAGE_TAG_RE.match(tag):
        return {"error": f"Invalid tag: {tag}"}
    digest = f"sha256:{secrets.token_hex(32)}"
    return {
        "repository": repository,
        "tag": tag,
        "digest": digest,
        "size_mb": round(size_mb, 1),
        "full_ref": f"registry.openskill.dev/{repository}:{tag}",
        "status": "pushed",
    }


def list_images(*, repository: str) -> dict:
    return {
        "repository": repository,
        "images": [
            {"tag": "latest", "digest": "sha256:abc1", "size_mb": 145.2, "pushed_at": "2026-10-23T12:00:00"},
            {"tag": "v2.0.0", "digest": "sha256:abc2", "size_mb": 142.8, "pushed_at": "2026-10-22T10:00:00"},
            {"tag": "v1.9.0", "digest": "sha256:abc3", "size_mb": 138.5, "pushed_at": "2026-10-15T08:00:00"},
        ],
        "total": 3,
        "total_size_mb": 426.5,
    }


def delete_image(*, repository: str, tag: str) -> dict:
    if tag == "latest":
        return {"error": "Cannot delete 'latest' tag"}
    return {"deleted": True, "repository": repository, "tag": tag}
