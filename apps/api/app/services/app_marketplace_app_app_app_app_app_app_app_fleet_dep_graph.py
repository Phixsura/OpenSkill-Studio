"""Fleet dependency graph — analyze service dependency topology."""
from __future__ import annotations
def fleet_dep_graph(edges: list[dict]) -> dict:
    sources = {e["from"] for e in edges}
    targets = {e["to"] for e in edges}
    all_nodes = sources | targets
    leaf = targets - sources
    root = sources - targets
    return {"nodes": len(all_nodes), "edges": len(edges), "roots": len(root), "leaves": len(leaf)}
