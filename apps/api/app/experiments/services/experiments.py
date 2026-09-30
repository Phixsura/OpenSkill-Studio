"""Experiment lifecycle service (ADR-017 §5).

Table-driven state machine; transitions serialize under SELECT ... FOR UPDATE
on the experiment row (racing transitions must not both win — the R396
lesson). Specs are immutable: new versions only in draft/review; while live
only ramp_bp (monotonic increase) and an earlier ended_at may change.
"""

import hashlib
import json
from datetime import UTC, datetime, timedelta

import pydantic
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentEvent,
    ExperimentLayer,
    ExperimentLayerAllocation,
    ExperimentVersion,
)
from app.experiments.schemas import ExperimentSpec
from app.experiments.security import (
    EXPERIMENT_DOMAINS,
    RISK_CLASSES,
    check_bandit_gate,
    check_targeting_field,
)
from app.models.user import User, UserRole

# ADR-017 §5: any non-terminal status may archive; running must pause or
# complete before archiving is NOT required by the ADR (archived from any
# non-terminal), but promoted/rejected/archived are terminal.
_ALLOWED: dict[str, frozenset[str]] = {
    "draft": frozenset({"review", "archived"}),
    "review": frozenset({"draft", "scheduled", "archived"}),
    "scheduled": frozenset({"running", "archived"}),
    "running": frozenset({"paused", "completed", "archived"}),
    "paused": frozenset({"running", "completed", "archived"}),
    "completed": frozenset({"analyzed", "archived"}),
    "analyzed": frozenset({"promoted", "rejected", "archived"}),
    "promoted": frozenset(),
    "rejected": frozenset(),
    "archived": frozenset(),
}

# Guardrails are mandatory to schedule except low-risk presentation domains
_GUARDRAIL_EXEMPT_DOMAINS = frozenset({"marketplace", "operational"})

ANALYSIS_CLOSE_DEFAULT_DAYS = 90


