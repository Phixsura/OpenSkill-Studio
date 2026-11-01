"""Privacy & Consent service (ADR-017 Part G)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.inventory import AISystem
from app.trustplane.models.privacy import (
    ConsentRecord,
    ConsentStatus,
    DataClassification,
    LegalBasis,
    PrivacyReview,
    PrivacyReviewStatus,
)
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError


class PrivacyReviewNotFoundError(AppError):
    def __init__(self):
        super().__init__("PRIVACY_REVIEW_NOT_FOUND", "Privacy review not found", 404)


class ConsentRecordNotFoundError(AppError):
    def __init__(self):
        super().__init__("CONSENT_RECORD_NOT_FOUND", "Consent record not found", 404)


async def create_privacy_review(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> PrivacyReview:
    system_id = data["system_id"]
    r = await db.execute(select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id))
    if r.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    review = PrivacyReview(
        org_id=org_id,
        system_id=system_id,
        title=data["title"],
        status=PrivacyReviewStatus.DRAFT,
        data_classification=DataClassification(data.get("data_classification", "internal")),
        data_inputs=data.get("data_inputs", []),
        data_outputs=data.get("data_outputs", []),
        purpose_limitation=data.get("purpose_limitation"),
        minimization_measures=data.get("minimization_measures", []),
        redaction_config=data.get("redaction_config"),
        retention_policy=data.get("retention_policy"),
        legal_basis=LegalBasis(data["legal_basis"]) if data.get("legal_basis") else None,
        legal_basis_detail=data.get("legal_basis_detail"),
        regions=data.get("regions", []),
        cross_region_transfers=data.get("cross_region_transfers", []),
        provider_data_use=data.get("provider_data_use"),
        created_by=user_id,
    )
    db.add(review)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="privacy_review.created", target_type="privacy_review", target_id=review.id,
        after={"title": data["title"], "system_id": system_id},
    )
    return review


async def get_privacy_review(db: AsyncSession, review_id: str, org_id: str) -> PrivacyReview:
    result = await db.execute(
        select(PrivacyReview).where(PrivacyReview.id == review_id, PrivacyReview.org_id == org_id)
    )
    review = result.scalar_one_or_none()
    if review is None:
        raise PrivacyReviewNotFoundError()
    return review


async def list_privacy_reviews(
    db: AsyncSession, org_id: str, *, system_id: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[PrivacyReview], int]:
    base = select(PrivacyReview).where(PrivacyReview.org_id == org_id)
    count_q = select(func.count()).select_from(PrivacyReview).where(PrivacyReview.org_id == org_id)
    if system_id:
        base = base.where(PrivacyReview.system_id == system_id)
        count_q = count_q.where(PrivacyReview.system_id == system_id)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(PrivacyReview.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def create_consent_record(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> ConsentRecord:
    system_id = data["system_id"]
    r = await db.execute(select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id))
    if r.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    from datetime import UTC, datetime

    record = ConsentRecord(
        org_id=org_id,
        system_id=system_id,
        purpose=data["purpose"],
        consent_status=ConsentStatus(data["consent_status"]),
        data_categories=data.get("data_categories", []),
        granted_at=datetime.now(UTC) if data["consent_status"] == "granted" else None,
    )
    db.add(record)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="consent.created", target_type="consent_record", target_id=record.id,
        after={"purpose": data["purpose"], "consent_status": data["consent_status"]},
    )
    return record


async def list_consent_records(
    db: AsyncSession, org_id: str, *, system_id: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[ConsentRecord], int]:
    base = select(ConsentRecord).where(ConsentRecord.org_id == org_id)
    count_q = select(func.count()).select_from(ConsentRecord).where(ConsentRecord.org_id == org_id)
    if system_id:
        base = base.where(ConsentRecord.system_id == system_id)
        count_q = count_q.where(ConsentRecord.system_id == system_id)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(ConsentRecord.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total
