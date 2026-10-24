"""Network graph — service dependency network visualization."""

import html


def build_network_graph(*, nodes: list[dict], edges: list[dict]) -> dict:
    node_map = {}
    for n in nodes:
        nid = n["id"]
        in_deg = sum(1 for e in edges if e["to"] == nid)
        out_deg = sum(1 for e in edges if e["from"] == nid)
        node_map[nid] = {
            "id": nid,
            "label": html.escape(n.get("label", nid)),
            "type": n.get("type", "service"),
            "in_degree": in_deg,
            "out_degree": out_deg,
            "is_leaf": out_deg == 0,
            "is_root": in_deg == 0,
        }
    safe_edges = [{"from": e["from"], "to": e["to"],
                    "label": html.escape(e.get("label", ""))} for e in edges]
    roots = [n for n in node_map.values() if n["is_root"]]
    leaves = [n for n in node_map.values() if n["is_leaf"]]
    return {"nodes": list(node_map.values()), "edges": safe_edges,
            "node_count": len(node_map), "edge_count": len(safe_edges),
            "root_count": len(roots), "leaf_count": len(leaves)}
