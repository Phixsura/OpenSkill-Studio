"""Bulk import endpoints (ADR-018 §16.1). Upload previews by default; the
commit re-reads the stored file and refuses if it drifted (fingerprint)."""

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.config import settings
from app.exceptions import AppError
from app.integrations.models.bulk import MAX_IMPORT_BYTES
from app.integrations.services.bulk_import import BulkImportService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


class ImportJobResponse(BaseModel):
    id: str
    kind: str
    template_version: int
    mode: str
    status: str
    fingerprint: str
    dry_stats: dict
    stats: dict
    created_at: datetime


def _resp(job) -> ImportJobResponse:
    return ImportJobResponse.model_validate(job, from_attributes=True)


async def _store_file(org_id: str, job_hint: str, content: bytes) -> str:
    from ulid import ULID

    file_key = f"orgs/{org_id}/imports/{ULID()}_{job_hint}.csv"
    from app.core.storage import get_s3_client

    async for client in get_s3_client():
        await client.put_object(
            Bucket=settings.s3_bucket, Key=file_key, Body=content, ContentType="text/csv"
        )
    return file_key


async def _load_file(file_key: str) -> bytes:
    from app.core.storage import get_s3_client

    async for client in get_s3_client():
        obj = await client.get_object(Bucket=settings.s3_bucket, Key=file_key)
        return await obj["Body"].read()
    raise AppError("STORAGE_ERROR", "Could not load import file", 500)


@router.post("/imports", response_model=DataResponse[ImportJobResponse], status_code=201)
async def upload_import(
    org_id: str,
    kind: str = Form(max_length=30),
    mode: str = Form(default="partial", max_length=10),
    idempotency_key: str | None = Form(default=None, max_length=100),
    file: UploadFile = File(...),  # noqa: B008
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    content = await file.read(MAX_IMPORT_BYTES + 1)
    if len(content) > MAX_IMPORT_BYTES:
        raise AppError("IMPORT_TOO_LARGE", "file exceeds 50MB", 422)
    file_key = await _store_file(org_id, kind, content)
    job = await BulkImportService(db).create_job(
        org_id,
        kind=kind,
        mode=mode,
        file_bytes=content,
        file_key=file_key,
        created_by=user.id,
        idempotency_key=idempotency_key,
    )
    resp = _resp(job)
    await db.commit()
    return {"data": resp}


@router.get("/imports/{job_id}", response_model=DataResponse[ImportJobResponse])
async def get_import(
    org_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    return {"data": _resp(await BulkImportService(db).get(org_id, job_id))}


@router.post("/imports/{job_id}/commit", response_model=DataResponse[ImportJobResponse])
async def commit_import(
    org_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    svc = BulkImportService(db)
    job = await svc.get(org_id, job_id)
    content = await _load_file(job.file_key)
    job = await svc.commit(org_id, job_id, file_bytes=content)
    resp = _resp(job)
    await db.commit()
    return {"data": resp}


@router.get("/imports/{job_id}/errors.csv", response_class=PlainTextResponse)
async def import_errors_csv(
    org_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    csv_text = await BulkImportService(db).errors_csv(org_id, job_id)
    return PlainTextResponse(csv_text, media_type="text/csv")
