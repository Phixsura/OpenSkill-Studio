"""Human Oversight & Approval service (ADR-017 Part H).

Review requests with separation of duty, meaningful rationale,
and append-only decision records.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.review import (
    ReviewDecision,
    ReviewDecisionType,
    ReviewRequest,
    ReviewStatus,
    ReviewType,
)
from app.trustplane.services.audit import record_trust_audit

# ── Errors ───────────────────────────────────────────────────────────


class ReviewNotFoundError(AppError):
    def __init__(self):
        super().__init__("REVIEW_NOT_FOUND", "Review request not found", 404)


class ReviewAlreadyDecidedError(AppError):
    def __init__(self):
        super().__init__("REVIEW_ALREADY_DECIDED", "Review has already been decided", 409)


class SelfReviewForbiddenError(AppError):
    def __init__(self):
        super().__init__(
            "SELF_REVIEW_FORBIDDEN",
            "Requester cannot review their own request",
            422,
        )


class RationaleRequiredError(AppError):
    def __init__(self):
        super().__init__(
            "RATIONALE_REQUIRED",
            "A rationale is required for review decisions",
            422,
        )


# ── Review Request CRUD ──────────────────────────────────────────────


async def create_review(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    review_type: str,
    title: str,
    target_type: str,
    target_id: str,
    description: str | None = None,
    assigned_to: str | None = None,
    context: dict | None = None,
    due_at: str | None = None,
) -> ReviewRequest:
    review = ReviewRequest(
        org_id=org_id,
        review_type=ReviewType(review_type),
        status=ReviewStatus.PENDING,
        title=title,
        description=description,
        target_type=target_type,
        target_id=target_id,
        requested_by=user_id,
        assigned_to=assigned_to,
        context=context,
        due_at=datetime.fromisoformat(due_at) if due_at else None,
    )
    db.add(review)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="review.created",
        target_type="review_request",
        target_id=review.id,
        after={"review_type": review_type, "title": title, "target": f"{target_type}:{target_id}"},
    )
    return review


async def get_review(db: AsyncSession, review_id: str, org_id: str) -> ReviewRequest:
    result = await db.execute(
        select(ReviewRequest).where(
            ReviewRequest.id == review_id, ReviewRequest.org_id == org_id
        )
    )
    review = result.scalar_one_or_none()
    if review is None:
        raise ReviewNotFoundError()
    return review


async def list_reviews(
    db: AsyncSession,
    org_id: str,
    *,
    status: str | None = None,
    review_type: str | None = None,
    assigned_to: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ReviewRequest], int]:
    base = select(ReviewRequest).where(ReviewRequest.org_id == org_id)
    count_base = (
        select(func.count()).select_from(ReviewRequest).where(ReviewRequest.org_id == org_id)
    )

    if status:
        base = base.where(ReviewRequest.status == status)
        count_base = count_base.where(ReviewRequest.status == status)
    if review_type:
        base = base.where(ReviewRequest.review_type == review_type)
        count_base = count_base.where(ReviewRequest.review_type == review_type)
    if assigned_to:
        base = base.where(ReviewRequest.assigned_to == assigned_to)
        count_base = count_base.where(ReviewRequest.assigned_to == assigned_to)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(ReviewRequest.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def assign_review(
    db: AsyncSession,
    review_id: str,
    org_id: str,
    user_id: str,
    assigned_to: str,
) -> ReviewRequest:
    review = await get_review(db, review_id, org_id)
    old = review.assigned_to
    review.assigned_to = assigned_to
    if review.status == ReviewStatus.PENDING:
        review.status = ReviewStatus.IN_REVIEW
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="review.assigned",
        target_type="review_request",
        target_id=review_id,
        before={"assigned_to": old},
        after={"assigned_to": assigned_to},
    )
    return review


async def decide_review(
    db: AsyncSession,
    review_id: str,
    org_id: str,
    reviewer_id: str,
    *,
    decision: str,
    rationale: str,
    conditions: str | None = None,
) -> tuple[ReviewRequest, ReviewDecision]:
    if not rationale or not rationale.strip():
        raise RationaleRequiredError()

    review = await get_review(db, review_id, org_id)

    # Cannot decide on already-terminal reviews
    if review.status in (
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
        ReviewStatus.EXPIRED,
        ReviewStatus.CANCELLED,
    ):
        raise ReviewAlreadyDecidedError()

    # Separation of duty
    if review.requested_by == reviewer_id:
        raise SelfReviewForbiddenError()

    decision_type = ReviewDecisionType(decision)

    # Create immutable decision record
    dec = ReviewDecision(
        request_id=review_id,
        decision=decision_type,
        reviewer_id=reviewer_id,
        rationale=rationale,
        conditions=conditions,
    )
    db.add(dec)

    # Update request status
    status_map = {
        ReviewDecisionType.APPROVE: ReviewStatus.APPROVED,
        ReviewDecisionType.REJECT: ReviewStatus.REJECTED,
        ReviewDecisionType.RETURN: ReviewStatus.RETURNED,
        ReviewDecisionType.ESCALATE: ReviewStatus.IN_REVIEW,
    }
    review.status = status_map[decision_type]
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=reviewer_id,
        actor_type="user",
        action="review.decided",
        target_type="review_request",
        target_id=review_id,
        after={"decision": decision, "status": review.status.value},
    )
    return review, dec


async def cancel_review(
    db: AsyncSession,
    review_id: str,
    org_id: str,
    user_id: str,
) -> ReviewRequest:
    review = await get_review(db, review_id, org_id)
    if review.status in (
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
        ReviewStatus.CANCELLED,
    ):
        raise ReviewAlreadyDecidedError()

    review.status = ReviewStatus.CANCELLED
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="review.cancelled",
        target_type="review_request",
        target_id=review_id,
    )
    return review


async def list_decisions(
    db: AsyncSession,
    review_id: str,
    org_id: str,
) -> list[ReviewDecision]:
    """Return all decisions for a review request (append-only history)."""
    await get_review(db, review_id, org_id)
    result = await db.execute(
        select(ReviewDecision)
        .where(ReviewDecision.request_id == review_id)
        .order_by(ReviewDecision.created_at)
    )
    return list(result.scalars().all())
