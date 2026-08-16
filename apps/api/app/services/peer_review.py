"""Peer review service — rounds, allocation, assessment, aggregation.

The allocation algorithm follows Moodle Workshop's random allocator
(mod/workshop/allocation/random): a progressive circle-square model that
guarantees fairness — the outer loop raises the required link count from 1
to N, so every reviewer gets their first assignment before anyone gets a
second. Targets are chosen lowest-workload-first with random tie-breaking;
self-review and duplicate pairs are excluded.
"""

import random
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.project import (
    PeerAssessment,
    PeerAssessmentStatus,
    PeerReviewPhase,
    PeerReviewRound,
    Project,
    Submission,
    SubmissionStatus,
)
from app.models.skill import ContentStatus

log = structlog.get_logger()


class RoundNotFoundError(AppError):
    def __init__(self):
        super().__init__("ROUND_NOT_FOUND", "Peer review round not found", 404)


class AssessmentNotFoundError(AppError):
    def __init__(self):
        super().__init__("ASSESSMENT_NOT_FOUND", "Peer assessment not found", 404)


def allocate_reviews(
    author_by_submission: dict[str, str],
    reviewers: list[str],
    num_reviews: int,
    *,
    rng: random.Random | None = None,
) -> list[tuple[str, str]]:
    """Allocate (reviewer_id, submission_id) pairs.

    Progressive fairness (Moodle model): iterate required-links from 1..N so
    every reviewer receives their first allocation before anyone receives a
    second. For each reviewer, pick the submission with the fewest reviews so
    far (random tie-break), excluding their own and already-assigned ones.
    """
    rng = rng or random.Random()
    submissions = list(author_by_submission.keys())
    if not submissions or not reviewers or num_reviews <= 0:
        return []

    review_load: dict[str, int] = {s: 0 for s in submissions}  # reviews per submission
    assigned: dict[str, set[str]] = {r: set() for r in reviewers}  # reviewer -> submissions
    pairs: list[tuple[str, str]] = []

    for _required in range(1, num_reviews + 1):
        order = list(reviewers)
        rng.shuffle(order)
        for reviewer in order:
            # candidates: not own submission, not already assigned
            candidates = [
                s
                for s in submissions
                if author_by_submission[s] != reviewer and s not in assigned[reviewer]
            ]
            if not candidates:
                continue
            min_load = min(review_load[s] for s in candidates)
            best = [s for s in candidates if review_load[s] == min_load]
            chosen = rng.choice(best)
            assigned[reviewer].add(chosen)
            review_load[chosen] += 1
            pairs.append((reviewer, chosen))

    # Repair pass: per-reviewer allocation can strand a submission with zero
    # reviews (the only zero-load target left may be the reviewer's own).
    # Swap a high-load assignment over to any unreviewed submission.
    for orphan in [s for s in submissions if review_load[s] == 0]:
        swap_candidates = [
            (i, r, s)
            for i, (r, s) in enumerate(pairs)
            if author_by_submission[orphan] != r  # can't review own
            and orphan not in assigned[r]  # no duplicate
            and review_load[s] > 1  # donor keeps >= 1 review
        ]
        if not swap_candidates:
            continue
        # Take from the highest-load donor
        swap_candidates.sort(key=lambda t: -review_load[t[2]])
        i, r, s = swap_candidates[0]
        pairs[i] = (r, orphan)
        assigned[r].discard(s)
        assigned[r].add(orphan)
        review_load[s] -= 1
        review_load[orphan] += 1

    return pairs


class PeerReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Rounds ──

    async def create_round(
        self,
        org_id: str,
        project_id: str,
        created_by: str,
        *,
        name: str,
        num_reviews: int = 2,
        anonymous: bool = True,
        include_self_review: bool = False,
        deadline: datetime | None = None,
    ) -> PeerReviewRound:
        project = await self.db.get(Project, project_id)
        if project is None or project.status == ContentStatus.ARCHIVED:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)
        if project.org_id != org_id:
            raise AppError("PROJECT_NOT_FOUND", "Project not found", 404)

        rnd = PeerReviewRound(
            org_id=org_id,
            project_id=project_id,
            name=name,
            num_reviews=num_reviews,
            anonymous=anonymous,
            include_self_review=include_self_review,
            deadline=deadline,
            created_by=created_by,
        )
        self.db.add(rnd)
        await self.db.flush()
        log.info("peer_round_created", round_id=rnd.id, project_id=project_id)
        return rnd

    async def get_round(self, round_id: str, org_id: str) -> PeerReviewRound:
        rnd = await self.db.get(PeerReviewRound, round_id)
        if rnd is None or rnd.org_id != org_id:
            raise RoundNotFoundError()
        return rnd

    async def list_rounds(self, project_id: str) -> list[PeerReviewRound]:
        result = await self.db.execute(
            select(PeerReviewRound)
            .where(PeerReviewRound.project_id == project_id)
            .order_by(PeerReviewRound.created_at.desc())
        )
        return list(result.scalars().all())

    # ── Allocation (SETUP → ASSESSMENT) ──

    async def start_assessment(self, round_id: str, org_id: str) -> tuple[PeerReviewRound, int]:
        """Allocate reviewers and move the round into the assessment phase.

        Eligible submissions: the latest SUBMITTED submission per author on
        the round's project. Reviewers = those same authors (a learner must
        have submitted to review — Moodle's musthavesubmission).
        """
        rnd = await self.get_round(round_id, org_id)
        if rnd.phase != PeerReviewPhase.SETUP:
            raise AppError("INVALID_PHASE", "Round is not in setup phase", 422)

        result = await self.db.execute(
            select(Submission)
            .where(
                Submission.project_id == rnd.project_id,
                Submission.status == SubmissionStatus.SUBMITTED,
            )
            .order_by(Submission.user_id, Submission.version.desc())
        )
        latest_by_author: dict[str, Submission] = {}
        for sub in result.scalars():
            if sub.user_id not in latest_by_author:
                latest_by_author[sub.user_id] = sub

        if len(latest_by_author) < 2:
            raise AppError(
                "NOT_ENOUGH_SUBMISSIONS",
                "At least 2 submitted learners are required for peer review",
                422,
            )

        author_by_submission = {s.id: uid for uid, s in latest_by_author.items()}
        reviewers = list(latest_by_author.keys())

        pairs = allocate_reviews(author_by_submission, reviewers, rnd.num_reviews)

        count = 0
        for reviewer_id, submission_id in pairs:
            self.db.add(
                PeerAssessment(
                    round_id=round_id,
                    submission_id=submission_id,
                    reviewer_id=reviewer_id,
                )
            )
            count += 1

        if rnd.include_self_review:
            for uid, sub in latest_by_author.items():
                self.db.add(
                    PeerAssessment(
                        round_id=round_id,
                        submission_id=sub.id,
                        reviewer_id=uid,
                        is_self_review=True,
                    )
                )
                count += 1

        rnd.phase = PeerReviewPhase.ASSESSMENT
        await self.db.flush()
        log.info("peer_round_allocated", round_id=round_id, assessments=count)
        return rnd, count

    async def close_round(self, round_id: str, org_id: str) -> PeerReviewRound:
        rnd = await self.get_round(round_id, org_id)
        if rnd.phase != PeerReviewPhase.ASSESSMENT:
            raise AppError("INVALID_PHASE", "Round is not in assessment phase", 422)
        rnd.phase = PeerReviewPhase.CLOSED
        await self.db.flush()
        return rnd

    # ── Assessments ──

    async def my_assessments(self, round_id: str, reviewer_id: str) -> list[PeerAssessment]:
        result = await self.db.execute(
            select(PeerAssessment)
            .where(
                PeerAssessment.round_id == round_id,
                PeerAssessment.reviewer_id == reviewer_id,
            )
            .order_by(PeerAssessment.created_at)
        )
        return list(result.scalars().all())

    async def list_assessments(self, round_id: str) -> list[PeerAssessment]:
        result = await self.db.execute(
            select(PeerAssessment)
            .where(PeerAssessment.round_id == round_id)
            .order_by(PeerAssessment.created_at)
        )
        return list(result.scalars().all())

    async def submit_assessment(
        self,
        assessment_id: str,
        reviewer_id: str,
        org_id: str,
        *,
        score: int,
        score_breakdown: list[dict] | None,
        feedback: str | None,
    ) -> PeerAssessment:
        assessment = await self.db.get(PeerAssessment, assessment_id)
        if assessment is None:
            raise AssessmentNotFoundError()
        rnd = await self.get_round(assessment.round_id, org_id)
        if assessment.reviewer_id != reviewer_id:
            raise AppError("PERMISSION_DENIED", "Not your assessment", 403)
        if rnd.phase != PeerReviewPhase.ASSESSMENT:
            raise AppError("INVALID_PHASE", "Round is not accepting assessments", 422)

        # Same cap the instructor review enforces — a peer score above the
        # project max would poison the round average.
        project = await self.db.get(Project, rnd.project_id)
        if project is not None and score > project.max_score:
            raise AppError(
                "SCORE_EXCEEDS_MAX",
                f"Score {score} exceeds project maximum of {project.max_score}",
                422,
            )

        assessment.score = score
        assessment.score_breakdown = score_breakdown
        assessment.feedback = feedback
        assessment.status = PeerAssessmentStatus.SUBMITTED
        assessment.submitted_at = datetime.now(UTC)
        await self.db.flush()
        log.info("peer_assessment_submitted", assessment_id=assessment_id)
        return assessment

    # ── Aggregation ──

    async def round_results(self, round_id: str, org_id: str) -> list[dict]:
        """Aggregate submitted peer scores per submission (mean, count)."""
        await self.get_round(round_id, org_id)
        result = await self.db.execute(
            select(
                PeerAssessment.submission_id,
                func.avg(PeerAssessment.score),
                func.count(PeerAssessment.id),
            )
            .where(
                PeerAssessment.round_id == round_id,
                PeerAssessment.status == PeerAssessmentStatus.SUBMITTED,
                PeerAssessment.is_self_review == False,  # noqa: E712
            )
            .group_by(PeerAssessment.submission_id)
        )
        return [
            {
                "submission_id": sid,
                "avg_score": round(float(avg), 1) if avg is not None else None,
                "review_count": count,
            }
            for sid, avg, count in result.all()
        ]
