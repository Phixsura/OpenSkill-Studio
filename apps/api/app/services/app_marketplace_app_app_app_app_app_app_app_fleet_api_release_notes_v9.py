"""Fleet API Release Notes v9 — track automated release note generation."""
from __future__ import annotations
def fleet_api_release_notes_v9(releases: list[dict]) -> dict:
    generated = [r for r in releases if r.get("notes_generated")]
    published = [r for r in releases if r.get("published")]
    features = sum(r.get("features", 0) for r in releases)
    return {"releases": len(releases), "generated": len(generated), "published": len(published),
            "total_features": features, "healthy": len(generated) == len(releases)}
