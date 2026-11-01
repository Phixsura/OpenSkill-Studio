"""Fleet Data Catalog v9 — track data asset discovery and lineage."""
from __future__ import annotations
def fleet_data_catalog_v9(assets: list[dict]) -> dict:
    cataloged = [a for a in assets if a.get("cataloged")]
    with_lineage = [a for a in assets if a.get("lineage")]
    owners = len({a.get("owner") for a in assets if a.get("owner")})
    return {"assets": len(assets), "cataloged": len(cataloged), "with_lineage": len(with_lineage),
            "owners": owners, "healthy": len(cataloged) == len(assets)}
