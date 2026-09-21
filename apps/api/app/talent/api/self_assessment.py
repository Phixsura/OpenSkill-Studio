"""Self-assessment quiz API (N15).

Authorization:
  - Generate quiz: any authenticated user
  - Submit assessment: any authenticated user (creates own evidence)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.self_assessment import (
    AssessmentResultResponse,
    SubmitAssessmentRequest,
)

router = APIRouter(prefix="/talent", tags=["Talent — Self-Assessment"])


@router.get(
    "/self-assessment/{capability_id}/quiz",
    response_model=DataResponse[dict],
    summary="Get Quiz",
)
async def get_quiz(
    capability_id: str,
    _user: User = Depends(get_current_user),
):
    """Get self-assessment quiz questions for a capability."""
    from app.talent.services.self_assessment import SelfAssessmentService

    # No DB needed for quiz generation — it's static
    svc = SelfAssessmentService(None)  # type: ignore[arg-type]
    quiz = svc.generate_quiz(capability_id)
    return DataResponse(data=quiz)


@router.post(
    "/self-assessment/{capability_id}/submit",
    response_model=DataResponse[AssessmentResultResponse],
    status_code=201,
    summary="Submit Assessment",
)
async def submit_assessment(
    capability_id: str,
    body: SubmitAssessmentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit self-assessment answers and create evidence."""
    from app.talent.services.self_assessment import SelfAssessmentService

    svc = SelfAssessmentService(db)
    try:
        result = await svc.submit_assessment(
            user_id=user.id,
            capability_id=capability_id,
            responses=body.responses,
        )
    except ValueError:
        raise HTTPException(422, "Validation error") from None

    await db.commit()
    return DataResponse(data=AssessmentResultResponse(**result))
