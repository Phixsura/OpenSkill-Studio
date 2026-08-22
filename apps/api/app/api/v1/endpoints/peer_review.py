from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.peer_review import (
    AssessmentResponse,
    AssessmentWithReviewerResponse,
    CreateRoundRequest,
    RoundResponse,
    RoundResultEntry,
    SubmitAssessmentRequest,
)
from app.services.peer_review import PeerReviewService

router = APIRouter(tags=["Peer Review"])

INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


@router.post(
    "/orgs/{org_id}/peer-review-rounds",
    response_model=DataResponse[RoundResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_round(
    org_id: str,
    body: CreateRoundRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = PeerReviewService(db)
    rnd = await svc.create_round(
        org_id,
        body.project_id,
        user.id,
        name=body.name,
        num_reviews=body.num_reviews,
        anonymous=body.anonymous,
        include_self_review=body.include_self_review,
        deadline=body.deadline,
    )
    await db.commit()
    return DataResponse(data=RoundResponse.model_validate(rnd))


@router.get(
    "/orgs/{org_id}/projects/{project_id}/peer-review-rounds",
    response_model=DataResponse[list[RoundResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_rounds(
    org_id: str,
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = PeerReviewService(db)
    rounds = await svc.list_rounds(project_id)
    # Only rounds of this org (project ownership enforced via round.org_id)
    rounds = [r for r in rounds if r.org_id == org_id]
    return DataResponse(data=[RoundResponse.model_validate(r) for r in rounds])


@router.post(
    "/orgs/{org_id}/peer-review-rounds/{round_id}/start",
    response_model=DataResponse[RoundResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def start_assessment(
    org_id: str,
    round_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = PeerReviewService(db)
    rnd, _count = await svc.start_assessment(round_id, org_id)
    await db.commit()
    return DataResponse(data=RoundResponse.model_validate(rnd))


@router.post(
    "/orgs/{org_id}/peer-review-rounds/{round_id}/close",
    response_model=DataResponse[RoundResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def close_round(
    org_id: str,
    round_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = PeerReviewService(db)
    rnd = await svc.close_round(round_id, org_id)
    await db.commit()
    return DataResponse(data=RoundResponse.model_validate(rnd))


@router.get(
    "/orgs/{org_id}/peer-review-rounds/{round_id}/my-assessments",
    response_model=DataResponse[list[AssessmentResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def my_assessments(
    org_id: str,
    round_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = PeerReviewService(db)
    await svc.get_round(round_id, org_id)
    assessments = await svc.my_assessments(round_id, user.id)
    return DataResponse(data=[AssessmentResponse.model_validate(a) for a in assessments])


@router.get(
    "/orgs/{org_id}/peer-review-rounds/{round_id}/assessments",
    response_model=DataResponse[list[AssessmentWithReviewerResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def all_assessments(
    org_id: str,
    round_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor view — includes reviewer identity regardless of anonymity."""
    await require_org_member(org_id, user, db, *INSTRUCTOR_ROLES)
    svc = PeerReviewService(db)
    await svc.get_round(round_id, org_id)
    assessments = await svc.list_assessments(round_id)
    return DataResponse(
        data=[AssessmentWithReviewerResponse.model_validate(a) for a in assessments]
    )


@router.post(
    "/orgs/{org_id}/peer-assessments/{assessment_id}/submit",
    response_model=DataResponse[AssessmentResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def submit_assessment(
    org_id: str,
    assessment_id: str,
    body: SubmitAssessmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = PeerReviewService(db)
    assessment = await svc.submit_assessment(
        assessment_id,
        user.id,
        org_id,
        score=body.score,
        score_breakdown=body.score_breakdown,
        feedback=body.feedback,
    )
    await db.commit()
    return DataResponse(data=AssessmentResponse.model_validate(assessment))


@router.get(
    "/orgs/{org_id}/peer-review-rounds/{round_id}/results",
    response_model=DataResponse[list[RoundResultEntry]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def round_results(
    org_id: str,
    round_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = PeerReviewService(db)
    rnd = await svc.get_round(round_id, org_id)
    # Students may only see aggregate results after the round is CLOSED —
    # exposing everyone's peer scores mid-assessment lets a reviewer anchor
    # on the crowd and undermines the review. Instructors can see anytime.
    from app.models.project import PeerReviewPhase

    if member.role not in INSTRUCTOR_ROLES and rnd.phase != PeerReviewPhase.CLOSED:
        raise HTTPException(status_code=403, detail="Results are available once the round closes")
    results = await svc.round_results(round_id, org_id)
    return DataResponse(data=[RoundResultEntry(**r) for r in results])
