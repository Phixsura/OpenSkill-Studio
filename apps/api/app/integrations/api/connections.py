"""Connection + provider admin endpoints (ADR-018 §15).

All org-scoped routes require an admin-or-above org member. Cross-tenant
ids answer 404 (service-level uniform-404).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.integrations.models import IntegrationConnection, IntegrationProvider
from app.integrations.schemas import (
    ConnectionCreateRequest,
    ConnectionResponse,
    ConnectionUpdateRequest,
    CredentialResponse,
    CredentialWriteRequest,
    PingResponse,
    ProviderResponse,
)
from app.integrations.services.connections import ConnectionService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


async def _admin(org_id: str, user: User, db: AsyncSession) -> None:
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)


async def _to_response(db: AsyncSession, conn: IntegrationConnection) -> ConnectionResponse:
    provider = await db.get(IntegrationProvider, conn.provider_id)
    from app.integrations.models import IntegrationConnectionCredential

    cred = await db.execute(
        select(IntegrationConnectionCredential.id).where(
            IntegrationConnectionCredential.connection_id == conn.id
        )
    )
    return ConnectionResponse(
        id=conn.id,
        org_id=conn.org_id,
        provider_key=provider.key if provider else "?",
        provider_version=conn.provider_version,
        name=conn.name,
        status=conn.status,
        config=conn.config or {},
        base_url=conn.base_url,
        health=conn.health or {},
        has_credential=cred.scalar_one_or_none() is not None,
        created_at=conn.created_at,
        updated_at=conn.updated_at,
    )


@router.get("/providers", response_model=DataResponse[list[ProviderResponse]])
async def list_providers(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    providers = await ConnectionService(db).list_providers()
    return {"data": [ProviderResponse.model_validate(p, from_attributes=True) for p in providers]}


@router.get("/connections", response_model=DataResponse[list[ConnectionResponse]])
async def list_connections(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conns = await ConnectionService(db).list(org_id)
    return {"data": [await _to_response(db, c) for c in conns]}


@router.post("/connections", response_model=DataResponse[ConnectionResponse], status_code=201)
async def create_connection(
    org_id: str,
    body: ConnectionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await ConnectionService(db).create(
        org_id,
        provider_key=body.provider_key,
        name=body.name,
        config=body.config,
        base_url=body.base_url,
        created_by=user.id,
    )
    resp = await _to_response(db, conn)
    await db.commit()
    return {"data": resp}


@router.get("/connections/{connection_id}", response_model=DataResponse[ConnectionResponse])
async def get_connection(
    org_id: str,
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await ConnectionService(db).get(org_id, connection_id)
    return {"data": await _to_response(db, conn)}


@router.patch("/connections/{connection_id}", response_model=DataResponse[ConnectionResponse])
async def update_connection(
    org_id: str,
    connection_id: str,
    body: ConnectionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await ConnectionService(db).update(
        org_id,
        connection_id,
        name=body.name,
        config=body.config,
        base_url=body.base_url,
        status=body.status,
    )
    resp = await _to_response(db, conn)
    await db.commit()
    return {"data": resp}


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    org_id: str,
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    await ConnectionService(db).delete(org_id, connection_id)
    await db.commit()


@router.post(
    "/connections/{connection_id}/credentials",
    response_model=DataResponse[CredentialResponse],
    status_code=201,
)
async def set_credential(
    org_id: str,
    connection_id: str,
    body: CredentialWriteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    cred = await ConnectionService(db).set_credential(
        org_id,
        connection_id,
        kind=body.kind,
        values=body.values,
        expires_at=body.expires_at,
    )
    resp = CredentialResponse(
        id=cred.id, kind=cred.kind, expires_at=cred.expires_at, rotated_at=cred.rotated_at
    )
    await db.commit()
    return {"data": resp}


@router.post(
    "/connections/{connection_id}/upgrade", response_model=DataResponse[ConnectionResponse]
)
async def upgrade_connection(
    org_id: str,
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await ConnectionService(db).upgrade(org_id, connection_id)
    resp = await _to_response(db, conn)
    await db.commit()
    return {"data": resp}


@router.post("/connections/{connection_id}/ping", response_model=DataResponse[PingResponse])
async def ping_connection(
    org_id: str,
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    svc = ConnectionService(db)
    from app.exceptions import AppError

    try:
        conn = await svc.ping(org_id, connection_id)
    except AppError as exc:
        if exc.code == "CONNECTION_NOT_FOUND":
            raise
        # Health already recorded by the service; surface the failure as a
        # structured ping result rather than an error envelope.
        await db.commit()
        return {"data": PingResponse(ok=False, status="failed", detail=exc.code)}
    await db.commit()
    return {"data": PingResponse(ok=True, status=conn.status)}
