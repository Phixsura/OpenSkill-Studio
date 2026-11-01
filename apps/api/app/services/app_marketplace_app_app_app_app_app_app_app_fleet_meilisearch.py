"""Fleet Meilisearch — track instant search engine."""
from __future__ import annotations
def fleet_meilisearch_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    indexes = sum(i.get("indexes", 0) for i in instances)
    documents = sum(i.get("documents", 0) for i in instances)
    search_p50_ms = round(sum(i.get("search_p50_ms", 0) for i in instances) / max(len(instances), 1), 1)
    return {"instances": len(instances), "healthy": len(healthy), "indexes": indexes,
            "documents": documents, "search_p50_ms": search_p50_ms, "fast": search_p50_ms < 50}
