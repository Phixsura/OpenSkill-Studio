"""Production telemetry as real-world evidence (ADR-016 Part G).

Aggregates existing WorkflowRun/StepRun data into privacy-safe snapshots.
Cross-tenant aggregates require sample_size >= 20 AND >= 3 contributing orgs.
Benchmark-vs-production divergence is FLAGGED (change event), never used to
silently change rankings.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.graph import (
    TELEMETRY_MIN_ORGS,
    TELEMETRY_MIN_SAMPLE,
    TelemetrySnapshot,
)
from app.exceptions import AppError


def _percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(int(len(ordered) * pct), len(ordered) - 1)
    return ordered[idx]


def aggregate_metrics(rows: list[dict]) -> dict:
    """Pure aggregation over per-execution rows (unit-testable)."""
    if not rows:
        return {}
    latencies = [r["latency_ms"] for r in rows if r.get("latency_ms") is not None]
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    successes = sum(1 for r in rows if r.get("succeeded"))
    retries = sum(int(r.get("retries") or 0) for r in rows)
    approvals = [r["approved"] for r in rows if r.get("approved") is not None]
    error_dist: dict[str, int] = {}
    for r in rows:
        code = r.get("error_code")
        if code:
            error_dist[str(code)[:60]] = error_dist.get(str(code)[:60], 0) + 1
    metrics = {
        "success_rate": round(successes / len(rows), 4),
        "retry_rate": round(retries / len(rows), 4),
        "latency_p50_ms": _percentile(latencies, 0.5),
        "latency_p95_ms": _percentile(latencies, 0.95),
        "effective_cost_usd_avg": round(sum(costs) / len(costs), 6) if costs else None,
        "error_distribution": error_dist,
    }
    if approvals:
        metrics["human_approval_rate"] = round(
            sum(1 for a in approvals if a) / len(approvals), 4
        )
    return metrics


class TelemetryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def write_snapshot(
        self,
        *,
        entity_kind: str,
        entity_id: str,
        window_start: datetime,
        window_end: datetime,
        rows: list[dict],
        org_id: str | None,
        contributing_orgs: int | None = None,
    ) -> TelemetrySnapshot:
        """Persist one aggregate. Cross-tenant rows enforce privacy thresholds."""
        if org_id is None:
            orgs = contributing_orgs if contributing_orgs is not None else len(
                {r.get("org_id") for r in rows if r.get("org_id")}
            )
            if len(rows) < TELEMETRY_MIN_SAMPLE or orgs < TELEMETRY_MIN_ORGS:
                raise AppError(
                    "ECO_TELEMETRY_THRESHOLD",
                    f"Cross-tenant aggregate needs >= {TELEMETRY_MIN_SAMPLE} samples "
                    f"from >= {TELEMETRY_MIN_ORGS} orgs",
                    422,
                )
        metrics = aggregate_metrics(rows)
        stmt = (
            pg_insert(TelemetrySnapshot)
            .values(
                entity_kind=entity_kind,
                entity_id=entity_id,
                window_start=window_start,
                window_end=window_end,
                org_id=org_id,
                sample_size=len(rows),
                metrics=metrics,
            )
            .on_conflict_do_update(
                constraint="uq_eco_telemetry_window",
                set_={"sample_size": len(rows), "metrics": metrics},
            )
            .returning(TelemetrySnapshot.id)
        )
        snap_id = await self.db.scalar(stmt)
        await self.db.flush()
        return await self.db.get(TelemetrySnapshot, snap_id)

    async def aggregate_workflow_runs(
        self,
        *,
        window_start: datetime,
        window_end: datetime,
    ) -> list[TelemetrySnapshot]:
        """Derive per-offering snapshots from WorkflowStepRun rows in a window."""
        from app.models.workflow_run import WorkflowRun, WorkflowStepRun

        step_rows = await self.db.execute(
            select(WorkflowStepRun, WorkflowRun.org_id)
            .join(WorkflowRun, WorkflowStepRun.run_id == WorkflowRun.id)
            .where(
                WorkflowStepRun.created_at >= window_start,
                WorkflowStepRun.created_at < window_end,
            )
        )
        by_offering: dict[str, list[dict]] = {}
        for step, org_id in step_rows:
            if not step.offering_id:
                continue
            status_val = getattr(step.status, "value", step.status)
            latency_ms = None
            if step.started_at and step.finished_at:
                latency_ms = (step.finished_at - step.started_at).total_seconds() * 1000
            by_offering.setdefault(step.offering_id, []).append(
                {
                    "org_id": org_id,
                    "succeeded": str(status_val).lower() == "completed",
                    "retries": max((step.attempt or 0) - 1, 0),
                    "latency_ms": latency_ms,
                    "cost_usd": None,  # step-level cost lives in cp metering
                    "error_code": step.error_code,
                }
            )
        snapshots = []
        for offering_id, rows in by_offering.items():
            # Per-org snapshots always allowed
            by_org: dict[str, list[dict]] = {}
            for row in rows:
                if row["org_id"]:
                    by_org.setdefault(row["org_id"], []).append(row)
            for org_id, org_rows in by_org.items():
                snapshots.append(
                    await self.write_snapshot(
                        entity_kind="provider_offering",
                        entity_id=offering_id,
                        window_start=window_start,
                        window_end=window_end,
                        rows=org_rows,
                        org_id=org_id,
                    )
                )
            # Cross-tenant only above thresholds
            orgs = len(by_org)
            if len(rows) >= TELEMETRY_MIN_SAMPLE and orgs >= TELEMETRY_MIN_ORGS:
                snapshots.append(
                    await self.write_snapshot(
                        entity_kind="provider_offering",
                        entity_id=offering_id,
                        window_start=window_start,
                        window_end=window_end,
                        rows=rows,
                        org_id=None,
                        contributing_orgs=orgs,
                    )
                )
        return snapshots

    async def list_snapshots(
        self,
        *,
        entity_kind: str | None = None,
        entity_id: str | None = None,
        org_id: str | None = None,
        include_cross_tenant: bool = True,
        limit: int = 50,
    ) -> list[TelemetrySnapshot]:
        """org-scoped rows are only visible to that org (caller pre-authorizes)."""
        from sqlalchemy import or_

        query = select(TelemetrySnapshot)
        if entity_kind:
            query = query.where(TelemetrySnapshot.entity_kind == entity_kind)
        if entity_id:
            query = query.where(TelemetrySnapshot.entity_id == entity_id)
        if org_id is not None:
            visibility = [TelemetrySnapshot.org_id == org_id]
            if include_cross_tenant:
                visibility.append(TelemetrySnapshot.org_id.is_(None))
            query = query.where(or_(*visibility))
        else:
            query = query.where(TelemetrySnapshot.org_id.is_(None))
        rows = await self.db.scalars(
            query.order_by(TelemetrySnapshot.window_end.desc()).limit(limit)
        )
        return list(rows)

    async def detect_divergence(
        self, entity_kind: str, entity_id: str, *, benchmark_scores: dict
    ) -> bool:
        """Flag benchmark-vs-production divergence as a change event (§3.7).

        Comparable pair: benchmark 'reliability' vs telemetry success_rate.
        Divergence > 0.25 absolute → degraded change event. Never mutates
        rankings.
        """
        snap = await self.db.scalar(
            select(TelemetrySnapshot)
            .where(
                TelemetrySnapshot.entity_kind == entity_kind,
                TelemetrySnapshot.entity_id == entity_id,
                TelemetrySnapshot.org_id.is_(None),
            )
            .order_by(TelemetrySnapshot.window_end.desc())
            .limit(1)
        )
        if not snap:
            return False
        bench_rel = benchmark_scores.get("reliability")
        prod_rel = (snap.metrics or {}).get("success_rate")
        if bench_rel is None or prod_rel is None:
            return False
        if abs(float(bench_rel) - float(prod_rel)) <= 0.25:
            return False
        # Need an observation anchor: reuse the latest observation for entity if any
        from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation

        # Idempotence: while an unacknowledged divergence flag is open for this
        # entity, don't stack another (re-flag only after an operator acks)
        open_flag = await self.db.scalar(
            select(ChangeEvent.id)
            .where(
                ChangeEvent.canonical_entity_id == entity_id,
                ChangeEvent.field == "benchmark_production_divergence",
                ChangeEvent.acknowledged.is_(False),
            )
            .limit(1)
        )
        if open_flag:
            return False

        obs = await self.db.scalar(
            select(EcosystemObservation)
            .where(
                EcosystemObservation.canonical_entity_kind == entity_kind,
                EcosystemObservation.canonical_entity_id == entity_id,
            )
            .order_by(EcosystemObservation.observed_at.desc())
            .limit(1)
        )
        if not obs:
            return False
        self.db.add(
            ChangeEvent(
                observation_id=obs.id,
                change_type="lifecycle",
                field="benchmark_production_divergence",
                old_value={"benchmark_reliability": float(bench_rel)},
                new_value={"production_success_rate": float(prod_rel)},
                severity="degraded",
                entity_kind=entity_kind,
                canonical_entity_id=entity_id,
            )
        )
        await self.db.flush()
        return True
