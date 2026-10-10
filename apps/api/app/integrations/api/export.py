"""Warehouse export endpoints (ADR-018 §16.2)."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.integrations.services.warehouse import S3PartWriter, WarehouseExportService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


class ExportStreamCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    dataset: str = Field(min_length=1, max_length=50)
    field_allowlist: list[str] | None = None
    anonymize: dict | None = None
    schedule: str = "manual"


class ExportStreamResponse(BaseModel):
    id: str
    name: str
    dataset: str
    field_allowlist: list
    anonymize: dict
    schedule: str
    cursor: dict
    enabled: bool
    created_at: datetime


class ExportRunResponse(BaseModel):
    id: str
    stream_id: str
    status: str
    cursor_from: dict
    cursor_to: dict
    row_count: int
    parts: list
    manifest_key: str | None
    error: str | None
    created_at: datetime
    finished_at: datetime | None


@router.get("/export-streams", response_model=DataResponse[list[ExportStreamResponse]])
async def list_streams(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    rows = await WarehouseExportService(db).list_streams(org_id)
    return {"data": [ExportStreamResponse.model_validate(r, from_attributes=True) for r in rows]}


@router.post(
    "/export-streams", response_model=DataResponse[ExportStreamResponse], status_code=201
)
async def create_stream(
    org_id: str,
    body: ExportStreamCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    stream = await WarehouseExportService(db).create_stream(
        org_id,
        name=body.name,
        dataset=body.dataset,
        field_allowlist=body.field_allowlist,
        anonymize=body.anonymize,
        schedule=body.schedule,
    )
    resp = ExportStreamResponse.model_validate(stream, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.post(
    "/export-streams/{stream_id}/run",
    response_model=DataResponse[ExportRunResponse],
    status_code=202,
)
async def run_stream(
    org_id: str,
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    run = await WarehouseExportService(db, writer=S3PartWriter()).run_export(org_id, stream_id)
    resp = ExportRunResponse.model_validate(run, from_attributes=True)
    await db.commit()
    return {"data": resp}


@router.get(
    "/export-streams/{stream_id}/runs", response_model=DataResponse[list[ExportRunResponse]]
)
async def list_stream_runs(
    org_id: str,
    stream_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    rows = await WarehouseExportService(db).list_runs(org_id, stream_id)
    return {"data": [ExportRunResponse.model_validate(r, from_attributes=True) for r in rows]}
