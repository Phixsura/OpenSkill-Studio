"""Privacy & Consent API (ADR-017 Part G)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.privacy import (
    ConsentRecordResponse,
    CreateConsentRecordRequest,
    CreatePrivacyReviewRequest,
    PrivacyReviewResponse,
)
from app.trustplane.services import privacy as privacy_svc

router = APIRouter(tags=["Trust — Privacy & Consent"])
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.post("/orgs/{org_id}/trust/privacy-reviews", response_model=DataResponse[PrivacyReviewResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_privacy_review(org_id: str, body: CreatePrivacyReviewRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    review = await privacy_svc.create_privacy_review(db, org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=PrivacyReviewResponse.model_validate(review))


@router.get("/orgs/{org_id}/trust/privacy-reviews", response_model=ListResponse[PrivacyReviewResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_privacy_reviews(org_id: str, system_id: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    reviews, total = await privacy_svc.list_privacy_reviews(db, org_id, system_id=system_id, page=page, per_page=per_page)
    return ListResponse(data=[PrivacyReviewResponse.model_validate(r) for r in reviews], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.get("/orgs/{org_id}/trust/privacy-reviews/{review_id}", response_model=DataResponse[PrivacyReviewResponse], dependencies=[Depends(rate_limit(30, 60))])
async def get_privacy_review(org_id: str, review_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    review = await privacy_svc.get_privacy_review(db, review_id, org_id)
    return DataResponse(data=PrivacyReviewResponse.model_validate(review))


@router.post("/orgs/{org_id}/trust/consent-records", response_model=DataResponse[ConsentRecordResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_consent_record(org_id: str, body: CreateConsentRecordRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    record = await privacy_svc.create_consent_record(db, org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ConsentRecordResponse.model_validate(record))


@router.get("/orgs/{org_id}/trust/consent-records", response_model=ListResponse[ConsentRecordResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_consent_records(org_id: str, system_id: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    records, total = await privacy_svc.list_consent_records(db, org_id, system_id=system_id, page=page, per_page=per_page)
    return ListResponse(data=[ConsentRecordResponse.model_validate(r) for r in records], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))
