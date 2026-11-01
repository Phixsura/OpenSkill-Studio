"""Fleet DynamoDB — track managed NoSQL table health."""
from __future__ import annotations
def fleet_dynamodb_status(tables: list[dict]) -> dict:
    active = [t for t in tables if t.get("status") == "ACTIVE"]
    throttled = [t for t in tables if t.get("throttled_reads", 0) > 0 or t.get("throttled_writes", 0) > 0]
    total_rcu = sum(t.get("consumed_rcu", 0) for t in tables)
    return {"tables": len(tables), "active": len(active), "throttled": len(throttled),
            "consumed_rcu": total_rcu, "healthy": len(throttled) == 0}
