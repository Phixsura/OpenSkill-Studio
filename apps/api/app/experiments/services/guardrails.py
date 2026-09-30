"""Guardrail evaluation & SRM health check (ADR-017 §9, Part D).

Hard rule: a breach AUTO-PAUSES via the same locked state machine every
transition uses; there is no auto-promote path in this module or anywhere in
the experiments package (a source-scan test enforces it). SRM is built-in and
not disableable — sample-ratio mismatch is a data-quality alarm, never a
pause (a paused experiment can't collect the evidence to diagnose it).

Guardrail observation windows are sliding (now - window_hours, now] and reuse
the same metric SOURCE_REGISTRY as snapshots; an unwired source SKIPS loudly
(the definitions land before their exp07 integrations) rather than blocking
every experiment on the slowest integration.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentVersion,
    MetricDefinition,
)
from app.experiments.models.guardrail import (
    INCIDENT_GUARDRAIL_KEY,
    SRM_GUARDRAIL_KEY,
    GuardrailEvent,
)
from app.experiments.schemas import ExperimentSpec
from app.experiments.services.metrics import SOURCE_REGISTRY, MetricService
from app.models.user import User

log = structlog.get_logger()

# Chi-square critical values at alpha = 0.001 for df 1..9 (variants <= 10).
# Table constants beat a hand-rolled sf() here — no numeric risk, exact gate.
_CHI2_CRIT_P001 = {
    1: 10.828, 2: 13.816, 3: 16.266, 4: 18.467, 5: 20.515,
    6: 22.458, 7: 24.322, 8: 26.124, 9: 27.877,
}

# SRM needs a sample before the ratio test means anything
SRM_MIN_ASSIGNMENTS = 100

# Re-alert suppression: one open SRM alert per experiment per day
_SRM_REALERT_HOURS = 24


class GuardrailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _spec(self, exp: Experiment) -> ExperimentSpec | None:
        latest = (
            await self.db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one_or_none()
        return ExperimentSpec.model_validate(latest.spec) if latest else None

    # ── SRM (built-in, alert-only) ───────────────────────────────────

    async def check_srm(self, exp: Experiment, spec: ExperimentSpec) -> dict | None:
        counts_q = (
            select(ExperimentAssignment.variant_key, ExperimentAssignment.id)
            .where(
                ExperimentAssignment.experiment_id == exp.id,
                ExperimentAssignment.is_holdout.is_(False),
            )
        )
        counts: dict[str, int] = {}
        for variant_key, _id in (await self.db.execute(counts_q)).all():
            counts[variant_key] = counts.get(variant_key, 0) + 1
        total = sum(counts.values())
        if total < SRM_MIN_ASSIGNMENTS:
            return None
        weights = {v.key: v.weight_bp for v in spec.variants}
        df = len(weights) - 1
        if df < 1 or df > 9:
            return None
        chi2 = 0.0
        for key, weight_bp in weights.items():
            expected = total * weight_bp / 10_000
            if expected <= 0:
                continue
            observed = counts.get(key, 0)
            chi2 += (observed - expected) ** 2 / expected
        if chi2 < _CHI2_CRIT_P001[df]:
            return None
        # Suppress duplicate alerts within the re-alert window
        recent = (
            await self.db.execute(
                select(GuardrailEvent)
                .where(
                    GuardrailEvent.experiment_id == exp.id,
                    GuardrailEvent.guardrail_key == SRM_GUARDRAIL_KEY,
                    GuardrailEvent.created_at
                    >= datetime.now(UTC) - timedelta(hours=_SRM_REALERT_HOURS),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        detail = {"chi2": round(chi2, 3), "df": df, "counts": counts, "total": total}
        if recent is None:
            self.db.add(
                GuardrailEvent(
                    experiment_id=exp.id,
                    guardrail_key=SRM_GUARDRAIL_KEY,
                    action="alerted",
                    auto=True,
                    detail=detail,
                )
            )
            log.warning("experiment_srm_alert", experiment_id=exp.id, **detail)
        return detail

    # ── Guardrail metrics ────────────────────────────────────────────

    @staticmethod
    def _observed(definition: MetricDefinition, combined: dict) -> float | None:
        """Collapse combined sufficient stats into the guarded scalar.
        binary/rate → numerator/denominator; continuous → sum or mean
        (definition.spec.guardrail_aggregate overrides; cost is a sum)."""
        aggregate = definition.spec.get("guardrail_aggregate")
        if aggregate is None:
            aggregate = "rate" if definition.kind in ("binary", "rate") else "mean"
        if aggregate == "rate":
            denominator = combined.get("denominator") or 0
            if not denominator:
                return None
            return float(combined.get("numerator") or 0) / float(denominator)
        if aggregate == "sum":
            return float(combined.get("sum_value") or combined.get("numerator") or 0)
        # mean
        n = combined.get("n") or 0
        if not n:
            return None
        return float(combined.get("sum_value") or 0) / float(n)

    async def evaluate_experiment(
        self, experiment_id: str, *, now: datetime | None = None
    ) -> dict:
        """Evaluate every guardrail + SRM for one running experiment.
        Stamps last_guardrail_check_at even when nothing fires (sweep
        fairness — §106.26). Returns a summary dict.

        The default clock is the DATABASE's clock_timestamp(): exposures
        stamp occurred_at with the DB clock, so the sliding window must use
        the same clock — app/DB skew otherwise makes freshly written
        exposures invisible (the exact outbox R-fix class). clock_timestamp
        (not now()): now() freezes at transaction start, which equals
        occurred_at for same-transaction writes and the half-open window's
        strict `< end` would exclude them."""
        if now is None:
            from sqlalchemy import func as _sql_func

            now = (await self.db.execute(select(_sql_func.clock_timestamp()))).scalar_one()
            if now.tzinfo is None:  # driver may hand back naive UTC
                now = now.replace(tzinfo=UTC)
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        summary: dict = {"experiment_id": experiment_id, "status": exp.status, "breaches": []}
        if exp.status != "running":
            summary["skipped"] = True
            return summary
        spec = await self._spec(exp)
        if spec is None:
            summary["skipped"] = True
            return summary

        srm = await self.check_srm(exp, spec)
        if srm is not None:
            summary["srm"] = srm

        msvc = MetricService(self.db)
        variant_units = await msvc._variant_units(experiment_id)  # noqa: SLF001 — same package
        breaches: list[GuardrailEvent] = []
        for guardrail in spec.metrics.guardrails:
            definition = (
                await self.db.execute(
                    select(MetricDefinition).where(MetricDefinition.key == guardrail.metric_key)
                )
            ).scalar_one_or_none()
            if definition is None:
                log.warning(
                    "experiment_guardrail_metric_undefined",
                    experiment_id=experiment_id,
                    metric_key=guardrail.metric_key,
                )
                continue
            source = SOURCE_REGISTRY.get(definition.spec.get("source", ""))
            if source is None:
                log.warning(
                    "experiment_guardrail_source_unwired",
                    experiment_id=experiment_id,
                    metric_key=guardrail.metric_key,
                )
                continue
            window_start = now - timedelta(hours=guardrail.window_hours)
            stats = await source(
                self.db,
                experiment=exp,
                definition=definition,
                variant_units=variant_units,
                window_start=window_start,
                window_end=now,
                unit_type=spec.unit_type,
            )
            combined: dict = {}
            for values in stats.values():
                for k, v in values.items():
                    if v is not None:
                        combined[k] = combined.get(k, 0) + v
            observed = self._observed(definition, combined)
            if observed is None:
                continue
            breached = (
                observed > guardrail.threshold
                if guardrail.op == "lte"
                else observed < guardrail.threshold
            )
            if breached:
                event = GuardrailEvent(
                    experiment_id=experiment_id,
                    guardrail_key=guardrail.metric_key,
                    metric_key=guardrail.metric_key,
                    observed=observed,
                    threshold=guardrail.threshold,
                    window_start=window_start,
                    window_end=now,
                    action="paused",
                    auto=True,
                    detail={"op": guardrail.op, "combined": {k: float(v) for k, v in combined.items()}},
                )
                self.db.add(event)
                breaches.append(event)
                summary["breaches"].append(
                    {"metric_key": guardrail.metric_key, "observed": observed,
                     "threshold": guardrail.threshold}
                )

        if breaches:
            # One pause for any number of breaches — same locked state machine
            # every transition uses. NEVER a promote (§2.2).
            from app.experiments.services.experiments import ExperimentService

            esvc = ExperimentService(self.db)
            await esvc.transition(
                experiment_id,
                to_status="paused",
                actor=_system_actor(),
                reason=f"guardrail breach: {summary['breaches'][0]['metric_key']}",
            )
            await esvc._record_event(  # noqa: SLF001 — same package
                experiment_id,
                event_type="guardrail_paused",
                actor_user_id=None,
                payload={"breaches": summary["breaches"]},
            )
            log.warning(
                "experiment_guardrail_paused",
                experiment_id=experiment_id,
                breaches=summary["breaches"],
            )
        exp.last_guardrail_check_at = now
        await self.db.flush()
        return summary

    async def record_incident(
        self, experiment_id: str, *, actor: User, reason: str | None = None
    ) -> GuardrailEvent:
        """Manual security/privacy incident → immediate pause (Part D)."""
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        event = GuardrailEvent(
            experiment_id=experiment_id,
            guardrail_key=INCIDENT_GUARDRAIL_KEY,
            action="paused",
            auto=False,
            detail={"reason": reason or ""},
        )
        self.db.add(event)
        if exp.status == "running":
            from app.experiments.services.experiments import ExperimentService

            await ExperimentService(self.db).transition(
                experiment_id, to_status="paused", actor=actor, reason=reason or "manual incident"
            )
        await self.db.flush()
        return event

    async def list_events(self, experiment_id: str, *, limit: int = 200) -> list[GuardrailEvent]:
        q = (
            select(GuardrailEvent)
            .where(GuardrailEvent.experiment_id == experiment_id)
            # id tiebreak on the timestamp order (§99.8)
            .order_by(GuardrailEvent.created_at.desc(), GuardrailEvent.id.desc())
            .limit(limit)
        )
        return list((await self.db.execute(q)).scalars())


class _SystemActor:
    """Worker-driven pauses have no human actor; high-risk gates never apply
    to a PAUSE (pausing is always allowed and always safe)."""

    id = None
    role = None


def _system_actor() -> _SystemActor:
    return _SystemActor()
