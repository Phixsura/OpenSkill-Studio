"""App API Developer Webhook Event Ordering — ensure correct event delivery order."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class OrderedEvent:
    event_id: str
    sequence_number: int
    partition_key: str
    delivered: bool = False

@dataclass
class PartitionState:
    partition_key: str
    last_delivered_seq: int = 0
    pending_count: int = 0
    out_of_order_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformWebhookEventOrdering:
    def __init__(self) -> None:
        self._partitions: dict[tuple[str, str], PartitionState] = {}

    def enqueue(self, installation_id: str, partition_key: str, event_id: str, sequence_number: int) -> PartitionState:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, partition_key)
        if key not in self._partitions:
            self._partitions[key] = PartitionState(partition_key=partition_key)
        p = self._partitions[key]
        p.pending_count += 1
        if sequence_number < p.last_delivered_seq:
            p.out_of_order_count += 1
        return p

    def deliver(self, installation_id: str, partition_key: str, sequence_number: int) -> PartitionState:
        key = (installation_id, partition_key)
        p = self._partitions.get(key)
        if p is None: raise KeyError(f"No partition {partition_key}")
        p.last_delivered_seq = max(p.last_delivered_seq, sequence_number)
        p.pending_count = max(0, p.pending_count - 1)
        return p

    def out_of_order_partitions(self, installation_id: str) -> list[PartitionState]:
        return [p for (inst, _), p in self._partitions.items() if inst == installation_id and p.out_of_order_count > 0]

    def all_partitions(self, installation_id: str) -> list[PartitionState]:
        return [p for (inst, _), p in self._partitions.items() if inst == installation_id]
