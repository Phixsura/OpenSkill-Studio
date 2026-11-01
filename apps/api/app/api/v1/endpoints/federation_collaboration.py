"""Federation Collaboration, Reputation & Conformance API (Issue #45 Parts K, N, P)."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str
from app.services import federation_collaboration as collab_svc

router = APIRouter(tags=["Federation — Collaboration & Reputation"])
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Schemas ──────────────────────────────────────────────────────────


class CreateGrantRequest(BaseModel):
    peer_instance_id: str
    resource_type: str
    resource_id: str
    permissions: list[str]
    expires_at: str | None = None


class GrantResponse(BaseModel):
    id: str
    org_id: str
    peer_instance_id: str
    resource_type: str
    resource_id: str
    permissions: list
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class ReputationResponse(BaseModel):
    id: str
    org_id: str
    peer_instance_id: str
    score: float
    total_interactions: int
    successful_interactions: int
    created_at: str
    model_config = {"from_attributes": True}


class ReportIncidentRequest(BaseModel):
    peer_instance_id: str
    incident_type: str
    title: str
    description: str | None = None
    severity: str = "medium"
    evidence: dict | None = None

    @field_validator("title")
    @classmethod
    def v_title(cls, v: str) -> str:
        v = reject_ctrl_str(v, "title")
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class PeerIncidentResponse(BaseModel):
    id: str
    org_id: str
    peer_instance_id: str
    incident_type: str
    title: str
    description: str | None
    severity: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


class ConformanceResponse(BaseModel):
    peer_id: str
    peer_uri: str
    protocol_version: str
    software_version: str
    trust_status: str
    circuit_breaker: dict
    conformance: dict


class CircuitBreakerResponse(BaseModel):
    id: str
    org_id: str
    peer_instance_id: str
    state: str
    failure_count: int
    created_at: str
    model_config = {"from_attributes": True}


# ── Part K: Collaboration Grants ─────────────────────────────────────


@router.post("/orgs/{org_id}/federation/grants", response_model=DataResponse[GrantResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_grant(org_id: str, body: CreateGrantRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    grant = await collab_svc.create_collaboration_grant(db, org_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=GrantResponse.model_validate(grant))


@router.get("/orgs/{org_id}/federation/grants", response_model=ListResponse[GrantResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_grants(org_id: str, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    grants, total = await collab_svc.list_collaboration_grants(db, org_id, page=page, per_page=per_page)
    return ListResponse(data=[GrantResponse.model_validate(g) for g in grants], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part N: Reputation & Incidents ───────────────────────────────────


@router.get("/orgs/{org_id}/federation/reputation", response_model=DataResponse[list[ReputationResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_reputations(org_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    reps = await collab_svc.list_peer_reputations(db, org_id)
    return DataResponse(data=[ReputationResponse.model_validate(r) for r in reps])


@router.get("/orgs/{org_id}/federation/reputation/{peer_instance_id}", response_model=DataResponse[ReputationResponse | None], dependencies=[Depends(rate_limit(30, 60))])
async def get_reputation(org_id: str, peer_instance_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    rep = await collab_svc.get_peer_reputation(db, org_id, peer_instance_id)
    return DataResponse(data=ReputationResponse.model_validate(rep) if rep else None)


@router.post("/orgs/{org_id}/federation/peer-incidents", response_model=DataResponse[PeerIncidentResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def report_incident(org_id: str, body: ReportIncidentRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    incident = await collab_svc.report_peer_incident(db, org_id, reported_by=user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=PeerIncidentResponse.model_validate(incident))


@router.get("/orgs/{org_id}/federation/peer-incidents", response_model=ListResponse[PeerIncidentResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_incidents(org_id: str, peer_instance_id: str | None = None, status: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    incidents, total = await collab_svc.list_peer_incidents(db, org_id, peer_instance_id=peer_instance_id, status=status, page=page, per_page=per_page)
    return ListResponse(data=[PeerIncidentResponse.model_validate(i) for i in incidents], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


# ── Part P: Protocol Conformance ─────────────────────────────────────


@router.get("/orgs/{org_id}/federation/conformance/{peer_instance_id}", response_model=DataResponse[ConformanceResponse], dependencies=[Depends(rate_limit(30, 60))])
async def check_conformance(org_id: str, peer_instance_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    report = await collab_svc.check_protocol_conformance(db, org_id, peer_instance_id)
    return DataResponse(data=ConformanceResponse(**report))


@router.get("/orgs/{org_id}/federation/circuit-breakers", response_model=DataResponse[list[CircuitBreakerResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_circuit_breakers(org_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    cbs = await collab_svc.list_circuit_breakers(db, org_id)
    return DataResponse(data=[CircuitBreakerResponse.model_validate(cb) for cb in cbs])
