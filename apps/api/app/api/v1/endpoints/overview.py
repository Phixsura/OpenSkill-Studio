"""Cross-org personal overview for the dashboard landing page.

Aggregates the learner's actionable to-dos: draft submissions to finish,
pending peer assessments, and recent reviews received — so the dashboard
shows work, not infrastructure status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.organization import MemberStatus, OrgMember, OrgRole
from app.models.project import (
    PeerAssessment,
    PeerAssessmentStatus,
    PeerReviewPhase,
    PeerReviewRound,
    Project,
    Submission,
    SubmissionReview,
    SubmissionStatus,
)
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.overview import DraftSummary, OverviewResponse, ReviewReceived

router = APIRouter(tags=["Overview"])


@router.get("/me/overview", response_model=DataResponse[OverviewResponse], dependencies=[Depends(rate_limit(30, 60))])
async def my_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Org memberships (active only)
    member_rows = await db.execute(
        select(OrgMember.org_id, OrgMember.role).where(
            OrgMember.user_id == user.id, OrgMember.status == MemberStatus.ACTIVE
        )
    )
    memberships = list(member_rows.all())
    org_ids = [m[0] for m in memberships]
    instructor_org_ids = [
        m[0] for m in memberships if m[1] in (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    ]

    if not org_ids:
        return DataResponse(
            data=OverviewResponse(
                drafts=[],
                peer_assessments_pending=0,
                reviews_received=[],
                pending_reviews_to_grade=0,
            )
        )

    # My draft submissions (unfinished work) with project context
    drafts_r = await db.execute(
        select(Submission.id, Submission.project_id, Submission.org_id, Project.title)
        .join(Project, Project.id == Submission.project_id)
        .where(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.DRAFT,
            # Only orgs the user is still an active member of — a removed
            # member would otherwise see dead links they can no longer open.
            Submission.org_id.in_(org_ids),
        )
        .order_by(Submission.created_at.desc())
        .limit(5)
    )
    drafts = [
        DraftSummary(submission_id=sid, project_id=pid, org_id=oid, project_title=title)
        for sid, pid, oid, title in drafts_r.all()
    ]

    # Pending peer assessments assigned to me in active (assessment-phase) rounds
    peer_r = await db.execute(
        select(func.count())
        .select_from(PeerAssessment)
        .join(PeerReviewRound, PeerReviewRound.id == PeerAssessment.round_id)
        .where(
            PeerAssessment.reviewer_id == user.id,
            PeerAssessment.status == PeerAssessmentStatus.PENDING,
            PeerReviewRound.phase == PeerReviewPhase.ASSESSMENT,
            PeerReviewRound.org_id.in_(org_ids),
        )
    )
    peer_pending = peer_r.scalar_one()

    # Recent reviews received on my submissions
    reviews_r = await db.execute(
        select(
            SubmissionReview.id,
            SubmissionReview.score,
            SubmissionReview.created_at,
            Submission.project_id,
            Submission.org_id,
            Submission.id,
            Project.title,
        )
        .join(Submission, Submission.id == SubmissionReview.submission_id)
        .join(Project, Project.id == Submission.project_id)
        .where(Submission.user_id == user.id, Submission.org_id.in_(org_ids))
        .order_by(SubmissionReview.created_at.desc())
        .limit(5)
    )
    reviews = [
        ReviewReceived(
            review_id=rid,
            score=score,
            created_at=created_at.isoformat(),
            project_id=pid,
            org_id=oid,
            submission_id=sid,
            project_title=title,
        )
        for rid, score, created_at, pid, oid, sid, title in reviews_r.all()
    ]

    # Instructor: submissions waiting for MY review across my instructor orgs
    to_grade = 0
    if instructor_org_ids:
        grade_r = await db.execute(
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.org_id.in_(instructor_org_ids),
                Submission.status == SubmissionStatus.SUBMITTED,
            )
        )
        to_grade = grade_r.scalar_one()

    return DataResponse(
        data=OverviewResponse(
            drafts=drafts,
            peer_assessments_pending=peer_pending,
            reviews_received=reviews,
            pending_reviews_to_grade=to_grade,
        )
    )
