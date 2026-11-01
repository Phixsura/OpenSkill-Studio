"""Fleet Neo4j — track graph database health."""
from __future__ import annotations
def fleet_neo4j_status(instances: list[dict]) -> dict:
    available = [i for i in instances if i.get("available", True)]
    total_nodes = sum(i.get("node_count", 0) for i in instances)
    total_rels = sum(i.get("relationship_count", 0) for i in instances)
    return {"instances": len(instances), "available": len(available), "nodes": total_nodes,
            "relationships": total_rels, "healthy": len(available) == len(instances)}
