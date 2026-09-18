"""Evidence ledger API — record, query, void, provenance.

Authorization rules:
  - Self-service evidence recording: verification_level forced to self_reported
  - Higher trust levels (instructor/employer/etc.) require the facade path
    with appropriate role checks at the call site
  - Users can only view their own evidence
  - Capability profile respects passport privacy settings
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.cursor import CursorListResponse, CursorMeta
from app.talent.schemas.evidence import (
    EvidenceResponse,
    ProvenanceResponse,
    RecordEvidenceRequest,
    VoidEvidenceRequest,
)
from app.talent.services.evidence import EvidenceService
from app.talent.services.scoring import compute_capability_profile

router = APIRouter(prefix="/talent", tags=["Talent — Evidence"])


@router.get(
    "/evidence",
    response_model=CursorListResponse[EvidenceResponse],
    summary="List evidence",
    description="Returns paginated capability evidence for the authenticated user. Supports cursor-based pagination.",
)
async def list_evidence(
    capability_id: str | None = None,
    status: str = "active",
    cursor: str | None = Query(None, description="Cursor for pagination (last item ID)"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List own evidence."""
    svc = EvidenceService(db)
    items, total = await svc.get_evidence_for_user(
        user.id,
        capability_id=capability_id,
        status=status,
        limit=limit,
        cursor=cursor,
    )
    all_items = list(items) if not isinstance(items, list) else items
    has_more = len(all_items) > limit
    if has_more:
        all_items = all_items[:limit]
    next_cursor = all_items[-1].id if has_more and all_items else None
    return CursorListResponse(
        data=[EvidenceResponse.model_validate(e) for e in all_items],
        meta=CursorMeta(next_cursor=next_cursor, has_more=has_more),
    )


@router.post(
    "/evidence",
    response_model=DataResponse[EvidenceResponse],
    status_code=201,
    summary="Record evidence",
    description="Submit new capability evidence with source, verification level, and optional digital signature.",
)
async def record_evidence(
    body: RecordEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record self-reported capability evidence.

    Self-service path: verification_level is forced to 'self_reported'
    regardless of what the request sends. Higher trust levels
    (instructor_verified, employer_verified, etc.) must go through the
    facade (record_capability_evidence) with appropriate role checks at
    the call site (e.g. instructor grading, employer verification).
    """
    svc = EvidenceService(db)
    try:
        evidence = await svc.record_evidence(
            user_id=user.id,
            capability_id=body.capability_id,
            source_type=body.source_type,
            source_id=body.source_id,
            # Force self_reported — users cannot self-attest higher trust
            verification_level="self_reported",
            occurred_at=body.occurred_at,
            org_id=body.org_id,
            score_normalized=body.score_normalized,
            confidence=body.confidence,
            expires_at=body.expires_at,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    await db.commit()
    await db.refresh(evidence)
    return DataResponse(data=EvidenceResponse.model_validate(evidence))


@router.get(
    "/evidence/{evidence_id}",
    response_model=DataResponse[EvidenceResponse],
    summary="Get evidence detail",
    description="Returns a single evidence record with full provenance chain.",
)
async def get_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.models.evidence import CapabilityEvidence

    evidence = await db.get(CapabilityEvidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    # Users can only see their own evidence
    if evidence.user_id != user.id:
        raise HTTPException(404, "Evidence not found")
    return DataResponse(data=EvidenceResponse.model_validate(evidence))


@router.post(
    "/evidence/{evidence_id}/void",
    response_model=DataResponse[EvidenceResponse],
    summary="Void evidence",
    description="Mark an evidence record as voided. Triggers score recalculation for affected capabilities.",
)
async def void_evidence(
    evidence_id: str,
    body: VoidEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Void an evidence row (retraction)."""
    from app.talent.models.evidence import CapabilityEvidence

    # Verify ownership
    evidence = await db.get(CapabilityEvidence, evidence_id)
    if not evidence or evidence.user_id != user.id:
        raise HTTPException(404, "Evidence not found")

    svc = EvidenceService(db)
    result = await svc.void_evidence(evidence_id, reason=body.reason)
    if not result:
        raise HTTPException(409, "Evidence is not active")
    await db.commit()
    await db.refresh(result)
    return DataResponse(data=EvidenceResponse.model_validate(result))


@router.get(
    "/evidence/{evidence_id}/provenance",
    response_model=DataResponse[ProvenanceResponse],
    summary="Get evidence provenance",
    description="Returns the full provenance chain for an evidence record.",
)
async def get_provenance(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.talent.models.evidence import CapabilityEvidence

    # Verify ownership before showing provenance
    evidence = await db.get(CapabilityEvidence, evidence_id)
    if not evidence or evidence.user_id != user.id:
        raise HTTPException(404, "Evidence not found")

    svc = EvidenceService(db)
    chain = await svc.get_provenance_chain(evidence_id, requesting_user_id=user.id)
    if not chain:
        raise HTTPException(404, "Evidence not found")
    return DataResponse(data=ProvenanceResponse(chain=chain))


# ---- Derived capability profile ----


@router.get(
    "/users/{user_id}/profile",
    summary="Get user capability profile",
    description="Returns computed capability scores for a user aggregated from all verified evidence.",
)
async def get_capability_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get derived capability profile for a user.

    Respects passport privacy:
      - Own profile: always visible
      - Other user: routed through passport visibility settings
    """
    # Own profile — always full access
    if user_id == user.id:
        import dataclasses

        scores = await compute_capability_profile(db, user_id)
        return DataResponse(data=[dataclasses.asdict(s) for s in scores])

    # Other user — respect passport privacy settings
    from app.talent.services.passport import PassportService

    svc = PassportService(db)
    passport_data = await svc.get_visible_passport(
        user_id,
        requesting_user_id=user.id,
    )
    if not passport_data:
        raise HTTPException(404, "Profile not found")

    # If the passport is visible but capabilities are not in visible_fields,
    # return an empty list (the user hasn't shared capability data)
    caps = passport_data.get("capabilities", [])
    return DataResponse(data=caps)
