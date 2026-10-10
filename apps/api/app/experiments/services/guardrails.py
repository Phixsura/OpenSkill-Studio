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

import re
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    ExperimentVersion,
    MetricDefinition,
)
from app.experiments.models.guardrail import (
    EXPOSURE_SRM_GUARDRAIL_KEY,
    EXPOSURE_SRM_WINDOW_GUARDRAIL_KEY,
    INCIDENT_GUARDRAIL_KEY,
    SRM_GUARDRAIL_KEY,
    SRM_WINDOW_GUARDRAIL_KEY,
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

# Defect #90: windowed SRM — slice width and its own minimum sample
SRM_WINDOW_HOURS = 24
SRM_WINDOW_MIN_ASSIGNMENTS = 100

# Exposure-SRM (§4.13 v2) needs a real exposed sample too
EXPOSURE_SRM_MIN_EXPOSED = 50

# Re-alert suppression: one open SRM alert per experiment per day
_SRM_REALERT_HOURS = 24


class GuardrailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _notify_alert(self, exp: Experiment, *, title: str, detail: dict) -> None:
        """Defect #38: alert-only findings (SRM, exposure-SRM, interaction)
        were silent outside the Console — the owner gets ONE notification per
        dedup window, fail-safe like the pause notification."""
        try:
            from app.services.notification import NotificationService

            # Defect #42 (the #41 class): the notification write runs under a
            # SAVEPOINT — a flush error here would otherwise poison the
            # session and sink the guardrail finding it merely annotates.
            async with self.db.begin_nested():
                await NotificationService(self.db).create(
                    user_id=exp.owner_user_id,
                    notification_type="experiment_guardrail",
                    title=title,
                    body="Alert only — the experiment keeps running; review the diagnostics.",
                    data={"experiment_id": exp.id, **detail},
                )
        except Exception:  # noqa: BLE001 — additive, never blocking
            log.warning("experiment_alert_notify_failed", experiment_id=exp.id)

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
        if spec.design == "switchback":
            # Defect #28: switchback rows all carry the placeholder variant —
            # a chi-square against the spec weights would ALWAYS fire. The
            # design randomizes TIME, not units; SRM does not apply.
            return None
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
            await self._notify_alert(
                exp, title=f"SRM alert on '{exp.title}'", detail=detail
            )
        return detail

    async def check_exposure_srm_window(
        self, exp: Experiment, *, notify: bool = True
    ) -> dict | None:
        """Defect #92: the windowed-SRM argument (#90) applied to trigger
        bias — chi-square of ONLY the last SRM_WINDOW_HOURS of exposed
        units against the cumulative assignment proportions. A late bias
        (deploy regression in the exposure call site) is diluted by the
        healthy cumulative mass. Alert-only, 24h-suppressed, own key."""
        spec = await self._spec(exp)
        if spec is None or spec.design == "switchback":
            return None  # same reason as check_srm (defect #28)
        from app.experiments.models.assignment import ExperimentExposure
        from app.experiments.services.assignment import AssignmentService

        assigned = (await AssignmentService(self.db).assignment_stats(exp.id))["variants"]
        total_assigned = sum(assigned.values())
        if total_assigned <= 0:
            return None
        window_start = datetime.now(UTC) - timedelta(hours=SRM_WINDOW_HOURS)
        exposed_q = (
            select(
                ExperimentAssignment.variant_key,
                func.count(func.distinct(ExperimentExposure.assignment_id)),
            )
            .join(
                ExperimentAssignment,
                ExperimentAssignment.id == ExperimentExposure.assignment_id,
            )
            .where(
                ExperimentExposure.experiment_id == exp.id,
                ExperimentExposure.occurred_at >= window_start,
            )
            .group_by(ExperimentAssignment.variant_key)
        )
        exposed = dict((await self.db.execute(exposed_q)).all())
        counts = {vk: exposed.get(vk, 0) for vk in assigned}
        total_exposed = sum(counts.values())
        if total_exposed < EXPOSURE_SRM_MIN_EXPOSED:
            return None
        df = len(assigned) - 1
        if df < 1 or df > 9:
            return None
        chi2 = 0.0
        for vk, n_assigned in assigned.items():
            expected = total_exposed * n_assigned / total_assigned
            if expected <= 0:
                continue
            chi2 += (counts.get(vk, 0) - expected) ** 2 / expected
        if chi2 < _CHI2_CRIT_P001[df]:
            return None
        recent = (
            await self.db.execute(
                select(GuardrailEvent)
                .where(
                    GuardrailEvent.experiment_id == exp.id,
                    GuardrailEvent.guardrail_key == EXPOSURE_SRM_WINDOW_GUARDRAIL_KEY,
                    GuardrailEvent.created_at
                    >= datetime.now(UTC) - timedelta(hours=_SRM_REALERT_HOURS),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        detail = {
            "chi2": round(chi2, 3),
            "df": df,
            "counts": counts,
            "total_exposed": total_exposed,
            "window_hours": SRM_WINDOW_HOURS,
        }
        if recent is None:
            self.db.add(
                GuardrailEvent(
                    experiment_id=exp.id,
                    guardrail_key=EXPOSURE_SRM_WINDOW_GUARDRAIL_KEY,
                    action="alerted",
                    auto=True,
                    detail=detail,
                )
            )
            log.warning(
                "experiment_exposure_srm_window_alert", experiment_id=exp.id, **detail
            )
            if notify:
                await self._notify_alert(
                    exp,
                    title=f"Windowed exposure-SRM alert on '{exp.title}'",
                    detail=detail,
                )
        return detail

    async def check_srm_window(
        self, exp: Experiment, spec: ExperimentSpec, *, notify: bool = True
    ) -> dict | None:
        """Defect #90: chi-square over ONLY the last SRM_WINDOW_HOURS of
        assignments. A late randomization break (post-ramp misconfig,
        differential dropout) is diluted by the healthy cumulative mass —
        the cumulative test stays under the p<0.001 bar for days while the
        recent slice is flagrant. Alert-only, 24h-suppressed, own key."""
        if spec.design == "switchback":
            return None  # defect #28: the design randomizes TIME, not units
        window_start = datetime.now(UTC) - timedelta(hours=SRM_WINDOW_HOURS)
        counts_q = (
            select(ExperimentAssignment.variant_key, ExperimentAssignment.id)
            .where(
                ExperimentAssignment.experiment_id == exp.id,
                ExperimentAssignment.is_holdout.is_(False),
                ExperimentAssignment.assigned_at >= window_start,
            )
        )
        counts: dict[str, int] = {}
        for variant_key, _id in (await self.db.execute(counts_q)).all():
            counts[variant_key] = counts.get(variant_key, 0) + 1
        counts = {**{v.key: 0 for v in spec.variants}, **counts}
        total = sum(counts.values())
        if total < SRM_WINDOW_MIN_ASSIGNMENTS:
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
        recent = (
            await self.db.execute(
                select(GuardrailEvent)
                .where(
                    GuardrailEvent.experiment_id == exp.id,
                    GuardrailEvent.guardrail_key == SRM_WINDOW_GUARDRAIL_KEY,
                    GuardrailEvent.created_at
                    >= datetime.now(UTC) - timedelta(hours=_SRM_REALERT_HOURS),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        detail = {
            "chi2": round(chi2, 3),
            "df": df,
            "counts": counts,
            "total": total,
            "window_hours": SRM_WINDOW_HOURS,
        }
        if recent is None:
            self.db.add(
                GuardrailEvent(
                    experiment_id=exp.id,
                    guardrail_key=SRM_WINDOW_GUARDRAIL_KEY,
                    action="alerted",
                    auto=True,
                    detail=detail,
                )
            )
            log.warning("experiment_srm_window_alert", experiment_id=exp.id, **detail)
            if notify:
                # When cumulative SRM already paged this cycle, the window
                # finding is the same underlying break — event, no second page
                await self._notify_alert(
                    exp, title=f"Windowed SRM alert on '{exp.title}'", detail=detail
                )
        return detail

    async def check_exposure_srm(self, exp: Experiment) -> dict | None:
        """§4.13 v2 (trigger-bias detection): per-variant EXPOSED-unit counts
        must track assignment proportions — a divergence means the exposure
        decision itself is affected by the treatment, which poisons any
        exposed-only (triggered) analysis. Alert-only, 24h-suppressed."""
        spec = await self._spec(exp)
        if spec is not None and spec.design == "switchback":
            return None  # same reason as check_srm (defect #28)
        from app.experiments.services.assignment import AssignmentService

        stats = await AssignmentService(self.db).exposure_stats(exp.id)
        funnel = stats.get("funnel", {})
        total_assigned = sum(v["assigned"] for v in funnel.values())
        total_exposed = sum(v["exposed_units"] for v in funnel.values())
        if total_exposed < EXPOSURE_SRM_MIN_EXPOSED or total_assigned <= 0:
            return None
        df = len(funnel) - 1
        if df < 1 or df > 9:
            return None
        chi2 = 0.0
        for row in funnel.values():
            expected = total_exposed * row["assigned"] / total_assigned
            if expected <= 0:
                continue
            chi2 += (row["exposed_units"] - expected) ** 2 / expected
        if chi2 < _CHI2_CRIT_P001[df]:
            return None
        recent = (
            await self.db.execute(
                select(GuardrailEvent)
                .where(
                    GuardrailEvent.experiment_id == exp.id,
                    GuardrailEvent.guardrail_key == EXPOSURE_SRM_GUARDRAIL_KEY,
                    GuardrailEvent.created_at
                    >= datetime.now(UTC) - timedelta(hours=_SRM_REALERT_HOURS),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        detail = {
            "chi2": round(chi2, 3),
            "df": df,
            "funnel": {k: dict(v) for k, v in funnel.items()},
            "total_exposed": total_exposed,
        }
        if recent is None:
            self.db.add(
                GuardrailEvent(
                    experiment_id=exp.id,
                    guardrail_key=EXPOSURE_SRM_GUARDRAIL_KEY,
                    action="alerted",
                    auto=True,
                    detail=detail,
                )
            )
            log.warning("experiment_exposure_srm_alert", experiment_id=exp.id, **detail)
            await self._notify_alert(
                exp, title=f"Exposure-SRM alert on '{exp.title}'", detail=detail
            )
        return detail

    # ── Guardrail metrics ────────────────────────────────────────────

    @staticmethod
    def _observed(definition: MetricDefinition, combined: dict) -> float | None:
        """Collapse combined sufficient stats into the guarded scalar.
        binary/rate → numerator/denominator; continuous → sum or mean
        (definition.spec.guardrail_aggregate overrides; cost is a sum).
        A non-finite result (fuzz-found: a denormal denominator overflows the
        division to inf, which then crashes the Numeric write on the
        GuardrailEvent) is treated like the denominator-0 case: not
        evaluable → None."""
        import math

        aggregate = definition.spec.get("guardrail_aggregate")
        if aggregate is None:
            aggregate = "rate" if definition.kind in ("binary", "rate") else "mean"
        if isinstance(aggregate, str) and re.fullmatch(r"p\d{1,2}(\.\d+)?", aggregate):
            # §4.14: percentile guardrail (p95 latency, say) — needs the
            # value_histogram the quantiles knob makes the source emit;
            # no sketch in the window means not evaluable (skip, not crash)
            from app.experiments.services.analysis import histogram_quantile

            out = histogram_quantile(
                combined.get("value_histogram") or {}, float(aggregate[1:]) / 100.0
            )
            return out["estimate"] if out is not None else None
        if aggregate == "rate":
            denominator = combined.get("denominator") or 0
            if not denominator:
                return None
            observed = float(combined.get("numerator") or 0) / float(denominator)
        elif aggregate == "sum":
            observed = float(combined.get("sum_value") or combined.get("numerator") or 0)
        else:  # mean
            n = combined.get("n") or 0
            if not n:
                return None
            observed = float(combined.get("sum_value") or 0) / float(n)
        return observed if math.isfinite(observed) else None

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
        try:
            spec = await self._spec(exp)
        except Exception:  # noqa: BLE001 — poison-spec resilience
            # An unparseable spec means guardrails CANNOT be evaluated — a
            # running experiment without working guardrails is unsafe, so
            # pause it (never leave it silently unguarded while the handler
            # dead-letters and retries forever).
            log.error("experiment_spec_unparseable", experiment_id=experiment_id)
            self.db.add(
                GuardrailEvent(
                    experiment_id=experiment_id,
                    guardrail_key="__spec_invalid__",
                    action="paused",
                    auto=True,
                    detail={"reason": "spec failed to parse — guardrails cannot run"},
                )
            )
            from app.experiments.services.experiments import ExperimentService

            await ExperimentService(self.db).transition(
                experiment_id,
                to_status="paused",
                actor=_system_actor(),
                reason="spec unparseable — guardrails cannot run",
            )
            exp.last_guardrail_check_at = now
            await self.db.flush()
            summary["breaches"] = [{"metric_key": "__spec_invalid__"}]
            return summary
        if spec is None:
            # #84 (round 333): a RUNNING experiment with no current_version
            # row is the poison-spec case in different clothes — unguarded
            # while running, and (unstamped) squatting a fairness-cap slot at
            # the head of every sweep. Same safety law: pause + stamp.
            log.error("experiment_version_row_missing", experiment_id=experiment_id)
            self.db.add(
                GuardrailEvent(
                    experiment_id=experiment_id,
                    guardrail_key="__spec_missing__",
                    action="paused",
                    auto=True,
                    detail={"reason": "current_version row missing — guardrails cannot run"},
                )
            )
            from app.experiments.services.experiments import ExperimentService

            await ExperimentService(self.db).transition(
                experiment_id,
                to_status="paused",
                actor=_system_actor(),
                reason="version row missing — guardrails cannot run",
            )
            exp.last_guardrail_check_at = now
            await self.db.flush()
            summary["breaches"] = [{"metric_key": "__spec_missing__"}]
            return summary

        srm = await self.check_srm(exp, spec)
        if srm is not None:
            summary["srm"] = srm
        srm_window = await self.check_srm_window(exp, spec, notify=srm is None)
        if srm_window is not None:
            summary["srm_window"] = srm_window
        exposure_srm = await self.check_exposure_srm(exp)
        if exposure_srm is not None:
            summary["exposure_srm"] = exposure_srm
        exposure_srm_window = await self.check_exposure_srm_window(
            exp, notify=exposure_srm is None
        )
        if exposure_srm_window is not None:
            summary["exposure_srm_window"] = exposure_srm_window

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
                    if v is None:
                        continue
                    # #65: a quantiles-enabled definition emits the exp13
                    # value_histogram dict — histograms fold as histograms
                    # (scalar + dict was a TypeError that killed the sweep)
                    if isinstance(v, dict):
                        hacc = combined.setdefault(k, {})
                        for bucket, count in v.items():
                            hacc[bucket] = hacc.get(bucket, 0) + count
                    else:
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
                    detail={"op": guardrail.op, "combined": {
                        k: (v if isinstance(v, dict) else float(v))
                        for k, v in combined.items()
                    }},
                )
                self.db.add(event)
                breaches.append(event)
                summary["breaches"].append(
                    {"metric_key": guardrail.metric_key, "observed": observed,
                     "threshold": guardrail.threshold}
                )

        if breaches:
            # §4.18: breach detail to tenant webhooks before the pause (the
            # pause itself also emits status_changed through transition)
            from app.experiments.services.webhook_events import emit_experiment_event

            await emit_experiment_event(
                self.db,
                scope_org_id=exp.scope_org_id,
                event_type="experiment.guardrail_breach",
                payload={
                    "experiment_id": experiment_id,
                    "experiment_key": exp.key,
                    "breaches": summary["breaches"],
                    "action": "paused",
                },
            )
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
            # Owner notification (Part D) — fail-safe: a notification hiccup
            # must never fail the pause it describes (the eco_audit posture)
            try:
                from app.services.notification import NotificationService

                # Defect #42: without the SAVEPOINT a failed notification
                # flush poisoned the session, the pause write itself was then
                # lost at handler commit, and the breached experiment KEPT
                # RUNNING while arq retried into the same wall forever.
                async with self.db.begin_nested():
                    await NotificationService(self.db).create(
                        user_id=exp.owner_user_id,
                        notification_type="experiment_guardrail",
                        title=f"Experiment '{exp.title}' auto-paused by guardrail",
                        body=(
                            f"{summary['breaches'][0]['metric_key']} breached its "
                            "threshold — review the guardrail dashboard."
                        ),
                        data={"experiment_id": experiment_id,
                              "breaches": summary["breaches"]},
                    )
            except Exception:  # noqa: BLE001 — additive, never blocking
                log.warning("experiment_pause_notify_failed", experiment_id=experiment_id)
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
