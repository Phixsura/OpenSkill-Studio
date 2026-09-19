"""Application feedback service — rejection reasons, interview feedback (N8).

Visibility controls:
  - employer_only: only employer org members can see
  - shared_with_candidate: the applicant can also see
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import (
    FEEDBACK_TYPES,
    FEEDBACK_VISIBILITY,
    Application,
    ApplicationFeedback,
)


class ApplicationFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_feedback(
        self,
        *,
        application_id: str,
        feedback_type: str,
        content: str,
        visibility: str = "employer_only",
        author_id: str,
    ) -> ApplicationFeedback:
        if feedback_type not in FEEDBACK_TYPES:
            raise ValueError(
                f"Invalid feedback_type: {feedback_type}. Must be one of {sorted(FEEDBACK_TYPES)}"
            )
        if visibility not in FEEDBACK_VISIBILITY:
            raise ValueError(
                f"Invalid visibility: {visibility}. Must be one of {sorted(FEEDBACK_VISIBILITY)}"
            )

        # For rejection_reason, application must be in rejected status
        if feedback_type == "rejection_reason":
            app = await self.db.get(Application, application_id)
            if not app or app.status != "rejected":
                raise ValueError("Rejection reason can only be added to rejected applications")

        feedback = ApplicationFeedback(
            application_id=application_id,
            feedback_type=feedback_type,
            content=content,
            visibility=visibility,
            author_id=author_id,
        )
        self.db.add(feedback)
        await self.db.flush()
        return feedback

    async def list_feedback(
        self,
        application_id: str,
        *,
        viewer_user_id: str,
        is_employer: bool = False,
    ) -> list[ApplicationFeedback]:
        """List feedback for an application.

        - Employer org members see all feedback.
        - Candidates only see 'shared_with_candidate' feedback.
        """
        q = select(ApplicationFeedback).where(ApplicationFeedback.application_id == application_id)
        if not is_employer:
            q = q.where(ApplicationFeedback.visibility == "shared_with_candidate")
        q = q.order_by(ApplicationFeedback.created_at.desc())
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def update_visibility(
        self,
        feedback_id: str,
        visibility: str,
        author_id: str,
    ) -> ApplicationFeedback | None:
        """Update feedback visibility. Only the author can change this."""
        if visibility not in FEEDBACK_VISIBILITY:
            raise ValueError(
                f"Invalid visibility: {visibility}. Must be one of {sorted(FEEDBACK_VISIBILITY)}"
            )

        feedback = await self.db.get(ApplicationFeedback, feedback_id)
        if not feedback:
            return None
        if feedback.author_id != author_id:
            return None

        feedback.visibility = visibility
        await self.db.flush()
        return feedback
