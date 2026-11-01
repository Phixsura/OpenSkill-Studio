"""Evidence Graph & Human Oversight API (ADR-017 Phase 2).

Org-scoped endpoints for assurance cases, evidence items, evidence
linking, review requests, and review decisions.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.evidence import (
    CaseResponse,
    ChangeCaseStatusRequest,
    ChangeEvidenceStatusRequest,
    CreateCaseRequest,
    CreateEvidenceRequest,
    CreateReviewRequest,
    DecideReviewRequest,
    DecisionResponse,
    EvidenceLinkResponse,
    EvidenceResponse,
    EvidenceSummaryResponse,
    LinkEvidenceRequest,
    ReviewResponse,
    ReviewSummaryResponse,
    UpdateCaseRequest,
)
from app.trustplane.services import evidence as evidence_svc
from app.trustplane.services import review as review_svc

router = APIRouter(tags=["Trust — Evidence & Reviews"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Assurance Cases ──────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/cases",
    response_model=DataResponse[CaseResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_case(
    org_id: str,
    body: CreateCaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    case = await evidence_svc.create_case(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=CaseResponse.model_validate(case))


@router.get(
    "/orgs/{org_id}/trust/cases",
    response_model=ListResponse[CaseResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_cases(
    org_id: str,
    system_id: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    cases, total = await evidence_svc.list_cases(
        db, org_id, system_id=system_id, status=status, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[CaseResponse.model_validate(c) for c in cases],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.get(
    "/orgs/{org_id}/trust/cases/{case_id}",
    response_model=DataResponse[CaseResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_case(
    org_id: str,
    case_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    case = await evidence_svc.get_case(db, case_id, org_id)
    return DataResponse(data=CaseResponse.model_validate(case))


@router.patch(
    "/orgs/{org_id}/trust/cases/{case_id}",
    response_model=DataResponse[CaseResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_case(
    org_id: str,
    case_id: str,
    body: UpdateCaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    case = await evidence_svc.update_case(
        db, case_id, org_id, user.id, **body.model_dump(exclude_unset=True)
    )
    await db.commit()
    return DataResponse(data=CaseResponse.model_validate(case))


@router.post(
    "/orgs/{org_id}/trust/cases/{case_id}/status",
    response_model=DataResponse[CaseResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def change_case_status(
    org_id: str,
    case_id: str,
    body: ChangeCaseStatusRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    case = await evidence_svc.change_case_status(db, case_id, org_id, user.id, body.status)
    await db.commit()
    return DataResponse(data=CaseResponse.model_validate(case))


# ── Evidence linking to cases ────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/trust/cases/{case_id}/evidence",
    response_model=DataResponse[list[EvidenceLinkResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_case_evidence(
    org_id: str,
    case_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    rows = await evidence_svc.list_case_evidence(db, case_id, org_id)
    items = []
    for row in rows:
        items.append(
            EvidenceLinkResponse(
                link_id=row["link_id"],
                relation=row["relation"],
                notes=row["notes"],
                evidence=EvidenceSummaryResponse.model_validate(row["evidence"]),
            )
        )
    return DataResponse(data=items)


@router.post(
    "/orgs/{org_id}/trust/cases/{case_id}/evidence",
    response_model=DataResponse[dict],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def link_evidence_to_case(
    org_id: str,
    case_id: str,
    body: LinkEvidenceRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    link = await evidence_svc.link_evidence(
        db, case_id, body.evidence_id, org_id, user.id,
        relation=body.relation, notes=body.notes,
    )
    await db.commit()
    return DataResponse(data={"id": link.id, "case_id": case_id, "evidence_id": body.evidence_id, "relation": body.relation})


@router.delete(
    "/orgs/{org_id}/trust/evidence-links/{link_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def unlink_evidence(
    org_id: str,
    link_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    await evidence_svc.unlink_evidence(db, link_id, org_id, user.id)
    await db.commit()


# ── Evidence Items ───────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/evidence",
    response_model=DataResponse[EvidenceResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_evidence(
    org_id: str,
    body: CreateEvidenceRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    item = await evidence_svc.create_evidence(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=EvidenceResponse.model_validate(item))


@router.get(
    "/orgs/{org_id}/trust/evidence",
    response_model=ListResponse[EvidenceSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_evidence(
    org_id: str,
    evidence_type: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    items, total = await evidence_svc.list_evidence(
        db, org_id, evidence_type=evidence_type, status=status,
        page=page, per_page=per_page,
    )
    return ListResponse(
        data=[EvidenceSummaryResponse.model_validate(e) for e in items],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.get(
    "/orgs/{org_id}/trust/evidence/{evidence_id}",
    response_model=DataResponse[EvidenceResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_evidence(
    org_id: str,
    evidence_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    item = await evidence_svc.get_evidence(db, evidence_id, org_id)
    return DataResponse(data=EvidenceResponse.model_validate(item))


@router.post(
    "/orgs/{org_id}/trust/evidence/{evidence_id}/status",
    response_model=DataResponse[EvidenceResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def change_evidence_status(
    org_id: str,
    evidence_id: str,
    body: ChangeEvidenceStatusRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    item = await evidence_svc.change_evidence_status(
        db, evidence_id, org_id, user.id, body.status
    )
    await db.commit()
    return DataResponse(data=EvidenceResponse.model_validate(item))


# ── Review Requests ──────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/reviews",
    response_model=DataResponse[ReviewResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_review(
    org_id: str,
    body: CreateReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    review = await review_svc.create_review(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=ReviewResponse.model_validate(review))


@router.get(
    "/orgs/{org_id}/trust/reviews",
    response_model=ListResponse[ReviewSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_reviews(
    org_id: str,
    status: str | None = None,
    review_type: str | None = None,
    assigned_to: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    reviews, total = await review_svc.list_reviews(
        db, org_id, status=status, review_type=review_type,
        assigned_to=assigned_to, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[ReviewSummaryResponse.model_validate(r) for r in reviews],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.get(
    "/orgs/{org_id}/trust/reviews/{review_id}",
    response_model=DataResponse[ReviewResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_review(
    org_id: str,
    review_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    review = await review_svc.get_review(db, review_id, org_id)
    return DataResponse(data=ReviewResponse.model_validate(review))


@router.post(
    "/orgs/{org_id}/trust/reviews/{review_id}/decide",
    response_model=DataResponse[DecisionResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def decide_review(
    org_id: str,
    review_id: str,
    body: DecideReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    _, decision = await review_svc.decide_review(
        db, review_id, org_id, user.id,
        decision=body.decision, rationale=body.rationale,
        conditions=body.conditions,
    )
    await db.commit()
    return DataResponse(data=DecisionResponse.model_validate(decision))


@router.post(
    "/orgs/{org_id}/trust/reviews/{review_id}/cancel",
    response_model=DataResponse[ReviewResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def cancel_review(
    org_id: str,
    review_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    review = await review_svc.cancel_review(db, review_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=ReviewResponse.model_validate(review))


@router.get(
    "/orgs/{org_id}/trust/reviews/{review_id}/decisions",
    response_model=DataResponse[list[DecisionResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_decisions(
    org_id: str,
    review_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    decisions = await review_svc.list_decisions(db, review_id, org_id)
    return DataResponse(data=[DecisionResponse.model_validate(d) for d in decisions])
