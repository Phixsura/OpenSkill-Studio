"""Fleet Qdrant — track Qdrant vector search health."""
from __future__ import annotations
def fleet_qdrant_status(collections: list[dict]) -> dict:
    green = [c for c in collections if c.get("status") == "green"]
    total_points = sum(c.get("points", 0) for c in collections)
    return {"collections": len(collections), "green": len(green),
            "total_points": total_points, "healthy": len(green) == len(collections)}
