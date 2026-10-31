"""Platform knowledge graph — map relationships between platform entities."""
from __future__ import annotations


def build_graph(entities: list[dict], relationships: list[dict]) -> dict:
    nodes = {e["id"]: {"id": e["id"], "type": e.get("type", "entity"),
                        "label": e.get("label", e["id"])} for e in entities}
    edges = [{"from": r["from"], "to": r["to"], "type": r.get("type", "related")}
             for r in relationships if r["from"] in nodes and r["to"] in nodes]
    types = sorted({n["type"] for n in nodes.values()})
    return {"nodes": list(nodes.values()), "edges": edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "entity_types": types}


def find_related(graph: dict, entity_id: str) -> dict:
    outgoing = [e["to"] for e in graph["edges"] if e["from"] == entity_id]
    incoming = [e["from"] for e in graph["edges"] if e["to"] == entity_id]
    return {"entity": entity_id, "outgoing": outgoing, "incoming": incoming,
            "total_connections": len(outgoing) + len(incoming)}
