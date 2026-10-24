"""Service topology diff — detect changes in service topology."""
from __future__ import annotations


def diff_topology(old: dict, new: dict) -> dict:
    old_nodes = set(old.get("nodes", []))
    new_nodes = set(new.get("nodes", []))
    old_edges = {f"{e['src']}→{e['dst']}" for e in old.get("edges", [])}
    new_edges = {f"{e['src']}→{e['dst']}" for e in new.get("edges", [])}
    added_nodes = sorted(new_nodes - old_nodes)
    removed_nodes = sorted(old_nodes - new_nodes)
    added_edges = sorted(new_edges - old_edges)
    removed_edges = sorted(old_edges - new_edges)
    has_changes = bool(added_nodes or removed_nodes or added_edges or removed_edges)
    return {"added_nodes": added_nodes, "removed_nodes": removed_nodes,
            "added_edges": added_edges, "removed_edges": removed_edges,
            "has_changes": has_changes,
            "total_changes": len(added_nodes) + len(removed_nodes) + len(added_edges) + len(removed_edges)}


def topology_risk(diff: dict) -> dict:
    removed = len(diff.get("removed_nodes", [])) + len(diff.get("removed_edges", []))
    added = len(diff.get("added_nodes", [])) + len(diff.get("added_edges", []))
    risk = "high" if removed > 2 else ("medium" if removed > 0 else ("low" if added > 0 else "none"))
    return {"risk": risk, "removals": removed, "additions": added}
