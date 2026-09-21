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

    async def overview(self) -> dict:
        """Ecosystem health snapshot for the operator workspace."""
        week_ago = datetime.now(UTC) - timedelta(days=7)
        return {
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
