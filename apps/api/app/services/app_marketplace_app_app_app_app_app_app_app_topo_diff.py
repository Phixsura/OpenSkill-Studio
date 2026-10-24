"""Service topology diff — compare topology snapshots over time."""
from __future__ import annotations


def diff_topology(old: dict, new: dict) -> dict:
    old_nodes = set(old.get("nodes", []))
    new_nodes = set(new.get("nodes", []))
    old_edges = {f"{e['from']}→{e['to']}" for e in old.get("edges", [])}
    new_edges = {f"{e['from']}→{e['to']}" for e in new.get("edges", [])}
    return {
        "nodes_added": sorted(new_nodes - old_nodes),
        "nodes_removed": sorted(old_nodes - new_nodes),
        "edges_added": sorted(new_edges - old_edges),
        "edges_removed": sorted(old_edges - new_edges),
        "total_changes": len(new_nodes ^ old_nodes) + len(new_edges ^ old_edges),
        "breaking": len(old_nodes - new_nodes) > 0 or len(old_edges - new_edges) > 0,
    }
