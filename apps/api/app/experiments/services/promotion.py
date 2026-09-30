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

    async def get(self, draft_id: str) -> PromotionDraft:
        draft = await self.db.get(PromotionDraft, draft_id)
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
        draft = await self.get(draft_id)
        if draft.status != "draft":
            raise AppError(
                "DECISION_STATE_INVALID", f"Cannot approve from status {draft.status}", 422
            )
        draft.status = "approved"
        draft.approved_by = actor.id
        await self.db.flush()
        return draft

    async def reject(self, draft_id: str, *, actor: User) -> PromotionDraft:
        draft = await self.get(draft_id)
        if draft.status not in ("draft", "approved"):
            raise AppError(
                "DECISION_STATE_INVALID", f"Cannot reject from status {draft.status}", 422
            )
        draft.status = "rejected"
        draft.approved_by = actor.id
        await self.db.flush()
        return draft

    async def apply(self, draft_id: str, *, actor: User) -> PromotionDraft:
        draft = await self.get(draft_id)
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
        raise AppError(
            "EXPERIMENT_PROMOTION_UNWIRED",
            f"Apply adapter for {draft.target_type} lands with its domain "
            "integration (exp07) — the draft stays approved",
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
