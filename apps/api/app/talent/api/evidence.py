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
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.talent.schemas.evidence import (
    CapabilityScoreResponse,
    EvidenceResponse,
    ProvenanceResponse,
    RecordEvidenceRequest,
    VoidEvidenceRequest,
)
from app.talent.services.evidence import EvidenceService
from app.talent.services.scoring import compute_capability_profile

router = APIRouter(prefix="/talent", tags=["Talent — Evidence"])


@router.get("/evidence", response_model=ListResponse[EvidenceResponse])
async def list_evidence(
    capability_id: str | None = None,
    status: str = "active",
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List own evidence."""
    svc = EvidenceService(db)
    items, total = await svc.get_evidence_for_user(
        user.id,
        capability_id=capability_id,
        status=status,
        limit=per_page,
        offset=(page - 1) * per_page,
    )
    return ListResponse(
        data=[EvidenceResponse.model_validate(e) for e in items],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=page * per_page < total),
    )


@router.post("/evidence", response_model=DataResponse[EvidenceResponse], status_code=201)
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
    return DataResponse(data=EvidenceResponse.model_validate(evidence))


@router.get("/evidence/{evidence_id}", response_model=DataResponse[EvidenceResponse])
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


@router.post("/evidence/{evidence_id}/void", response_model=DataResponse[EvidenceResponse])
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
    return DataResponse(data=EvidenceResponse.model_validate(result))


@router.get("/evidence/{evidence_id}/provenance", response_model=DataResponse[ProvenanceResponse])
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

@router.get("/users/{user_id}/profile", response_model=DataResponse[list[CapabilityScoreResponse]])
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
        scores = await compute_capability_profile(db, user_id)
        return DataResponse(
            data=[CapabilityScoreResponse(**s.__dict__) for s in scores]
        )

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
