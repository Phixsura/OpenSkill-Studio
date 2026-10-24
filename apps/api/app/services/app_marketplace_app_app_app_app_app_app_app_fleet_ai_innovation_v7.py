"""Fleet AI Innovation v7 — track AI R&D and innovation at scale."""
from __future__ import annotations
def fleet_ai_innovation_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    experiments = sum(t.get("experiments", 0) for t in trackers)
    breakthroughs = sum(t.get("breakthroughs", 0) for t in trackers)
    patents = sum(t.get("patents", 0) for t in trackers)
    papers = sum(t.get("papers", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "experiments": experiments,
            "breakthroughs": breakthroughs, "patents": patents, "papers": papers, "innovating": breakthroughs > 0}
