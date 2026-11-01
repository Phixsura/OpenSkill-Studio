"""Fleet BigQuery — track data analytics warehouse."""
from __future__ import annotations
def fleet_bigquery_status(datasets: list[dict]) -> dict:
    total_tables = sum(d.get("tables", 0) for d in datasets)
    total_storage_tb = sum(d.get("storage_tb", 0) for d in datasets)
    queries_24h = sum(d.get("queries_24h", 0) for d in datasets)
    bytes_processed = sum(d.get("bytes_processed_tb", 0) for d in datasets)
    return {"datasets": len(datasets), "tables": total_tables, "storage_tb": round(total_storage_tb, 1),
            "queries_24h": queries_24h, "bytes_processed_tb": round(bytes_processed, 1)}
