"""Fleet AI Knowledge Graph — track knowledge base management."""
from __future__ import annotations
def fleet_ai_kg(graphs: list[dict]) -> dict:
    active = [g for g in graphs if g.get("active", True)]
    entities = sum(g.get("entities", 0) for g in graphs)
    relationships = sum(g.get("relationships", 0) for g in graphs)
    queries_24h = sum(g.get("queries_24h", 0) for g in graphs)
    return {"graphs": len(graphs), "active": len(active), "entities": entities,
            "relationships": relationships, "queries_24h": queries_24h}
