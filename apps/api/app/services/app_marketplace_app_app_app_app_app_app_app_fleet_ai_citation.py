"""Fleet AI Citation Tracker — track AI response source attribution."""
from __future__ import annotations
def fleet_ai_citation_tracker(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    citations_24h = sum(t.get("citations_24h", 0) for t in trackers)
    sources_verified = sum(t.get("verified", 0) for t in trackers)
    accuracy_pct = round(sum(t.get("accuracy_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "citations_24h": citations_24h,
            "verified": sources_verified, "accuracy_pct": accuracy_pct, "trustworthy": accuracy_pct > 90}
