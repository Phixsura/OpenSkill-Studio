"""Request enrichment pipeline — enrich requests with context before processing."""
from __future__ import annotations


def enrich_request(request: dict, enrichers: list[dict]) -> dict:
    enriched = dict(request)
    applied = []
    for e in enrichers:
        field = e["field"]
        value = e["value"]
        if field not in enriched:
            enriched[field] = value
            applied.append({"field": field, "source": e.get("source", "default")})
    return {"request": enriched, "enrichments_applied": len(applied),
            "enrichments": applied, "total_fields": len(enriched)}


def build_enrichment_context(user_id: str, tenant_id: str, features: list[str]) -> dict:
    return {"user_id": user_id, "tenant_id": tenant_id,
            "features": features, "feature_count": len(features),
            "context_built": True}
