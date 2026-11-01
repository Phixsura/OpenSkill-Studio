"""Federation Exchange API (Issue #45 Parts D–J, M, N).

Cross-instance artifact exchange, credential verification, talent mobility,
opportunity/marketplace/ecosystem federation, federated search, and
data residency policies.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import (
    DataResponse,
    ListResponse,
    PaginationMeta,
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
)
from app.services import federation_exchange as fed_svc

router = APIRouter(tags=["Federation — Exchange"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Schemas ──────────────────────────────────────────────────────────


class PublishArtifactRequest(BaseModel):
    artifact_type: str
    artifact_id: str
    version: str
    manifest: dict
    checksum: str
    signature: str | None = None
    target_instance_id: str | None = None

    @field_validator("manifest")
    @classmethod
    def v_manifest(cls, v: dict) -> dict:
        reject_ctrl_json(v, "manifest")
        reject_deep_json(v, "manifest")
        return v


class ArtifactResponse(BaseModel):
    id: str
    org_id: str
    artifact_type: str
    artifact_id: str
    version: str
    checksum: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class CreateCredentialVerificationRequest(BaseModel):
    user_id: str
    credential_type: str
    credential_id: str
    issuer_instance_id: str
    verification_data: dict


class CredentialVerificationResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    credential_type: str
    credential_id: str
    issuer_instance_id: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class CreateAccountLinkRequest(BaseModel):
    user_id: str
    remote_instance_id: str
    remote_user_ref: str
    link_type: str = "portable_profile"


class AccountLinkResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    remote_instance_id: str
    remote_user_ref: str
    link_type: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class CreatePortabilityRecordRequest(BaseModel):
    user_id: str
    record_type: str
    source_instance_id: str
    destination_instance_id: str
    data_manifest: dict


class PublishOpportunityRequest(BaseModel):
    opportunity_id: str
    title: str
    description: str | None = None
    requirements: dict | None = None
    target_instances: list | None = None

    @field_validator("title")
    @classmethod
    def v_title(cls, v: str) -> str:
        return reject_ctrl_str(v, "title")


class OpportunityResponse(BaseModel):
    id: str
    org_id: str
    opportunity_id: str
    title: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class PublishListingRequest(BaseModel):
    listing_id: str
    title: str
    listing_type: str
    price_info: dict | None = None
    target_instances: list | None = None


class ListingResponse(BaseModel):
    id: str
    org_id: str
    listing_id: str
    title: str
    listing_type: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class PublishObservationRequest(BaseModel):
    observation_type: str
    subject_type: str
    subject_id: str
    data: dict
    source_instance_id: str | None = None


class ObservationResponse(BaseModel):
    id: str
    org_id: str
    observation_type: str
    subject_type: str
    subject_id: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class CreateResidencyPolicyRequest(BaseModel):
    name: str
    allowed_regions: list[str]
    blocked_regions: list[str] | None = None
    data_categories: list[str] | None = None
    enforcement_mode: str = "enforce"

    @field_validator("name")
    @classmethod
    def v_name(cls, v: str) -> str:
        v = reject_ctrl_str(v, "name")
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class ResidencyPolicyResponse(BaseModel):
    id: str
    org_id: str
    name: str
    allowed_regions: list
    blocked_regions: list
    data_categories: list
    enforcement_mode: str
    is_active: bool
    created_at: str
    model_config = {"from_attributes": True}


# ── Part D: Artifacts ────────────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/artifacts", response_model=DataResponse[ArtifactResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def publish_artifact(org_id: str, body: PublishArtifactRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    artifact = await fed_svc.publish_artifact(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ArtifactResponse.model_validate(artifact))


@router.get("/orgs/{org_id}/federation/artifacts", response_model=ListResponse[ArtifactResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_artifacts(org_id: str, artifact_type: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    artifacts, total = await fed_svc.list_artifacts(db, org_id, artifact_type=artifact_type, page=page, per_page=per_page)
    return ListResponse(data=[ArtifactResponse.model_validate(a) for a in artifacts], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.get("/orgs/{org_id}/federation/artifacts/{artifact_id}", response_model=DataResponse[ArtifactResponse], dependencies=[Depends(rate_limit(30, 60))])
async def get_artifact(org_id: str, artifact_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    artifact = await fed_svc.get_artifact(db, artifact_id, org_id)
    return DataResponse(data=ArtifactResponse.model_validate(artifact))


# ── Part E: Credentials ──────────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/credentials/verify", response_model=DataResponse[CredentialVerificationResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_credential_verification(org_id: str, body: CreateCredentialVerificationRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    verification = await fed_svc.create_credential_verification(db, org_id, **body.model_dump())
    await db.commit()
    return DataResponse(data=CredentialVerificationResponse.model_validate(verification))


@router.get("/orgs/{org_id}/federation/credentials", response_model=ListResponse[CredentialVerificationResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_credential_verifications(org_id: str, user_id: str | None = None, status: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    verifications, total = await fed_svc.list_credential_verifications(db, org_id, user_id=user_id, status=status, page=page, per_page=per_page)
    return ListResponse(data=[CredentialVerificationResponse.model_validate(v) for v in verifications], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part F: Talent Mobility ──────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/account-links", response_model=DataResponse[AccountLinkResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_account_link(org_id: str, body: CreateAccountLinkRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    link = await fed_svc.create_account_link(db, org_id, **body.model_dump())
    await db.commit()
    return DataResponse(data=AccountLinkResponse.model_validate(link))


@router.get("/orgs/{org_id}/federation/account-links", response_model=ListResponse[AccountLinkResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_account_links(org_id: str, user_id: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    links, total = await fed_svc.list_account_links(db, org_id, user_id=user_id, page=page, per_page=per_page)
    return ListResponse(data=[AccountLinkResponse.model_validate(lk) for lk in links], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part G: Opportunities ────────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/opportunities", response_model=DataResponse[OpportunityResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def publish_opportunity(org_id: str, body: PublishOpportunityRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    opp = await fed_svc.publish_opportunity(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=OpportunityResponse.model_validate(opp))


@router.get("/orgs/{org_id}/federation/opportunities", response_model=ListResponse[OpportunityResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_opportunities(org_id: str, status: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    opps, total = await fed_svc.list_opportunities(db, org_id, status=status, page=page, per_page=per_page)
    return ListResponse(data=[OpportunityResponse.model_validate(o) for o in opps], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part H: Marketplace ──────────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/marketplace", response_model=DataResponse[ListingResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def publish_listing(org_id: str, body: PublishListingRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    listing = await fed_svc.publish_listing(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ListingResponse.model_validate(listing))


@router.get("/orgs/{org_id}/federation/marketplace", response_model=ListResponse[ListingResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_marketplace_listings(org_id: str, listing_type: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    listings, total = await fed_svc.list_marketplace_listings(db, org_id, listing_type=listing_type, page=page, per_page=per_page)
    return ListResponse(data=[ListingResponse.model_validate(ls) for ls in listings], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part I: Ecosystem Intelligence ───────────────────────────────────


@router.post("/orgs/{org_id}/federation/observations", response_model=DataResponse[ObservationResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def publish_observation(org_id: str, body: PublishObservationRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    obs = await fed_svc.publish_observation(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ObservationResponse.model_validate(obs))


@router.get("/orgs/{org_id}/federation/observations", response_model=ListResponse[ObservationResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_observations(org_id: str, observation_type: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    obs, total = await fed_svc.list_observations(db, org_id, observation_type=observation_type, page=page, per_page=per_page)
    return ListResponse(data=[ObservationResponse.model_validate(o) for o in obs], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part M: Data Residency ───────────────────────────────────────────


@router.post("/orgs/{org_id}/federation/residency-policies", response_model=DataResponse[ResidencyPolicyResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_residency_policy(org_id: str, body: CreateResidencyPolicyRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, OrgRole.OWNER)
    policy = await fed_svc.create_residency_policy(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ResidencyPolicyResponse.model_validate(policy))


@router.get("/orgs/{org_id}/federation/residency-policies", response_model=DataResponse[list[ResidencyPolicyResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_residency_policies(org_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    policies = await fed_svc.list_residency_policies(db, org_id)
    return DataResponse(data=[ResidencyPolicyResponse.model_validate(p) for p in policies])
