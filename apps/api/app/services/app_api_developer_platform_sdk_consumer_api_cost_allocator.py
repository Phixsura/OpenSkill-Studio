"""Endpoint Cost Allocator — per-endpoint cost tracking with consumer attribution."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class CostRecord:
    endpoint_id: str
    consumer_id: str
    period: str
    requests: int
    compute_cost_cents: int
    bandwidth_cost_cents: int
    storage_cost_cents: int = 0


@dataclass
class CostAllocator:
    """Track and allocate infrastructure costs per endpoint and consumer."""

    _records: list[CostRecord] = field(default_factory=list)
    _unit_costs: dict[str, dict[str, float]] = field(default_factory=dict)

    def set_unit_cost(self, endpoint_id: str, compute_per_req: float = 0.001,
                      bandwidth_per_mb: float = 0.01) -> dict:
        self._unit_costs[endpoint_id] = {
            "compute_per_req": compute_per_req,
            "bandwidth_per_mb": bandwidth_per_mb,
        }
        return {"endpoint_id": endpoint_id, "configured": True}

    def record(self, record: CostRecord) -> dict:
        if record.requests < 0:
            raise ValueError("Requests must be non-negative")
        self._records.append(record)
        logger.info("cost_recorded", endpoint_id=record.endpoint_id,
                     consumer_id=record.consumer_id)
        return {"recorded": True, "total_records": len(self._records)}

    def get_endpoint_cost(self, endpoint_id: str, period: str | None = None) -> dict:
        records = [r for r in self._records if r.endpoint_id == endpoint_id]
        if period:
            records = [r for r in records if r.period == period]
        if not records:
            return {"endpoint_id": endpoint_id, "total_cost_cents": 0}
        total_compute = sum(r.compute_cost_cents for r in records)
        total_bandwidth = sum(r.bandwidth_cost_cents for r in records)
        total_storage = sum(r.storage_cost_cents for r in records)
        total_requests = sum(r.requests for r in records)
        total = total_compute + total_bandwidth + total_storage
        return {
            "endpoint_id": endpoint_id,
            "total_requests": total_requests,
            "compute_cents": total_compute,
            "bandwidth_cents": total_bandwidth,
            "storage_cents": total_storage,
            "total_cost_cents": total,
            "total_dollars": round(total / 100, 2),
        }

    def get_consumer_cost(self, consumer_id: str, period: str | None = None) -> dict:
        records = [r for r in self._records if r.consumer_id == consumer_id]
        if period:
            records = [r for r in records if r.period == period]
        if not records:
            return {"consumer_id": consumer_id, "total_cost_cents": 0}
        total = sum(r.compute_cost_cents + r.bandwidth_cost_cents + r.storage_cost_cents
                    for r in records)
        by_endpoint: dict[str, int] = {}
        for r in records:
            cost = r.compute_cost_cents + r.bandwidth_cost_cents + r.storage_cost_cents
            by_endpoint[r.endpoint_id] = by_endpoint.get(r.endpoint_id, 0) + cost
        return {
            "consumer_id": consumer_id,
            "total_cost_cents": total,
            "total_dollars": round(total / 100, 2),
            "by_endpoint": by_endpoint,
        }

    def get_top_costs(self, period: str | None = None, limit: int = 10) -> list[dict]:
        consumer_costs: dict[str, int] = {}
        for r in self._records:
            if period and r.period != period:
                continue
            cost = r.compute_cost_cents + r.bandwidth_cost_cents + r.storage_cost_cents
            consumer_costs[r.consumer_id] = consumer_costs.get(r.consumer_id, 0) + cost
        ranked = sorted(consumer_costs.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"consumer_id": c, "total_cents": v, "total_dollars": round(v / 100, 2)}
                for c, v in ranked]

    def get_period_summary(self, period: str) -> dict:
        records = [r for r in self._records if r.period == period]
        if not records:
            return {"period": period, "total_cost_cents": 0}
        total = sum(r.compute_cost_cents + r.bandwidth_cost_cents + r.storage_cost_cents
                    for r in records)
        return {
            "period": period,
            "record_count": len(records),
            "unique_consumers": len(set(r.consumer_id for r in records)),
            "unique_endpoints": len(set(r.endpoint_id for r in records)),
            "total_cost_cents": total,
            "total_dollars": round(total / 100, 2),
        }
