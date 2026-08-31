"""Provider connection/offering endpoints (ADR-011).

Credential values are WRITE-ONLY: accepted on create/update, encrypted at
rest, and never returned by any GET. Responses carry only credential_id.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.provider import (
    AdapterResponse,
    CapabilityResponse,
    ConnectionResponse,
    CreateConnectionRequest,
    CreateOfferingRequest,
    OfferingResponse,
    UpdateConnectionRequest,
    UpdateOfferingRequest,
)
from app.services.provider import ProviderService

router = APIRouter(tags=["Providers"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Platform catalogs (authenticated read) ─────────────────


@router.get(
    "/capabilities",
    response_model=DataResponse[list[CapabilityResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_capabilities(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ProviderService(db)
    caps = await svc.list_capabilities()
    return DataResponse(data=[CapabilityResponse.model_validate(c) for c in caps])


@router.get(
    "/providers/adapters",
    response_model=DataResponse[list[AdapterResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_adapters(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ProviderService(db)
    adapters = await svc.list_adapters()
    return DataResponse(data=[AdapterResponse.model_validate(a) for a in adapters])


# ── Org connections (ADMIN+) ──────────────────────────────


@router.post(
    "/orgs/{org_id}/provider-connections",
    response_model=DataResponse[ConnectionResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_connection(
    org_id: str,
    body: CreateConnectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    conn = await svc.create_connection(
        org_id=org_id,
        adapter_id=body.adapter_id,
        name=body.name,
        config=body.config,
        credentials=body.credentials,
        created_by=user.id,
    )
    await db.commit()
    return DataResponse(data=ConnectionResponse.model_validate(conn))


@router.get(
    "/orgs/{org_id}/provider-connections",
    response_model=DataResponse[list[ConnectionResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_connections(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProviderService(db)
    conns = await svc.list_connections(org_id)
    return DataResponse(data=[ConnectionResponse.model_validate(c) for c in conns])


@router.get(
    "/orgs/{org_id}/provider-connections/{connection_id}",
    response_model=DataResponse[ConnectionResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_connection(
    org_id: str,
    connection_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProviderService(db)
    conn = await svc.get_connection(connection_id, org_id)
    return DataResponse(data=ConnectionResponse.model_validate(conn))


@router.put(
    "/orgs/{org_id}/provider-connections/{connection_id}",
    response_model=DataResponse[ConnectionResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_connection(
    org_id: str,
    connection_id: str,
    body: UpdateConnectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    # exclude_unset (NOT exclude_none): an explicit `"credentials": null`
    # detaches and deletes the credential, while an absent field leaves it
    # unchanged — passing body.credentials directly made the two
    # indistinguishable, so credentials could never be detached.
    fields = body.model_dump(exclude_unset=True)
    conn = await svc.update_connection(
        connection_id,
        org_id,
        name=fields.get("name"),
        config=fields.get("config"),
        status=fields.get("status"),
        updated_by=user.id,
        **({"credentials": fields["credentials"]} if "credentials" in fields else {}),
    )
    await db.commit()
    return DataResponse(data=ConnectionResponse.model_validate(conn))


@router.delete(
    "/orgs/{org_id}/provider-connections/{connection_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_connection(
    org_id: str,
    connection_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    await svc.delete_connection(connection_id, org_id)
    await db.commit()


# ── Offerings ─────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/provider-offerings",
    response_model=DataResponse[OfferingResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_offering(
    org_id: str,
    body: CreateOfferingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    offering = await svc.create_offering(
        org_id=org_id,
        connection_id=body.connection_id,
        capability_key=body.capability_key,
        model_name=body.model_name,
        features=body.features,
        limits=body.limits,
        cost_per_call_usd=body.cost_per_call_usd,
        quality_tier=body.quality_tier,
    )
    await db.commit()
    return DataResponse(data=OfferingResponse.model_validate(offering))


@router.get(
    "/orgs/{org_id}/provider-offerings",
    response_model=DataResponse[list[OfferingResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_offerings(
    org_id: str,
    capability: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = ProviderService(db)
    offerings = await svc.list_offerings(org_id, capability_key=capability, active_only=False)
    return DataResponse(data=[OfferingResponse.model_validate(o) for o in offerings])


@router.put(
    "/orgs/{org_id}/provider-offerings/{offering_id}",
    response_model=DataResponse[OfferingResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_offering(
    org_id: str,
    offering_id: str,
    body: UpdateOfferingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    # exclude_unset (NOT exclude_none): an explicit `"cost_per_call_usd": null`
    # must clear the cost, while an absent field leaves it unchanged —
    # passing every body attribute made the two indistinguishable, so a
    # priced offering could never go back to unknown cost.
    offering = await svc.update_offering(
        offering_id,
        org_id,
        **body.model_dump(exclude_unset=True),
    )
    await db.commit()
    return DataResponse(data=OfferingResponse.model_validate(offering))


@router.delete(
    "/orgs/{org_id}/provider-offerings/{offering_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_offering(
    org_id: str,
    offering_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = ProviderService(db)
    await svc.delete_offering(offering_id, org_id)
    await db.commit()
