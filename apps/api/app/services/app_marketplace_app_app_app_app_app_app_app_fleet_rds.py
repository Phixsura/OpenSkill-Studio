"""Fleet RDS — track managed database health."""
from __future__ import annotations
def fleet_rds_status(instances: list[dict]) -> dict:
    available = [i for i in instances if i.get("status") == "available"]
    multi_az = [i for i in instances if i.get("multi_az", False)]
    total_storage = sum(i.get("storage_gb", 0) for i in instances)
    return {"instances": len(instances), "available": len(available), "multi_az": len(multi_az),
            "storage_gb": total_storage, "all_available": len(available) == len(instances)}
