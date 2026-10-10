"""Mapping profile + sync engine admin endpoints (ADR-018 §15)."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.integrations.services.mapping import MappingService
from app.integrations.services.sync_engine import SyncProfileService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


async def _admin(org_id: str, user: User, db: AsyncSession) -> None:
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)


# ── schemas ──


class MappingCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    direction: str
    model: str
    document: dict
    connection_id: str | None = Field(default=None, max_length=26)


class MappingUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: dict


class MappingPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    samples: list[dict] = Field(min_length=1, max_length=20)


class MappingResponse(BaseModel):
    id: str
    name: str
    direction: str
    model: str
    document: dict
    version: int
    connection_id: str | None
    created_at: datetime


class SyncProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    connection_id: str = Field(min_length=1, max_length=26)
    name: str = Field(min_length=1, max_length=200)
    model: str
    direction: str
    mapping_profile_id: str | None = Field(default=None, max_length=26)
    schedule: str = "manual"
    field_policy: dict = Field(default_factory=dict)
    options: dict = Field(default_factory=dict)


class SyncProfileResponse(BaseModel):
    id: str
    connection_id: str
    name: str
    model: str
    direction: str
    mapping_profile_id: str | None
    mapping_version: int | None
    schedule: str
    field_policy: dict
    options: dict
    enabled: bool
    created_at: datetime


class SyncRunResponse(BaseModel):
    id: str
    profile_id: str
    status: str
    trigger: str
    cursor_in: dict
    cursor_out: dict
    stats: dict
    error: dict | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class RecordResultResponse(BaseModel):
    id: str
    external_id: str
    model: str
    outcome: str
    conflict_class: str | None
    detail: dict
    resolved_by: str | None
    resolved_action: str | None
    created_at: datetime


class ResolveConflictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str = Field(pattern="^(accept_theirs|keep_ours|dismiss)$")


# ── mapping profiles ──


@router.get("/mapping-profiles", response_model=DataResponse[list[MappingResponse]])
async def list_mappings(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    rows = await MappingService(db).list(org_id)
    return {"data": [MappingResponse.model_validate(r, from_attributes=True) for r in rows]}


@router.post("/mapping-profiles", response_model=DataResponse[MappingResponse], status_code=201)
async def create_mapping(
    org_id: str,
    body: MappingCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await MappingService(db).create(
        org_id,
        name=body.name,
        direction=body.direction,
        model=body.model,
        document=body.document,
        connection_id=body.connection_id,
    )
    resp = MappingResponse.model_validate(row, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.get("/mapping-profiles/{profile_id}", response_model=DataResponse[MappingResponse])
async def get_mapping(
    org_id: str,
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await MappingService(db).get(org_id, profile_id)
    return {"data": MappingResponse.model_validate(row, from_attributes=True)}


@router.patch("/mapping-profiles/{profile_id}", response_model=DataResponse[MappingResponse])
async def update_mapping(
    org_id: str,
    profile_id: str,
    body: MappingUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await MappingService(db).update_document(org_id, profile_id, body.document)
    resp = MappingResponse.model_validate(row, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.post("/mapping-profiles/{profile_id}/preview", response_model=DataResponse[list[dict]])
async def preview_mapping(
    org_id: str,
    profile_id: str,
    body: MappingPreviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    return {"data": await MappingService(db).preview(org_id, profile_id, body.samples)}


# ── sync profiles / runs ──


@router.get("/sync-profiles", response_model=DataResponse[list[SyncProfileResponse]])
async def list_sync_profiles(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    rows = await SyncProfileService(db).list(org_id)
    return {"data": [SyncProfileResponse.model_validate(r, from_attributes=True) for r in rows]}


@router.post("/sync-profiles", response_model=DataResponse[SyncProfileResponse], status_code=201)
async def create_sync_profile(
    org_id: str,
    body: SyncProfileCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await SyncProfileService(db).create(
        org_id,
        connection_id=body.connection_id,
        name=body.name,
        model=body.model,
        direction=body.direction,
        mapping_profile_id=body.mapping_profile_id,
        schedule=body.schedule,
        field_policy=body.field_policy,
        options=body.options,
    )
    resp = SyncProfileResponse.model_validate(row, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.post(
    "/sync-profiles/{profile_id}/run", response_model=DataResponse[SyncRunResponse], status_code=202
)
async def trigger_sync(
    org_id: str,
    profile_id: str,
    backfill: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    run = await SyncProfileService(db).trigger(
        org_id, profile_id, trigger="backfill" if backfill else "manual"
    )
    resp = SyncRunResponse.model_validate(run, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.get("/sync-runs", response_model=DataResponse[list[SyncRunResponse]])
async def list_sync_runs(
    org_id: str,
    profile_id: str | None = Query(default=None, max_length=26),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    rows = await SyncProfileService(db).list_runs(org_id, profile_id)
    return {"data": [SyncRunResponse.model_validate(r, from_attributes=True) for r in rows]}


@router.get("/sync-runs/{run_id}", response_model=DataResponse[SyncRunResponse])
async def get_sync_run(
    org_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    run, _ = await SyncProfileService(db)._run_scoped(org_id, run_id)  # noqa: SLF001
    return {"data": SyncRunResponse.model_validate(run, from_attributes=True)}


@router.post("/sync-runs/{run_id}/cancel", response_model=DataResponse[SyncRunResponse])
async def cancel_sync_run(
    org_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    run = await SyncProfileService(db).cancel(org_id, run_id)
    resp = SyncRunResponse.model_validate(run, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.get(
    "/sync-runs/{run_id}/records", response_model=DataResponse[list[RecordResultResponse]]
)
async def sync_run_records(
    org_id: str,
    run_id: str,
    outcome: str | None = Query(default=None, max_length=20),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    rows = await SyncProfileService(db).run_records(org_id, run_id, outcome)
    return {"data": [RecordResultResponse.model_validate(r, from_attributes=True) for r in rows]}


@router.post(
    "/sync-runs/{run_id}/records/{result_id}/resolve",
    response_model=DataResponse[RecordResultResponse],
)
async def resolve_sync_conflict(
    org_id: str,
    run_id: str,
    result_id: str,
    body: ResolveConflictRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    result = await SyncProfileService(db).resolve_conflict(
        org_id, run_id, result_id, action=body.action, actor_id=user.id
    )
    resp = RecordResultResponse.model_validate(result, from_attributes=True)
    await db.commit()
    return {"data": resp}
