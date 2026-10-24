"""Fleet AI Multimodal — track vision, audio, and multimodal AI pipelines."""
from __future__ import annotations
def fleet_ai_multimodal(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    modalities = set()
    for p in pipelines:
        modalities.update(p.get("modalities", []))
    requests_24h = sum(p.get("requests_24h", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "modalities": sorted(modalities),
            "requests_24h": requests_24h, "multimodal": len(modalities) > 1}
