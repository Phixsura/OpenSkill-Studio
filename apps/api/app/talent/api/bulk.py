"""Bulk operations API — batch create/transition up to 100 items (ADR-015 D4A).

Partial success: each item is processed independently so a single failure
does not roll back the successful siblings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.models.application import (
    APPLICATION_TRANSITIONS,
    Application,
    ApplicationEvent,
)
from app.talent.models.employer import Opportunity
from app.talent.schemas.bulk import (
    BulkCapabilityRequest,
    BulkCapabilityResult,
    BulkError,
    BulkEvidenceRequest,
    BulkEvidenceResult,
    BulkTransitionRequest,
    BulkTransitionResult,
    TransitionResult,
)
from app.talent.schemas.capability import CapabilityResponse
from app.talent.schemas.evidence import EvidenceResponse

MAX_BATCH_SIZE = 500

router = APIRouter(prefix="/talent", tags=["Talent — Bulk Operations"])

# Transitions that only the candidate (applicant) may perform
_CANDIDATE_TRANSITIONS = frozenset({"withdrawn", "accepted"})
# Transitions that only the employer may perform
_EMPLOYER_TRANSITIONS = frozenset(
    {"screening", "interview", "assessment", "offer", "rejected", "hired", "completed"}
)


# ---------------------------------------------------------------------------
# POST /talent/capabilities/bulk
# ---------------------------------------------------------------------------


@router.post(
    "/capabilities/bulk",
    response_model=DataResponse[BulkCapabilityResult],
    status_code=200,
    summary="Bulk Create Capabilities",
)
async def bulk_create_capabilities(
    body: BulkCapabilityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create up to 100 capabilities in one request (partial success)."""
    from app.talent.services.capability import CapabilityService

    svc = CapabilityService(db)
    result = BulkCapabilityResult()

    for idx, item in enumerate(body.items):
        try:
            cap = await svc.create_capability(
                canonical_name=item.canonical_name,
                category=item.category,
                description=item.description,
                parent_id=item.parent_id,
                capability_tag_id=item.capability_tag_id,
                level_definitions=item.level_definitions,
                decay_config=item.decay_config,
                sort_order=item.sort_order,
                external_ids=item.external_ids,
                aliases=item.aliases,
                translations=item.translations,
            )
            await db.flush()
            result.created.append(CapabilityResponse.model_validate(cap))
        except Exception as exc:
            result.errors.append(BulkError(index=idx, error=str(exc)))

    if result.created:
        await db.commit()
        # Refresh to populate server_default timestamps
        for i, cap_resp in enumerate(result.created):
            obj = await db.get(
                __import__("app.talent.models.capability", fromlist=["Capability"]).Capability,
                cap_resp.id,
            )
            if obj:
                await db.refresh(obj)
                result.created[i] = CapabilityResponse.model_validate(obj)

    return DataResponse(data=result)


# ---------------------------------------------------------------------------
# POST /talent/evidence/bulk
# ---------------------------------------------------------------------------


@router.post(
    "/evidence/bulk",
    response_model=DataResponse[BulkEvidenceResult],
    status_code=200,
    summary="Bulk Record Evidence",
)
async def bulk_record_evidence(
    body: BulkEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record up to 100 evidence items in one request (partial success)."""
    from app.talent.services.evidence import EvidenceService

    svc = EvidenceService(db)
    result = BulkEvidenceResult()

    for idx, item in enumerate(body.items):
        try:
            ev = await svc.record_evidence(
                user_id=user.id,
                capability_id=item.capability_id,
                source_type=item.source_type,
                source_id=item.source_id,
                verification_level=item.verification_level,
                occurred_at=item.occurred_at,
                org_id=item.org_id,
                score_normalized=item.score_normalized,
                confidence=item.confidence,
                expires_at=item.expires_at,
                metadata=item.metadata,
            )
            await db.flush()
            result.created.append(EvidenceResponse.model_validate(ev))
        except Exception as exc:
            result.errors.append(BulkError(index=idx, error=str(exc)))

    if result.created:
        await db.commit()
        # Refresh for server_default timestamps
        from app.talent.models.evidence import CapabilityEvidence

        for i, ev_resp in enumerate(result.created):
            obj = await db.get(CapabilityEvidence, ev_resp.id)
            if obj:
                await db.refresh(obj)
                result.created[i] = EvidenceResponse.model_validate(obj)

    return DataResponse(data=result)


# ---------------------------------------------------------------------------
# POST /talent/applications/bulk-transition
# ---------------------------------------------------------------------------


@router.post(
    "/applications/bulk-transition",
    response_model=DataResponse[BulkTransitionResult],
    status_code=200,
    summary="Bulk Transition Applications",
)
async def bulk_transition_applications(
    body: BulkTransitionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Transition up to 50 applications in one request (partial success).

    Each transition is validated independently against the state machine
    and authorization rules.
    """
    result = BulkTransitionResult()

    for idx, item in enumerate(body.transitions):
        try:
            app = await db.get(Application, item.application_id)
            if not app:
                result.errors.append(BulkError(index=idx, error="Application not found"))
                continue

            # State machine check
            allowed = APPLICATION_TRANSITIONS.get(app.status, [])
            if item.status not in allowed:
                result.errors.append(
                    BulkError(
                        index=idx,
                        error=(
                            f"Cannot transition from '{app.status}' to "
                            f"'{item.status}'. Allowed: {allowed}"
                        ),
                    )
                )
                continue

            # Authorization
            if item.status in _CANDIDATE_TRANSITIONS:
                if app.user_id != user.id:
                    result.errors.append(BulkError(index=idx, error="Application not found"))
                    continue
            elif item.status in _EMPLOYER_TRANSITIONS:
                opp = await db.get(Opportunity, app.opportunity_id)
                if not opp:
                    result.errors.append(BulkError(index=idx, error="Opportunity not found"))
                    continue
                try:
                    await require_org_member(opp.employer_org_id, user, db)
                except HTTPException:
                    result.errors.append(
                        BulkError(index=idx, error="Not authorized for this transition")
                    )
                    continue
            else:
                # submitted — must be applicant
                if app.user_id != user.id:
                    result.errors.append(BulkError(index=idx, error="Application not found"))
                    continue

            old_status = app.status
            app.status = item.status

            event = ApplicationEvent(
                application_id=app.id,
                from_status=old_status,
                to_status=item.status,
                acted_by=user.id,
                note=item.note,
            )
            db.add(event)

            result.transitioned.append(
                TransitionResult(
                    application_id=app.id,
                    from_status=old_status,
                    to_status=item.status,
                )
            )

        except Exception as exc:
            result.errors.append(BulkError(index=idx, error=str(exc)))

    if result.transitioned:
        await db.commit()

    return DataResponse(data=result)
