"""SCIM 2.0 protocol router (/scim/v2) + org-scoped token admin (ADR-018 §5.3).

Protocol responses/errors are SCIM-shaped (RFC 7644), not the app envelope.
The bearer token resolves the org; the URL carries no org id.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.integrations.services.scim import (
    ScimError,
    ScimGroupService,
    ScimToken,
    ScimTokenService,
    ScimUserService,
)
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

scim_router = APIRouter(prefix="/scim/v2", tags=["SCIM"])
token_admin_router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])

_CT = "application/scim+json"


def _scim_json(body: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(body, status_code=status, media_type=_CT)


async def _auth(
    db: AsyncSession, authorization: str | None
) -> ScimToken:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise ScimError(401, "Bearer token required")
    return await ScimTokenService(db).authenticate(authorization[7:].strip())


async def _run(db: AsyncSession, authorization: str | None, fn):
    """Authenticate, run, commit; render ScimError as its RFC body. The
    error path still commits — last_used_at and audit rows must survive."""
    try:
        token = await _auth(db, authorization)
        result = await fn(token)
        await db.commit()
        return result
    except ScimError as exc:
        await db.rollback()
        return _scim_json(exc.body(), exc.status)


# ── discovery ──


@scim_router.get("/ServiceProviderConfig")
async def service_provider_config():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": True},
            "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
            "filter": {"supported": True, "maxResults": 200},
            "changePassword": {"supported": False},
            "sort": {"supported": False},
            "etag": {"supported": False},
            "authenticationSchemes": [
                {
                    "type": "oauthbearertoken",
                    "name": "Bearer token",
                    "description": "Org-scoped SCIM bearer token",
                }
            ],
        }
    )


@scim_router.get("/ResourceTypes")
async def resource_types():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 2,
            "Resources": [
                {
                    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
                    "id": "User",
                    "name": "User",
                    "endpoint": "/Users",
                    "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
                },
                {
                    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
                    "id": "Group",
                    "name": "Group",
                    "endpoint": "/Groups",
                    "schema": "urn:ietf:params:scim:schemas:core:2.0:Group",
                },
            ],
        }
    )


@scim_router.get("/Schemas")
async def schemas():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": 2,
            "Resources": [
                {"id": "urn:ietf:params:scim:schemas:core:2.0:User", "name": "User"},
                {"id": "urn:ietf:params:scim:schemas:core:2.0:Group", "name": "Group"},
            ],
        }
    )


# ── Users ──


@scim_router.get("/Users")
async def list_users(
    filter: str | None = Query(default=None, max_length=300),  # noqa: A002
    startIndex: int = Query(default=1, ge=1),  # noqa: N803
    count: int = Query(default=100, ge=0, le=200),
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        body = await ScimUserService(db, token).list(
            filter_expr=filter, start_index=startIndex, count=count
        )
        return _scim_json(body)

    return await _run(db, authorization, fn)


@scim_router.post("/Users")
async def create_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        body, _created = await ScimUserService(db, token).create(payload)
        return _scim_json(body, 201)

    return await _run(db, authorization, fn)


@scim_router.get("/Users/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        return _scim_json(await ScimUserService(db, token).get(user_id))

    return await _run(db, authorization, fn)


@scim_router.put("/Users/{user_id}")
async def replace_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        return _scim_json(await ScimUserService(db, token).replace(user_id, payload))

    return await _run(db, authorization, fn)


@scim_router.patch("/Users/{user_id}")
async def patch_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        return _scim_json(await ScimUserService(db, token).patch(user_id, payload))

    return await _run(db, authorization, fn)


@scim_router.delete("/Users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        await ScimUserService(db, token).delete(user_id)
        return Response(status_code=204)

    return await _run(db, authorization, fn)


# ── Groups ──


@scim_router.get("/Groups")
async def list_groups(
    startIndex: int = Query(default=1, ge=1),  # noqa: N803
    count: int = Query(default=100, ge=0, le=200),
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        return _scim_json(
            await ScimGroupService(db, token).list(start_index=startIndex, count=count)
        )

    return await _run(db, authorization, fn)


@scim_router.post("/Groups")
async def create_group(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        return _scim_json(await ScimGroupService(db, token).create(payload), 201)

    return await _run(db, authorization, fn)


@scim_router.get("/Groups/{group_id}")
async def get_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        return _scim_json(await ScimGroupService(db, token).get(group_id))

    return await _run(db, authorization, fn)


@scim_router.patch("/Groups/{group_id}")
async def patch_group(
    group_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        return _scim_json(await ScimGroupService(db, token).patch(group_id, payload))

    return await _run(db, authorization, fn)


@scim_router.delete("/Groups/{group_id}")
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        await ScimGroupService(db, token).delete(group_id)
        return Response(status_code=204)

    return await _run(db, authorization, fn)


async def _json_body(request: Request) -> dict:
    import json

    raw = await request.body()
    if len(raw) > 262_144:  # 256KB cap
        raise ScimError(413, "Payload too large")
    try:
        payload = json.loads(raw or b"{}")
    except json.JSONDecodeError:
        raise ScimError(400, "Invalid JSON", "invalidSyntax") from None
    if not isinstance(payload, dict):
        raise ScimError(400, "Body must be an object", "invalidSyntax")
    return payload


# ── token admin (org-scoped, app envelope) ──


class ScimTokenCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    group_map: dict = Field(default_factory=dict)


class ScimTokenGroupMapRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group_map: dict


class ScimTokenResponse(BaseModel):
    """token value appears ONLY in the create response (shown once)."""

    id: str
    name: str
    group_map: dict
    last_used_at: datetime | None
    created_at: datetime
    revoked_at: datetime | None
    token: str | None = None


def _token_resp(t, raw=None) -> ScimTokenResponse:
    return ScimTokenResponse(
        id=t.id,
        name=t.name,
        group_map=t.group_map or {},
        last_used_at=t.last_used_at,
        created_at=t.created_at,
        revoked_at=t.revoked_at,
        token=raw,
    )


@token_admin_router.get("/scim-tokens", response_model=DataResponse[list[ScimTokenResponse]])
async def list_scim_tokens(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    return {"data": [_token_resp(t) for t in await ScimTokenService(db).list(org_id)]}


@token_admin_router.post(
    "/scim-tokens", response_model=DataResponse[ScimTokenResponse], status_code=201
)
async def create_scim_token(
    org_id: str,
    body: ScimTokenCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    token, raw = await ScimTokenService(db).create(
        org_id, name=body.name, group_map=body.group_map, created_by=user.id
    )
    resp = _token_resp(token, raw)
    await db.commit()
    return {"data": resp}


@token_admin_router.patch(
    "/scim-tokens/{token_id}", response_model=DataResponse[ScimTokenResponse]
)
async def update_scim_token(
    org_id: str,
    token_id: str,
    body: ScimTokenGroupMapRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    token = await ScimTokenService(db).update_group_map(org_id, token_id, body.group_map)
    resp = _token_resp(token)
    await db.commit()
    return {"data": resp}


@token_admin_router.delete("/scim-tokens/{token_id}", status_code=204)
async def revoke_scim_token(
    org_id: str,
    token_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    await ScimTokenService(db).revoke(org_id, token_id)
    await db.commit()
