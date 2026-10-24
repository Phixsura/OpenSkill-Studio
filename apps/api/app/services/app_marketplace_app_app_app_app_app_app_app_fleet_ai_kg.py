"""Fleet AI Knowledge Graph — track entity-relationship knowledge bases."""
from __future__ import annotations
def fleet_ai_knowledge_graph(graphs: list[dict]) -> dict:
    active = [g for g in graphs if g.get("active", True)]
    entities = sum(g.get("entities", 0) for g in graphs)
    relations = sum(g.get("relations", 0) for g in graphs)
    queries_24h = sum(g.get("queries_24h", 0) for g in graphs)
    return {"graphs": len(graphs), "active": len(active), "entities": entities,
            "relations": relations, "queries_24h": queries_24h, "connected": relations > entities}
