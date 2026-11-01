"""Fleet Log Archive v9 — track long-term log retention and compliance."""
from __future__ import annotations
def fleet_log_archive_v9(archives: list[dict]) -> dict:
    compressed = [a for a in archives if a.get("compressed")]
    size_tb = sum(a.get("size_tb", 0) for a in archives)
    retention_met = all(a.get("retention_met", True) for a in archives)
    return {"archives": len(archives), "compressed": len(compressed), "size_tb": round(size_tb, 1),
            "retention_compliant": retention_met, "healthy": retention_met}
