"""API Consumer Request Bulkhead — isolate failures with bulkhead pattern."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class BulkheadPartition:
    partition_id: str
    name: str
    max_concurrent: int
    active: int = 0
    queued: int = 0
    rejected: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkhead:
    def __init__(self) -> None:
        self._partitions: dict[tuple[str, str], BulkheadPartition] = {}

    def create_partition(self, installation_id: str, partition: BulkheadPartition) -> BulkheadPartition:
        if not installation_id: raise ValueError("installation_id is required")
        if partition.max_concurrent < 1: raise ValueError("max_concurrent must be >= 1")
        key = (installation_id, partition.partition_id)
        if key in self._partitions: raise ValueError(f"Partition {partition.partition_id} exists")
        self._partitions[key] = partition
        return partition

    def try_acquire(self, installation_id: str, partition_id: str) -> bool:
        p = self._partitions.get((installation_id, partition_id))
        if p is None: return True  # no partition = no limit
        if p.active >= p.max_concurrent:
            p.rejected += 1
            return False
        p.active += 1
        return True

    def release(self, installation_id: str, partition_id: str) -> None:
        p = self._partitions.get((installation_id, partition_id))
        if p and p.active > 0: p.active -= 1

    def utilization(self, installation_id: str, partition_id: str) -> float:
        p = self._partitions.get((installation_id, partition_id))
        if p is None or p.max_concurrent == 0: return 0.0
        return round((p.active / p.max_concurrent) * 100, 1)

    def list_partitions(self, installation_id: str) -> list[BulkheadPartition]:
        return [p for (inst, _), p in self._partitions.items() if inst == installation_id]
