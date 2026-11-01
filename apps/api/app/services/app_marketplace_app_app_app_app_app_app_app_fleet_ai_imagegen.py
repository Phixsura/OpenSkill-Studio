"""Fleet AI Image Generation — track image synthesis."""
from __future__ import annotations
def fleet_ai_imagegen(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    images_24h = sum(s.get("images_24h", 0) for s in services)
    avg_gen_sec = round(sum(s.get("avg_gen_sec", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "images_24h": images_24h,
            "avg_gen_sec": avg_gen_sec, "fast": avg_gen_sec < 30}