def canonical_spec_hash(spec: dict) -> str:
    """SHA-256 over canonical JSON — sorted keys, compact separators."""
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ExperimentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── helpers ──────────────────────────────────────────────────────

    async def _record_event(
        self,
        experiment_id: str,
        *,
        event_type: str,
        actor_user_id: str | None,
        payload: dict | None = None,
    ) -> None:
        self.db.add(
            ExperimentEvent(
                experiment_id=experiment_id,
                actor_user_id=actor_user_id,
                event_type=event_type,
                payload=payload or {},
            )
        )

    async def get_scoped(
        self, experiment_id: str, scope_org_ids: list[str] | None
    ) -> Experiment:
        """Uniform 404 outside the caller's read scope (R89 — an org admin
        must not be able to probe platform experiments' existence)."""
        exp = await self.get(experiment_id)
        if scope_org_ids is not None and exp.scope_org_id not in scope_org_ids:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        return exp

    async def get(self, experiment_id: str) -> Experiment:
        exp = await self.db.get(Experiment, experiment_id)
        if not exp:
            # Uniform 404 — no existence oracle across tenants (R89 class 2)
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        return exp

    async def _get_locked(self, experiment_id: str) -> Experiment:
        row = (
            await self.db.execute(
                select(Experiment).where(Experiment.id == experiment_id).with_for_update()
            )
        ).scalar_one_or_none()
        if not row:
            raise AppError("EXPERIMENT_NOT_FOUND", "Experiment not found", 404)
        return row

    # ── create / read ────────────────────────────────────────────────

    async def create(
        self,
        *,
        key: str,
        title: str,
        domain: str,
        layer_key: str,
        owner_user_id: str,
        scope_org_id: str | None = None,
        risk_class: str = "medium",
        holdout_bp: int = 0,
    ) -> Experiment:
        if domain not in EXPERIMENT_DOMAINS:
            raise AppError(
                "VALIDATION_ERROR",
                f"Unknown domain: {domain} (allowed: {sorted(EXPERIMENT_DOMAINS)})",
                422,
            )
        if risk_class not in RISK_CLASSES:
            raise AppError("VALIDATION_ERROR", f"Unknown risk_class: {risk_class}", 422)
        if scope_org_id is not None:
            # Validate the org up front — otherwise the FK violation at flush
            # is swallowed by the IntegrityError→EXPERIMENT_KEY_TAKEN mapping
            # below and misreports a missing org as a key conflict
            from app.models.organization import Organization

            if await self.db.get(Organization, scope_org_id) is None:
                raise AppError("EXPERIMENT_NOT_FOUND", "Organization not found", 404)
        layer = (
            await self.db.execute(select(ExperimentLayer).where(ExperimentLayer.key == layer_key))
        ).scalar_one_or_none()
        if not layer:
            raise AppError("EXPERIMENT_NOT_FOUND", "Layer not found", 404)
        if layer.domain != domain:
            raise AppError(
                "VALIDATION_ERROR",
                f"Layer {layer_key} belongs to domain {layer.domain}, not {domain}",
                422,
            )
        exp = Experiment(
            key=key,
            title=title,
            domain=domain,
            layer_key=layer_key,
            owner_user_id=owner_user_id,
            scope_org_id=scope_org_id,
            risk_class=risk_class,
            holdout_bp=holdout_bp,
        )
        self.db.add(exp)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise AppError("EXPERIMENT_KEY_TAKEN", f"Experiment key taken: {key}", 409) from exc
        # A surface hook may have negative-cached this key as absent —
        # invalidate so the new experiment takes effect immediately here
        from app.experiments.services.assignment import forget_missing_key

        forget_missing_key(key)
        await self._record_event(
            exp.id, event_type="created", actor_user_id=owner_user_id, payload={"key": key}
        )
        return exp

    async def list_experiments(
        self,
        *,
        status: str | None = None,
        domain: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
        scope_org_ids: list[str] | None = None,
    ) -> tuple[list[Experiment], int, str | None]:
        """Keyset pagination: newest-first strictly by ULID id (cursor
        predicate matches the sort order — the R395 lesson)."""
        base = select(Experiment)
        if status:
            base = base.where(Experiment.status == status)
        if domain:
            base = base.where(Experiment.domain == domain)
        if scope_org_ids is not None:
            # org-admin delegation (§18): only experiments scoped to the
            # caller's orgs — platform-wide experiments are NOT theirs to see
            base = base.where(Experiment.scope_org_id.in_(scope_org_ids))
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        q = base.order_by(Experiment.id.desc())
        if cursor:
            q = q.where(Experiment.id < cursor)
        rows = list((await self.db.execute(q.limit(limit))).scalars())
        next_cursor = rows[-1].id if len(rows) == limit else None
        return rows, total, next_cursor

    async def list_events(self, experiment_id: str, *, limit: int = 100) -> list[ExperimentEvent]:
        await self.get(experiment_id)
        q = (
            select(ExperimentEvent)
            .where(ExperimentEvent.experiment_id == experiment_id)
            # id tiebreak on the timestamp order (§99.8)
            .order_by(ExperimentEvent.created_at.desc(), ExperimentEvent.id.desc())
            .limit(limit)
        )
        return list((await self.db.execute(q)).scalars())

    # ── versions (immutable specs) ───────────────────────────────────

    def validate_spec(self, spec: dict, *, domain: str, risk_class: str) -> ExperimentSpec:
        # Size cap BEFORE parsing: an unbounded spec JSONB is a storage/DoS
        # surface (the R98 oversized-input class) — 64 KB is generous for any
        # legitimate design
        try:
            raw_size = len(
                json.dumps(spec, separators=(",", ":"), ensure_ascii=False, default=str)
            )
        except (TypeError, ValueError) as exc:
            raise AppError("EXPERIMENT_SPEC_INVALID", "Spec is not JSON-serializable", 422) from exc
        if raw_size > 64_000:
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", f"Spec too large ({raw_size} bytes > 64000)", 422
            )
        try:
            parsed = ExperimentSpec.model_validate(spec)
        except pydantic.ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(x) for x in first.get("loc", ()))
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", f"Invalid spec at {loc}: {first.get('msg')}", 422
            ) from exc
        # Ethics gates (typed codes, ADR-017 §2)
        for rule in [*parsed.population.rules, *parsed.population.exclusions]:
            check_targeting_field(rule.field)
        check_bandit_gate(
            domain=domain, risk_class=risk_class, allocation_mode=parsed.allocation_mode
        )
        return parsed

    async def create_version(
        self, experiment_id: str, *, spec: dict, actor: User
    ) -> ExperimentVersion:
        exp = await self._get_locked(experiment_id)
        if exp.status not in ("draft", "review"):
            raise AppError(
                "EXPERIMENT_INVALID_TRANSITION",
                f"Spec versions may only be added in draft/review (status: {exp.status})",
                422,
            )
        parsed = self.validate_spec(spec, domain=exp.domain, risk_class=exp.risk_class)
        payload = parsed.model_dump(mode="json")
        version = ExperimentVersion(
            experiment_id=exp.id,
            version=exp.current_version + 1,
            spec=payload,
            spec_hash=canonical_spec_hash(payload),
            created_by=actor.id,
        )
        self.db.add(version)
        exp.current_version = version.version
        await self.db.flush()
        await self._record_event(
            exp.id,
            event_type="version_created",
            actor_user_id=actor.id,
            payload={"version": version.version, "spec_hash": version.spec_hash},
        )
        return version

    async def get_versions(self, experiment_id: str) -> list[ExperimentVersion]:
        await self.get(experiment_id)
        q = (
            select(ExperimentVersion)
            .where(ExperimentVersion.experiment_id == experiment_id)
            .order_by(ExperimentVersion.version.desc())
        )
        return list((await self.db.execute(q)).scalars())

    # ── lifecycle ────────────────────────────────────────────────────

    def check_transition(self, from_status: str, to_status: str) -> None:
        allowed = _ALLOWED.get(from_status)
        if allowed is None or to_status not in allowed:
            raise AppError(
                "EXPERIMENT_INVALID_TRANSITION",
                f"Cannot transition {from_status} -> {to_status}",
                422,
            )

    async def _check_schedule_preconditions(
        self, exp: Experiment, actor: User, checklist: dict | None = None
    ) -> None:
        from app.experiments.security import required_checklist_keys

        # §5 v2 launch checklist: every required item affirmed to schedule
        missing = [
            key
            for key in required_checklist_keys(exp.domain)
            if not (checklist or {}).get(key)
        ]
        if missing:
            raise AppError(
                "EXPERIMENT_CHECKLIST_INCOMPLETE",
                f"Launch checklist incomplete: {', '.join(missing)}",
                422,
            )
        if exp.current_version < 1:
            raise AppError(
                "EXPERIMENT_SPEC_INVALID", "Cannot schedule without a spec version", 422
            )
        latest = (
            await self.db.execute(
                select(ExperimentVersion)
                .where(
                    ExperimentVersion.experiment_id == exp.id,
                    ExperimentVersion.version == exp.current_version,
                )
            )
        ).scalar_one()
        spec = self.validate_spec(latest.spec, domain=exp.domain, risk_class=exp.risk_class)
        needs_guardrails = not (
            exp.risk_class == "low" and exp.domain in _GUARDRAIL_EXEMPT_DOMAINS
        )
        if needs_guardrails and not spec.metrics.guardrails:
            raise AppError(
                "EXPERIMENT_NO_GUARDRAILS",
                "Experiments must declare guardrail metrics before scheduling",
                422,
            )
        if exp.risk_class == "high" and actor.role != UserRole.ADMIN:
            raise AppError(
                "FORBIDDEN", "High-risk experiments require platform-admin approval", 403
            )
        allocation = (
            await self.db.execute(
                select(ExperimentLayerAllocation).where(
                    ExperimentLayerAllocation.experiment_id == exp.id
                )
            )
        ).scalar_one_or_none()
        if not allocation:
            raise AppError(
                "EXPERIMENT_SPEC_INVALID",
                "Cannot schedule without a layer slice allocation",
                422,
            )

    async def transition(
        self,
        experiment_id: str,
        *,
        to_status: str,
        actor: User,
        reason: str | None = None,
        checklist: dict | None = None,
        _via_decision: bool = False,
    ) -> Experiment:
        exp = await self._get_locked(experiment_id)
        self.check_transition(exp.status, to_status)
        if to_status in ("promoted", "rejected") and not _via_decision:
            # §2.2 hard gate: promoted/rejected exist ONLY as the outcome of a
            # DecisionRecord (approver + verified analysis hash). The generic
            # transition surface must never mint them — otherwise the
            # decision registry is optional and the hash gate is decorative.
            raise AppError(
                "EXPERIMENT_DECISION_REQUIRED",
                f"'{to_status}' is set by recording a decision, not by direct transition",
                422,
            )
        if to_status == "scheduled":
            await self._check_schedule_preconditions(exp, actor, checklist)
        now = datetime.now(UTC)
        from_status = exp.status
        exp.status = to_status
        if to_status == "running" and exp.started_at is None:
            exp.started_at = now
        if to_status == "completed":
            exp.ended_at = exp.ended_at or now
            if exp.analysis_close_at is None:
                exp.analysis_close_at = exp.ended_at + timedelta(
                    days=ANALYSIS_CLOSE_DEFAULT_DAYS
                )
        await self._record_event(
            exp.id,
            event_type="transition",
            actor_user_id=actor.id,
            payload={
                "from": from_status,
                "to": to_status,
                "reason": reason,
                **({"checklist": checklist} if checklist else {}),
            },
        )
        await self.db.flush()
        return exp

    async def set_ramp(self, experiment_id: str, *, ramp_bp: int, actor: User) -> Experiment:
        exp = await self._get_locked(experiment_id)
        if exp.status not in ("draft", "review", "scheduled", "running"):
            raise AppError(
                "EXPERIMENT_INVALID_TRANSITION",
                f"Ramp cannot change in status {exp.status}",
                422,
            )
        # Ramp only widens eligibility — a decrease would break ITT (§6)
        if exp.status in ("scheduled", "running") and ramp_bp < exp.ramp_bp:
            raise AppError(
                "EXPERIMENT_RAMP_DECREASE",
                f"Ramp may only increase while live ({exp.ramp_bp} -> {ramp_bp})",
                422,
            )
        before = exp.ramp_bp
        exp.ramp_bp = ramp_bp
        await self._record_event(
            exp.id,
            event_type="ramp_changed",
            actor_user_id=actor.id,
            payload={"from_bp": before, "to_bp": ramp_bp},
        )
        await self.db.flush()
        return exp
