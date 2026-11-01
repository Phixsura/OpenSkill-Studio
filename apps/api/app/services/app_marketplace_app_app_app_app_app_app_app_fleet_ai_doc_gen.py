"""Fleet AI Doc Generation — track AI-powered documentation synthesis."""
from __future__ import annotations
def fleet_ai_doc_gen(generators: list[dict]) -> dict:
    active = [g for g in generators if g.get("active", True)]
    pages_24h = sum(g.get("pages_24h", 0) for g in generators)
    repos_covered = sum(g.get("repos", 0) for g in generators)
    freshness = round(sum(g.get("freshness_pct", 0) for g in generators) / max(len(generators), 1), 1)
    return {"generators": len(generators), "active": len(active), "pages_24h": pages_24h,
            "repos": repos_covered, "freshness": freshness, "current": freshness > 90}
