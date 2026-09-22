"""Operator workspace aggregates (ADR-016 Part P)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.benchmark import BenchmarkRun
from app.ecosystem.models.catalog import ResolutionCandidate
from app.ecosystem.models.graph import ImpactAnalysis
from app.ecosystem.models.mapping import PriceObservation
from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
from app.ecosystem.models.replacement import ComponentDraft, ReplacementCandidate, RolloutPlan
from app.ecosystem.models.source import EcosystemSource


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _count(self, query) -> int:
        return (await self.db.scalar(select(func.count()).select_from(query.subquery()))) or 0

    async def _stale_source_count(self) -> int:
        """§16 (StatusGator): a feed that stopped succeeding is itself an
        incident — active sources overdue by 3× their sync interval."""
        now = datetime.now(UTC)
        rows = await self.db.scalars(
            select(EcosystemSource).where(EcosystemSource.status == "active")
        )
        stale = 0
        for source in rows:
            anchor = source.last_success_at or source.created_at
            if anchor and (now - anchor) > timedelta(
                minutes=3 * source.sync_interval_minutes
            ):
                stale += 1
        return stale

    async def coverage(self) -> dict:
        """Backstage maturity bar: per-kind catalog completeness — how many
        entities have a capability mapping, any benchmark, and any price
        observation. Ratios expose curation debt per dimension; entities are
        never hidden for being incomplete."""
        from sqlalchemy import distinct
        from sqlalchemy import select as sa_select

        from app.ecosystem.models.benchmark import BenchmarkRun
        from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL
        from app.ecosystem.models.mapping import CapabilityMapping

        # entity_ids present in each evidence dimension (one query each)
        mapped_ids = {
            row for row in await self.db.scalars(
                sa_select(distinct(CapabilityMapping.entity_id))
            )
        }
        priced_ids = {
            row for row in await self.db.scalars(
                sa_select(distinct(PriceObservation.entity_id))
            )
        }
        benched_ids = set()
        for run in await self.db.scalars(
            sa_select(BenchmarkRun).where(BenchmarkRun.status == "completed").limit(1000)
        ):
            target_id = (run.target or {}).get("entity_id")
            if target_id:
                benched_ids.add(target_id)
        out = {}
        for kind, model in CATALOG_KIND_TO_MODEL.items():
            ids = {row for row in await self.db.scalars(sa_select(model.id))}
            total = len(ids)
            out[kind] = {
                "total": total,
                "with_capability_mapping": len(ids & mapped_ids),
                "with_benchmark": len(ids & benched_ids),
                "with_pricing": len(ids & priced_ids),
            }
        return out

    async def overview(self) -> dict:
        """Ecosystem health snapshot for the operator workspace."""
        week_ago = datetime.now(UTC) - timedelta(days=7)
        return {
            "sources_stale": await self._stale_source_count(),
            "sources": {
                "active": await self._count(
                    select(EcosystemSource.id).where(EcosystemSource.status == "active")
                ),
                "paused": await self._count(
                    select(EcosystemSource.id).where(EcosystemSource.status == "paused")
                ),
                "error": await self._count(
                    select(EcosystemSource.id).where(EcosystemSource.status == "error")
                ),
            },
            "discoveries_7d": await self._count(
                select(EcosystemObservation.id).where(
                    EcosystemObservation.observed_at >= week_ago
                )
            ),
            # §11.1: review-queue visibility so curation debt can't rot silently
            "observations_unverified": await self._count(
                select(EcosystemObservation.id).where(
                    EcosystemObservation.human_verified.is_(False)
                )
            ),
            # §11.2: heuristic flags are advisory — surfaced, never blocking
            "injection_flagged_unverified": await self._count(
                select(EcosystemObservation.id).where(
                    EcosystemObservation.human_verified.is_(False),
                    EcosystemObservation.normalized["injection_flag"].as_boolean().is_(True),
                )
            ),
            "changes_unacknowledged": await self._count(
                select(ChangeEvent.id).where(ChangeEvent.acknowledged.is_(False))
            ),
            "security_critical_open": await self._count(
                select(ChangeEvent.id).where(
                    ChangeEvent.severity == "security_critical",
                    ChangeEvent.acknowledged.is_(False),
                )
            ),
            "pricing_unreviewed": await self._count(
                select(PriceObservation.id).where(
                    PriceObservation.reconciliation_status == "unreviewed"
                )
            ),
            "resolution_pending": await self._count(
                select(ResolutionCandidate.id).where(ResolutionCandidate.status == "pending")
            ),
            "benchmark_queue": await self._count(
                select(BenchmarkRun.id).where(BenchmarkRun.status.in_(("queued", "running")))
            ),
            "impact_open": await self._count(
                select(ImpactAnalysis.id).where(ImpactAnalysis.status == "open")
            ),
            "replacements_proposed": await self._count(
                select(ReplacementCandidate.id).where(
                    ReplacementCandidate.status == "proposed"
                )
            ),
            "drafts_in_review": await self._count(
                select(ComponentDraft.id).where(ComponentDraft.status == "in_review")
            ),
            "rollouts_active": await self._count(
                select(RolloutPlan.id).where(
                    RolloutPlan.status.in_(("running", "evaluating"))
                )
            ),
        }

    async def change_feed(
        self, *, severity: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[ChangeEvent]:
        query = select(ChangeEvent)
        if severity:
            query = query.where(ChangeEvent.severity == severity)
        rows = await self.db.scalars(
            query.order_by(ChangeEvent.detected_at.desc()).limit(limit).offset(offset)
        )
        return list(rows)
