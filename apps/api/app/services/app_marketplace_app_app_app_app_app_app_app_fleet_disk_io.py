"""Fleet disk I/O — aggregate disk read/write across fleet."""
from __future__ import annotations
def fleet_disk_io(services: list[dict]) -> dict:
    reads = sum(s.get("disk_read_mbps", 0) for s in services)
    writes = sum(s.get("disk_write_mbps", 0) for s in services)
    return {"read_mbps": round(reads, 1), "write_mbps": round(writes, 1),
            "total_iops": round(reads + writes, 1), "saturated": (reads + writes) > 1000}
