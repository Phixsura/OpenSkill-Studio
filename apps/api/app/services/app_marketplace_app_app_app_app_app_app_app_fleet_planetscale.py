"""Fleet PlanetScale — track serverless MySQL platform."""
from __future__ import annotations
def fleet_planetscale_status(databases: list[dict]) -> dict:
    production = [d for d in databases if d.get("branch") == "main"]
    deploy_requests = sum(d.get("deploy_requests_open", 0) for d in databases)
    rows_read = sum(d.get("rows_read_24h", 0) for d in databases)
    return {"databases": len(databases), "production": len(production),
            "deploy_requests": deploy_requests, "rows_read_24h": rows_read}
