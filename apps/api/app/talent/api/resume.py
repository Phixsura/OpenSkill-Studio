"""Resume parsing API — extract skills from resume text (N18)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.talent.schemas.resume import ParseResumeRequest, ParseResumeResponse

router = APIRouter(prefix="/talent", tags=["Talent — Resume"])


@router.post("/resume/parse", response_model=DataResponse[ParseResumeResponse])
async def parse_resume(
    body: ParseResumeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Parse resume text and extract capabilities.

    Optionally auto-creates self_reported evidence for high-confidence
    matches (confidence >= 0.80).
    """
    from app.talent.services.resume_parser import ResumeParserService

    svc = ResumeParserService(db)
    result = await svc.parse_resume_text(
        user_id=user.id,
        text=body.text,
        auto_create_evidence=body.auto_create_evidence,
    )

    if body.auto_create_evidence:
        await db.commit()

    return DataResponse(data=ParseResumeResponse(**result))
