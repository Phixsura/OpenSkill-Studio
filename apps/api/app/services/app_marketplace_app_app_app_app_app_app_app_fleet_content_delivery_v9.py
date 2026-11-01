"""Fleet Content Delivery v9 — track CDN asset delivery and optimization."""
from __future__ import annotations
def fleet_content_delivery_v9(assets: list[dict]) -> dict:
    optimized = [a for a in assets if a.get("optimized")]
    compressed = [a for a in assets if a.get("compressed")]
    bandwidth_saved = sum(a.get("bandwidth_saved_gb", 0) for a in assets)
    return {"assets": len(assets), "optimized": len(optimized), "compressed": len(compressed),
            "bandwidth_saved_gb": round(bandwidth_saved, 1), "healthy": True}
