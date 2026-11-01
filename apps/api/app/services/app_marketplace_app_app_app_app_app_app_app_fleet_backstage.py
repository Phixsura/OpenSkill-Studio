"""Fleet Backstage adoption — track developer portal integration."""
from __future__ import annotations
def fleet_backstage_adoption(components: list[dict]) -> dict:
    registered = [c for c in components if c.get("in_backstage", False)]
    with_techdocs = [c for c in registered if c.get("has_techdocs", False)]
    pct = round(len(registered) / max(len(components), 1) * 100, 1)
    return {"total": len(components), "registered": len(registered),
            "with_techdocs": len(with_techdocs), "coverage_pct": pct}
