"""Service communication map — visualize all inter-service communication."""
from __future__ import annotations


def build_comm_map(communications: list[dict]) -> dict:
    nodes = set()
    edges = []
    by_protocol: dict[str, int] = {}
    total_rps = 0
    for c in communications:
        nodes.add(c["source"])
        nodes.add(c["destination"])
        rps = c.get("rps", 0)
        total_rps += rps
        protocol = c.get("protocol", "http")
        by_protocol[protocol] = by_protocol.get(protocol, 0) + 1
        edges.append({"source": c["source"], "destination": c["destination"],
                       "protocol": protocol, "rps": rps})
    return {"nodes": sorted(nodes), "edges": edges, "node_count": len(nodes),
            "edge_count": len(edges), "total_rps": total_rps,
            "by_protocol": by_protocol}


def find_chatty_services(comm_map: dict, threshold_rps: int = 100) -> list[dict]:
    return sorted([e for e in comm_map["edges"] if e["rps"] >= threshold_rps],
                  key=lambda e: -e["rps"])
