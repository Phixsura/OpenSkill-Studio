"""Fleet D1 — track Cloudflare edge SQLite."""
from __future__ import annotations
def fleet_d1_status(databases: list[dict]) -> dict:
    active = [d for d in databases if d.get("active", True)]
    rows_read = sum(d.get("rows_read_24h", 0) for d in databases)
    rows_written = sum(d.get("rows_written_24h", 0) for d in databases)
    return {"databases": len(databases), "active": len(active), "rows_read_24h": rows_read,
            "rows_written_24h": rows_written, "all_active": len(active) == len(databases)}
