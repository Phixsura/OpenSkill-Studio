"""Fleet Kinesis — track real-time streaming data."""
from __future__ import annotations
def fleet_kinesis_status(streams: list[dict]) -> dict:
    active = [s for s in streams if s.get("status") == "ACTIVE"]
    total_shards = sum(s.get("shards", 0) for s in streams)
    records_per_sec = sum(s.get("records_per_sec", 0) for s in streams)
    return {"streams": len(streams), "active": len(active), "shards": total_shards,
            "records_per_sec": records_per_sec, "all_active": len(active) == len(streams)}
