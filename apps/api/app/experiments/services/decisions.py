"""Decision registry (ADR-017 §11, Part J).

Decisions are recorded ONLY from status `analyzed` and must reference the
result hash of an actually-recorded analysis run — no decide-before-analyze.
Observational experiments may never take a `promote` decision (stricter than
the ADR's draft gate: defense starts at the decision, §2 posture). The
registry is searchable organizational memory; the meta endpoint aggregates
the corpus for §11 v2 meta-analysis.
"""

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import ExperimentEvent, ExperimentVersion
from app.experiments.models.decision import DECISIONS, DecisionRecord
from app.experiments.models.guardrail import GuardrailEvent
from app.experiments.schemas import ExperimentSpec
from app.experiments.services.experiments import ExperimentService
from app.models.user import User

EXTEND_DEFAULT_DAYS = 30

# LIKE metacharacters in user search input act as wildcards (R394 lesson)
_LIKE_ESCAPE = str.maketrans({"%": r"\%", "_": r"\_", "\\": "\\\\"})


class DecisionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _analysis_hash_exists(self, experiment_id: str, result_hash: str) -> bool:
        row = (
            await self.db.execute(
                select(ExperimentEvent.id)
                .where(
                    ExperimentEvent.experiment_id == experiment_id,
                    ExperimentEvent.event_type == "analysis_look",
                    ExperimentEvent.payload["result_hash"].astext == result_hash,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        return row is not None

    async def _guardrail_outcome(self, experiment_id: str) -> dict:
        rows = (
            await self.db.execute(
                select(GuardrailEvent.guardrail_key, GuardrailEvent.action, func.count())
                .where(GuardrailEvent.experiment_id == experiment_id)
                .group_by(GuardrailEvent.guardrail_key, GuardrailEvent.action)
            )
        ).all()
        return {
            "events": [
                {"guardrail_key": key, "action": action, "count": count}
                for key, action, count in rows
            ],
            "clean": not rows,
        }

    async def create(
        self,
        experiment_id: str,
        *,
        decision: str,
        summary: str,
        analysis_result_hash: str,
        actor: User,
        uncertainty: dict | None = None,
        segments: dict | None = None,
        evidence: dict | None = None,
        extend_days: int = EXTEND_DEFAULT_DAYS,
    ) -> DecisionRecord:
        if decision not in DECISIONS:
            raise AppError(
                "VALIDATION_ERROR", f"Unknown decision: {decision} (allowed: {sorted(DECISIONS)})", 422
            )
        esvc = ExperimentService(self.db)
        exp = await esvc._get_locked(experiment_id)  # noqa: SLF001 — same package
        if exp.status != "analyzed":
            raise AppError(
                "DECISION_STATE_INVALID",
                f"Decisions require status analyzed (got {exp.status})",
                422,
            )
        if not await self._analysis_hash_exists(experiment_id, analysis_result_hash):
            raise AppError(
                "DECISION_HASH_MISMATCH",
                "analysis_result_hash does not match any recorded analysis run",
                422,
            )
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == experiment_id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one()
        spec = ExperimentSpec.model_validate(latest.spec)
        if decision == "promote" and spec.analysis_type != "randomized":
            # Stricter than the draft-time gate on purpose (§2 posture)
            raise AppError(
                "PROMOTION_REQUIRES_RANDOMIZED",
                "Observational analyses cannot promote — associations only",
                422,
            )
        record = DecisionRecord(
            experiment_id=experiment_id,
            experiment_version=exp.current_version,
            decision=decision,
            summary=summary,
            domain=exp.domain,
            analysis_type=spec.analysis_type,
            analysis_result_hash=analysis_result_hash,
            uncertainty=uncertainty or {},
            segments=segments or {},
            guardrail_outcome=await self._guardrail_outcome(experiment_id),
            evidence=evidence or {},
            approver_user_id=actor.id,
        )
        self.db.add(record)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise AppError(
                "DECISION_STATE_INVALID",
                "Experiment already has a terminal decision",
                409,
            ) from exc
        if decision == "promote":
            await esvc.transition(experiment_id, to_status="promoted", actor=actor)
        elif decision == "reject":
            await esvc.transition(experiment_id, to_status="rejected", actor=actor)
        elif decision == "extend" and exp.analysis_close_at is not None:
            exp.analysis_close_at = exp.analysis_close_at + timedelta(days=extend_days)
        await esvc._record_event(  # noqa: SLF001 — same package
            experiment_id,
            event_type="decision_recorded",
            actor_user_id=actor.id,
            payload={"decision": decision, "record_id": record.id,
                     "analysis_result_hash": analysis_result_hash},
        )
        await self.db.flush()
        return record

    async def get(self, decision_id: str) -> DecisionRecord:
        record = await self.db.get(DecisionRecord, decision_id)
        if not record:
            raise AppError("EXPERIMENT_NOT_FOUND", "Decision record not found", 404)
        return record

    async def search(
        self,
        *,
        domain: str | None = None,
        decision: str | None = None,
        q: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[DecisionRecord], int, str | None]:
        base = select(DecisionRecord)
        if domain:
            base = base.where(DecisionRecord.domain == domain)
        if decision:
            base = base.where(DecisionRecord.decision == decision)
        if q:
            escaped = q.translate(_LIKE_ESCAPE)
            base = base.where(
                func.lower(DecisionRecord.summary).like(f"%{escaped.lower()}%", escape="\\")
            )
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        page = base.order_by(DecisionRecord.id.desc())
        if cursor:
            page = page.where(DecisionRecord.id < cursor)
        rows = list((await self.db.execute(page.limit(limit))).scalars())
        next_cursor = rows[-1].id if len(rows) == limit else None
        return rows, total, next_cursor

    async def meta(self, *, domain: str | None = None) -> dict:
        """§11 v2 corpus aggregates. Observational records are excluded from
        the win-rate (they cannot promote by construction, but stay counted)."""
        base = select(DecisionRecord.decision, DecisionRecord.analysis_type, func.count())
        if domain:
            base = base.where(DecisionRecord.domain == domain)
        rows = (await self.db.execute(base.group_by(
            DecisionRecord.decision, DecisionRecord.analysis_type
        ))).all()
        by_decision: dict[str, int] = {}
        randomized_terminal = 0
        randomized_promoted = 0
        for decision, analysis_type, count in rows:
            by_decision[decision] = by_decision.get(decision, 0) + count
            if analysis_type == "randomized" and decision in ("promote", "reject"):
                randomized_terminal += count
                if decision == "promote":
                    randomized_promoted += count
        return {
            "total": sum(by_decision.values()),
            "by_decision": by_decision,
            "win_rate": (
                randomized_promoted / randomized_terminal if randomized_terminal else None
            ),
        }
