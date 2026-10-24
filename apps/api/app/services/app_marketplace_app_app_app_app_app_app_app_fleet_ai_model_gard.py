"""Fleet AI Model Garden — track curated model catalog and discovery."""
from __future__ import annotations
def fleet_ai_model_garden(gardens: list[dict]) -> dict:
    active = [g for g in gardens if g.get("active", True)]
    models = sum(g.get("models", 0) for g in gardens)
    categories = sum(g.get("categories", 0) for g in gardens)
    downloads_24h = sum(g.get("downloads_24h", 0) for g in gardens)
    return {"gardens": len(gardens), "active": len(active), "models": models,
            "categories": categories, "downloads_24h": downloads_24h, "rich": models > 100}
