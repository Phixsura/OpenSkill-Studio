"""Fleet AI ETL Engine — track Extract-Transform-Load for AI data."""
from __future__ import annotations
def fleet_ai_etl(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    jobs_24h = sum(e.get("jobs_24h", 0) for e in engines)
    records_processed = sum(e.get("records", 0) for e in engines)
    failures = sum(e.get("failures", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "jobs_24h": jobs_24h,
            "records": records_processed, "failures": failures, "reliable": failures == 0}
