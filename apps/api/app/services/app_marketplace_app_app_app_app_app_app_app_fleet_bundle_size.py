"""Fleet bundle size — track JS bundle sizes."""
from __future__ import annotations
def fleet_bundle_size(bundles: list[dict]) -> dict:
    total_kb = sum(b.get("size_kb", 0) for b in bundles)
    large = [b for b in bundles if b.get("size_kb", 0) > 200]
    return {"total_kb": total_kb, "bundles": len(bundles), "large": len(large),
            "optimized": len(large) == 0}
