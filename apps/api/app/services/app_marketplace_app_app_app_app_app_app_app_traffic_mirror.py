"""Traffic mirroring engine — mirror production traffic for testing."""
from __future__ import annotations


def create_mirror(source: str, target: str, sample_rate: float = 1.0,
                   filters: list[str] | None = None) -> dict:
    return {"source": source, "target": target, "sample_rate": min(1.0, max(0, sample_rate)),
            "filters": filters or [], "status": "active", "mirrored": 0, "errors": 0}


def process_mirror(mirror: dict, request_count: int, error_count: int = 0) -> dict:
    sampled = int(request_count * mirror["sample_rate"])
    mirror["mirrored"] += sampled
    mirror["errors"] += error_count
    return {"mirrored": sampled, "total_mirrored": mirror["mirrored"],
            "total_errors": mirror["errors"],
            "error_rate": round(mirror["errors"] / max(mirror["mirrored"], 1) * 100, 1)}


def mirror_summary(mirrors: list[dict]) -> dict:
    total_mirrored = sum(m["mirrored"] for m in mirrors)
    total_errors = sum(m["errors"] for m in mirrors)
    active = sum(1 for m in mirrors if m["status"] == "active")
    return {"total_mirrors": len(mirrors), "active": active,
            "total_mirrored": total_mirrored, "total_errors": total_errors}
