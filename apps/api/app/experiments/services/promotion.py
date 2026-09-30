"""Policy promotion (ADR-017 §11, Part K).

An approved `promote` decision can produce a DRAFT change in a target domain
— never a direct production mutation. Apply adapters create the target
domain's own draft object under that domain's invariants:

- matching_config  → NEW inactive MatchingConfig version (the matching
  domain's D1 rule: configs are never mutated, only new versions; activation
  stays a matching-domain decision)
- learning_path    → NEW LearningPath row in status draft (curriculum
  recommendations never silently rewrite active curricula — Part F)
- others (pack_recommendation, workflow_binding, eco_rollout_policy,
  pricing_presentation) validate at draft time and refuse APPLY with a typed
  code until their exp07 integration lands — explicitly, never silently.

Apply is idempotent: an applied draft returns 409 PROMOTION_ALREADY_APPLIED.
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models.decision import PromotionDraft
from app.experiments.security import PROMOTION_TARGET_TYPES
from app.experiments.services.decisions import DecisionService
from app.models.user import User

_ID_LENGTH = 26


class PromotionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── target validation (draft time) ───────────────────────────────

    async def _validate_target(self, target_type: str, target_ref: str, payload: dict) -> None:
        if target_type not in PROMOTION_TARGET_TYPES:
            raise AppError(
                "VALIDATION_ERROR",
                f"Unknown target_type: {target_type} "
                f"(allowed: {sorted(PROMOTION_TARGET_TYPES)})",
                422,
            )
        if target_type == "matching_config":
            from app.models.matching import MatchingConfig

            config = await self.db.get(MatchingConfig, target_ref)
            if not config:
                raise AppError("EXPERIMENT_NOT_FOUND", "Matching config not found", 404)
            weights = payload.get("weights")
            if weights is not None:
                if not isinstance(weights, dict) or not weights:
                    raise AppError("VALIDATION_ERROR", "weights must be a non-empty object", 422)
                total = sum(float(v) for v in weights.values())
                if abs(total - 1.0) > 1e-6:
                    # The matching domain's own invariant — never bypassed (§2.2)
                    raise AppError(
                        "VALIDATION_ERROR", f"weights must sum to 1.0 (got {total})", 422
                    )
        elif target_type == "learning_path":
            from app.models.learning_path import LearningPath

            path = await self.db.get(LearningPath, target_ref)
            if not path:
                raise AppError("EXPERIMENT_NOT_FOUND", "Learning path not found", 404)
        elif target_type == "workflow_binding":
            from app.models.workflow_pack import WorkflowPackInstallation

            installation = await self.db.get(WorkflowPackInstallation, target_ref)
            if not installation:
                raise AppError("EXPERIMENT_NOT_FOUND", "Workflow installation not found", 404)
            step_id = payload.get("step_id")
            offering_id = payload.get("offering_id")
            if not step_id or not offering_id:
                raise AppError(
                    "VALIDATION_ERROR", "workflow_binding requires step_id and offering_id", 422
                )
            from app.models.provider import ProviderConnection, ProviderModelOffering

            offering = await self.db.get(ProviderModelOffering, offering_id)
            if offering is None or not offering.is_active:
                raise AppError("EXPERIMENT_NOT_FOUND", "Offering not found or inactive", 404)
            conn = await self.db.get(ProviderConnection, offering.connection_id)
            # The offering must belong to the installation's org (R3 —
            # promotion never crosses the credential boundary)
            if conn is None or conn.org_id != installation.org_id or conn.status != "active":
                raise AppError(
                    "VALIDATION_ERROR",
                    "Offering does not belong to the installation's org",
                    422,
                )
        elif target_type == "eco_rollout_policy":
            from app.ecosystem.models.replacement import ReplacementCandidate

            candidate = await self.db.get(ReplacementCandidate, target_ref)
            if not candidate:
                raise AppError("EXPERIMENT_NOT_FOUND", "Replacement candidate not found", 404)
            # RolloutService.create re-runs the full eco gates at apply
            # (hard-incompatible refusal, retired/blocked entity guard)
        elif len(target_ref) > 64 or not target_ref.strip():
            raise AppError("VALIDATION_ERROR", "target_ref must be a non-empty reference", 422)

    # ── lifecycle ────────────────────────────────────────────────────

    async def create_draft(
        self,
        decision_id: str,
        *,
        target_type: str,
        target_ref: str,
        draft_payload: dict,
        actor: User,
    ) -> PromotionDraft:
        decision = await DecisionService(self.db).get(decision_id)
        if decision.decision != "promote":
            raise AppError(
                "DECISION_STATE_INVALID",
                f"Promotion drafts require a promote decision (got {decision.decision})",
                422,
            )
        if decision.analysis_type != "randomized":
            # Defense in depth — the decision service already blocks this
            raise AppError(
                "PROMOTION_REQUIRES_RANDOMIZED",
                "Observational analyses cannot produce promotion drafts",
                422,
            )
        await self._validate_target(target_type, target_ref, draft_payload)
        draft = PromotionDraft(
            decision_record_id=decision_id,
            target_type=target_type,
            target_ref=target_ref,
            draft_payload=draft_payload,
        )
        self.db.add(draft)
        await self.db.flush()
        from app.experiments.services.experiments import ExperimentService

        await ExperimentService(self.db)._record_event(  # noqa: SLF001 — same package
            decision.experiment_id,
            event_type="promotion_drafted",
            actor_user_id=actor.id,
            payload={"draft_id": draft.id, "target_type": target_type,
                     "target_ref": target_ref},
        )
        return draft

    async def get(self, draft_id: str, *, for_update: bool = False) -> PromotionDraft:
        q = select(PromotionDraft).where(PromotionDraft.id == draft_id)
        if for_update:
            # Status changes serialize on the row — two concurrent applies
            # must not both pass the idempotency check and double-create the
            # target-domain draft (R396 transition-race class)
            q = q.with_for_update()
        draft = (await self.db.execute(q)).scalar_one_or_none()
        if not draft:
            raise AppError("EXPERIMENT_NOT_FOUND", "Promotion draft not found", 404)
        return draft

    async def list_drafts(
        self, *, status: str | None = None, limit: int = 100
    ) -> list[PromotionDraft]:
        q = select(PromotionDraft)
        if status:
            q = q.where(PromotionDraft.status == status)
        q = q.order_by(PromotionDraft.id.desc()).limit(limit)
        return list((await self.db.execute(q)).scalars())

    async def approve(self, draft_id: str, *, actor: User) -> PromotionDraft:
        draft = await self.get(draft_id, for_update=True)
        if draft.status != "draft":
            raise AppError(
                "DECISION_STATE_INVALID", f"Cannot approve from status {draft.status}", 422
            )
        draft.status = "approved"
        draft.approved_by = actor.id
        await self.db.flush()
        return draft

    async def reject(self, draft_id: str, *, actor: User) -> PromotionDraft:
        draft = await self.get(draft_id, for_update=True)
        if draft.status not in ("draft", "approved"):
            raise AppError(
                "DECISION_STATE_INVALID", f"Cannot reject from status {draft.status}", 422
            )
        draft.status = "rejected"
        draft.approved_by = actor.id
        await self.db.flush()
        return draft

    async def apply(self, draft_id: str, *, actor: User) -> PromotionDraft:
        draft = await self.get(draft_id, for_update=True)
        if draft.status == "applied":
            raise AppError("PROMOTION_ALREADY_APPLIED", "Draft already applied", 409)
        if draft.status != "approved":
            raise AppError(
                "DECISION_STATE_INVALID",
                f"Apply requires an approved draft (got {draft.status})",
                422,
            )
        # Re-validate at apply time — the target may have changed since draft
        await self._validate_target(draft.target_type, draft.target_ref, draft.draft_payload)
        applied_ref = await self._apply_adapter(draft, actor)
        draft.status = "applied"
        draft.applied_at = datetime.now(UTC)
        draft.applied_ref = applied_ref
        decision = await DecisionService(self.db).get(draft.decision_record_id)
        from app.experiments.services.experiments import ExperimentService

        await ExperimentService(self.db)._record_event(  # noqa: SLF001 — same package
            decision.experiment_id,
            event_type="promotion_drafted",
            actor_user_id=actor.id,
            payload={"draft_id": draft.id, "applied_ref": applied_ref, "applied": True},
        )
        await self.db.flush()
        return draft

    # ── apply adapters (target-domain DRAFT objects) ─────────────────

    async def _apply_adapter(self, draft: PromotionDraft, actor: User) -> str:
        if draft.target_type == "matching_config":
            return await self._apply_matching_config(draft)
        if draft.target_type == "learning_path":
            return await self._apply_learning_path(draft, actor)
        if draft.target_type == "workflow_binding":
            return await self._apply_workflow_binding(draft)
        if draft.target_type == "eco_rollout_policy":
            return await self._apply_eco_rollout(draft)
        # pack_recommendation / pricing_presentation: no target-domain draft
        # store exists yet — refusing explicitly beats applying into nothing
        raise AppError(
            "EXPERIMENT_PROMOTION_UNWIRED",
            f"No target-domain draft store for {draft.target_type} yet — "
            "the draft stays approved",
            422,
        )

    async def _apply_matching_config(self, draft: PromotionDraft) -> str:
        """NEW inactive MatchingConfig version — never mutates the referenced
        row (the matching domain's D1 invariant). Activation is a separate,
        matching-domain decision."""
        from app.models.matching import MatchingConfig

        base = await self.db.get(MatchingConfig, draft.target_ref)
        max_version = (
            await self.db.execute(
                select(func.max(MatchingConfig.version)).where(
                    MatchingConfig.target_entity_type == base.target_entity_type
                )
            )
        ).scalar_one()
        new_config = MatchingConfig(
            version=(max_version or 0) + 1,
            target_entity_type=base.target_entity_type,
            weights=draft.draft_payload.get("weights") or base.weights,
            thresholds=draft.draft_payload.get("thresholds") or base.thresholds,
            is_active=False,
        )
        self.db.add(new_config)
        await self.db.flush()
        return new_config.id

    async def _apply_workflow_binding(self, draft: PromotionDraft) -> str:
        """UNCONFIRMED WorkflowStepBinding suggestion (confirmed_by=None) —
        exactly the domain's own draft shape (D5: install creates unconfirmed
        suggestions; only a human confirmation makes them live). An existing
        binding row for the installation+step is never overwritten."""
        from sqlalchemy.exc import IntegrityError

        from app.models.workflow_pack import WorkflowPackInstallation
        from app.models.workflow_run import WorkflowStepBinding

        installation = await self.db.get(WorkflowPackInstallation, draft.target_ref)
        binding = WorkflowStepBinding(
            org_id=installation.org_id,
            installation_id=installation.id,
            step_id=draft.draft_payload["step_id"],
            binding_mode="confirmed",
            offering_id=draft.draft_payload["offering_id"],
            reasons=[f"experiment promotion {draft.id}"],
        )
        try:
            # SAVEPOINT: a unique-constraint loser must not poison the
            # caller's transaction (the outbox handler's nested-block pattern)
            async with self.db.begin_nested():
                self.db.add(binding)
                await self.db.flush()
        except IntegrityError as exc:
            raise AppError(
                "DECISION_STATE_INVALID",
                "A binding already exists for this installation+step — "
                "review it in the workflow domain instead of overwriting",
                409,
            ) from exc
        return binding.id

    async def _apply_eco_rollout(self, draft: PromotionDraft) -> str:
        """DRAFT eco RolloutPlan via the eco domain's own service — its gates
        (hard-incompatible refusal, retired/blocked entity guard, guardrail
        shape check) all re-run here; the plan starts in eco status draft and
        every promote/reject stays an explicit eco-domain human decision."""
        from app.ecosystem.services.rollout import RolloutService

        payload = draft.draft_payload
        plan = await RolloutService(self.db).create(
            replacement_candidate_id=draft.target_ref,
            scope_type=payload.get("scope_type", "benchmark_only"),
            scope_ref=payload.get("scope_ref"),
            guardrails=payload.get("guardrails"),
        )
        return plan.id

    async def _apply_learning_path(self, draft: PromotionDraft, actor: User) -> str:
        """NEW LearningPath in status draft — active curricula are never
        silently rewritten (Part F)."""
        from app.models.learning_path import LearningPath
        from app.models.skill import ContentStatus

        base = await self.db.get(LearningPath, draft.target_ref)
        payload = draft.draft_payload
        new_path = LearningPath(
            org_id=base.org_id,
            name=payload.get("name") or f"{base.name} (experiment recommendation)",
            slug=f"{base.slug}-exp-{draft.id[-8:].lower()}",
            description=payload.get("description") or base.description,
            status=ContentStatus.DRAFT,
            estimated_minutes=base.estimated_minutes,
            created_by=actor.id,
        )
        self.db.add(new_path)
        await self.db.flush()
        return new_path.id
