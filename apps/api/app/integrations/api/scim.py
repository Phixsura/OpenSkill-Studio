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
from app.core.rate_limit import rate_limit
from app.integrations.facade import record_fabric_audit
from app.integrations.services.scim import (
    MAX_BULK_OPERATIONS,
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


def _project(body: dict, attributes: str | None, excluded: str | None) -> dict:
    """R496 (RFC 7644 §3.9): honor ?attributes / ?excludedAttributes on read
    surfaces. Top-level keys only (sub-attribute selection keeps the parent);
    id + schemas are always returned; meta rides along under `attributes`
    so schema-aware clients can still validate the resource."""
    if not attributes and not excluded:
        return body

    def one(res: dict) -> dict:
        if attributes:
            keep = {a.strip().split(".")[0] for a in attributes.split(",") if a.strip()}
            keep |= {"schemas", "id", "meta"}
            return {k: v for k, v in res.items() if k in keep}
        drop = {a.strip().split(".")[0] for a in (excluded or "").split(",") if a.strip()}
        drop -= {"schemas", "id"}
        return {k: v for k, v in res.items() if k not in drop}

    if isinstance(body.get("Resources"), list):
        out = dict(body)
        out["Resources"] = [one(r) for r in body["Resources"] if isinstance(r, dict)]
        return out
    return one(body)


async def _auth(db: AsyncSession, authorization: str | None) -> ScimToken:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise ScimError(401, "Bearer token required")
    return await ScimTokenService(db).authenticate(authorization[7:].strip())


async def _run(db: AsyncSession, authorization: str | None, fn):
    """Authenticate, run, commit; render ScimError as its RFC body. On a
    ScimError the whole operation is ROLLED BACK (atomicity — a partially
    applied op must not persist); the best-effort last_used_at bump and any
    audit row written before the error roll back with it, which is correct
    because the action they describe did not take effect."""
    try:
        token = await _auth(db, authorization)
        result = await fn(token)
        await db.commit()
        return result
    except ScimError as exc:
        await db.rollback()
        return _scim_json(exc.body(), exc.status)


# ── discovery ──


@scim_router.get("/ServiceProviderConfig", dependencies=[Depends(rate_limit(240, 60))])
async def service_provider_config():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": True},
            "bulk": {
                "supported": True,
                # advertised == enforced (apply_bulk reads the same constant)
                "maxOperations": MAX_BULK_OPERATIONS,
                "maxPayloadSize": 1_048_576,
            },
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


# R496 (scim2-tester conformance): discovery sub-resources are served from
# ONE table so /ResourceTypes, /ResourceTypes/{id}, /Schemas and
# /Schemas/{id} can never drift apart.
def _attr(
    name: str,
    *,
    type_: str = "string",
    multi: bool = False,
    required: bool = False,
    sub: list[dict] | None = None,
) -> dict:
    out = {
        "name": name,
        "type": type_,
        "multiValued": multi,
        "required": required,
        "mutability": "readWrite",
        "returned": "default",
        "uniqueness": "none",
    }
    if sub is not None:
        # Complex attributes DECLARE their sub-attributes — a schema-aware
        # client (scim2-models) rejects undeclared keys as "extra inputs",
        # so the declaration must match what _user/_group_resource emit.
        out["subAttributes"] = sub
    return out


_SCHEMA_DOCS: dict[str, dict] = {
    "urn:ietf:params:scim:schemas:core:2.0:User": {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
        "id": "urn:ietf:params:scim:schemas:core:2.0:User",
        "name": "User",
        "description": "User account (supported subset)",
        "attributes": [
            # userName is the platform identity (email) — settable at
            # creation, never mutated through SCIM (takeover class, R26-33).
            {**_attr("userName", required=True), "mutability": "immutable"},
            _attr("displayName"),
            _attr("name", type_="complex", sub=[_attr("formatted")]),
            # emails mirror userName (identity IS the email) — read-only.
            {
                **_attr(
                    "emails",
                    type_="complex",
                    multi=True,
                    sub=[_attr("value"), _attr("primary", type_="boolean")],
                ),
                "mutability": "readOnly",
            },
            _attr("active", type_="boolean"),
            _attr("externalId"),
        ],
    },
    "urn:ietf:params:scim:schemas:core:2.0:Group": {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
        "id": "urn:ietf:params:scim:schemas:core:2.0:Group",
        "name": "Group",
        "description": "Group (supported subset)",
        "attributes": [
            _attr("displayName", required=True),
            _attr(
                "members",
                type_="complex",
                multi=True,
                sub=[_attr("value"), _attr("display")],
            ),
            _attr("externalId"),
        ],
    },
}

_RESOURCE_TYPE_DOCS: dict[str, dict] = {
    "User": {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
        "id": "User",
        "name": "User",
        "endpoint": "/Users",
        "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
    },
    "Group": {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
        "id": "Group",
        "name": "Group",
        "endpoint": "/Groups",
        "schema": "urn:ietf:params:scim:schemas:core:2.0:Group",
    },
}


@scim_router.get("/ResourceTypes", dependencies=[Depends(rate_limit(240, 60))])
async def resource_types():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(_RESOURCE_TYPE_DOCS),
            "Resources": list(_RESOURCE_TYPE_DOCS.values()),
        }
    )


@scim_router.get("/ResourceTypes/{type_id}", dependencies=[Depends(rate_limit(240, 60))])
async def resource_type_by_id(type_id: str):
    doc = _RESOURCE_TYPE_DOCS.get(type_id)
    if doc is None:
        return _scim_json(ScimError(404, f"ResourceType {type_id!r} not found").body(), 404)
    return _scim_json(doc)


@scim_router.get("/Schemas", dependencies=[Depends(rate_limit(240, 60))])
async def schemas():
    return _scim_json(
        {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(_SCHEMA_DOCS),
            "Resources": list(_SCHEMA_DOCS.values()),
        }
    )


@scim_router.get("/Schemas/{schema_id:path}", dependencies=[Depends(rate_limit(240, 60))])
async def schema_by_id(schema_id: str):
    doc = _SCHEMA_DOCS.get(schema_id)
    if doc is None:
        return _scim_json(ScimError(404, f"Schema {schema_id!r} not found").body(), 404)
    return _scim_json(doc)


# ── Users ──


@scim_router.post("/Bulk", dependencies=[Depends(rate_limit(60, 60))])
async def bulk(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    """RFC 7644 §3.7 (R52): bulk user/group operations under one request."""
    from app.integrations.services.scim import apply_bulk

    raw = await request.body()
    if len(raw) > 1_048_576:
        return _scim_json(ScimError(413, "Payload exceeds 1MB", "tooLarge").body(), 413)

    async def run(token):
        # R353: parse INSIDE the _run wrapper — a ScimError raised out here
        # (non-dict JSON) escaped as a 500 before.
        body = await _json_body(request)
        return _scim_json(await apply_bulk(db, token, body))

    return await _run(db, authorization, run)


@scim_router.get("/Users", dependencies=[Depends(rate_limit(240, 60))])
async def list_users(
    filter: str | None = Query(default=None, max_length=300),  # noqa: A002
    startIndex: int = Query(default=1, ge=1),  # noqa: N803
    count: int = Query(default=100, ge=0, le=200),
    attributes: str | None = Query(default=None, max_length=500),
    excludedAttributes: str | None = Query(default=None, max_length=500),  # noqa: N803
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        body = await ScimUserService(db, token).list(
            filter_expr=filter, start_index=startIndex, count=count
        )
        return _scim_json(_project(body, attributes, excludedAttributes))

    return await _run(db, authorization, fn)


@scim_router.post("/Users", dependencies=[Depends(rate_limit(240, 60))])
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


@scim_router.get("/Users/{user_id}", dependencies=[Depends(rate_limit(240, 60))])
async def get_user(
    user_id: str,
    attributes: str | None = Query(default=None, max_length=500),
    excludedAttributes: str | None = Query(default=None, max_length=500),  # noqa: N803
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        body = await ScimUserService(db, token).get(user_id)
        return _scim_json(_project(body, attributes, excludedAttributes))

    return await _run(db, authorization, fn)


@scim_router.put("/Users/{user_id}", dependencies=[Depends(rate_limit(240, 60))])
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


@scim_router.patch("/Users/{user_id}", dependencies=[Depends(rate_limit(240, 60))])
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


@scim_router.delete("/Users/{user_id}", dependencies=[Depends(rate_limit(240, 60))])
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


@scim_router.get("/Groups", dependencies=[Depends(rate_limit(240, 60))])
async def list_groups(
    startIndex: int = Query(default=1, ge=1),  # noqa: N803
    count: int = Query(default=100, ge=0, le=200),
    filter: str | None = Query(default=None, max_length=256),  # noqa: A002 — SCIM param name
    attributes: str | None = Query(default=None, max_length=500),
    excludedAttributes: str | None = Query(default=None, max_length=500),  # noqa: N803
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        body = await ScimGroupService(db, token).list(
            start_index=startIndex, count=count, filter_expr=filter
        )
        return _scim_json(_project(body, attributes, excludedAttributes))

    return await _run(db, authorization, fn)


@scim_router.post("/Groups", dependencies=[Depends(rate_limit(240, 60))])
async def create_group(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        payload = await _json_body(request)
        return _scim_json(await ScimGroupService(db, token).create(payload), 201)

    return await _run(db, authorization, fn)


@scim_router.get("/Groups/{group_id}", dependencies=[Depends(rate_limit(240, 60))])
async def get_group(
    group_id: str,
    attributes: str | None = Query(default=None, max_length=500),
    excludedAttributes: str | None = Query(default=None, max_length=500),  # noqa: N803
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def fn(token):
        body = await ScimGroupService(db, token).get(group_id)
        return _scim_json(_project(body, attributes, excludedAttributes))

    return await _run(db, authorization, fn)


@scim_router.put("/Groups/{group_id}", dependencies=[Depends(rate_limit(240, 60))])
async def replace_group(
    group_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    async def run(token):
        payload = await _json_body(request)  # R353: inside the wrapper
        return _scim_json(await ScimGroupService(db, token).replace(group_id, payload))

    return await _run(db, authorization, run)


@scim_router.patch("/Groups/{group_id}", dependencies=[Depends(rate_limit(240, 60))])
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


@scim_router.delete("/Groups/{group_id}", dependencies=[Depends(rate_limit(240, 60))])
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
    await record_fabric_audit(db, org_id, user.id, "intg.scim_token.minted", "scim_token", token.id)
    await db.commit()
    return {"data": resp}


@token_admin_router.patch("/scim-tokens/{token_id}", response_model=DataResponse[ScimTokenResponse])
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
    await record_fabric_audit(
        db,
        org_id,
        user.id,
        "intg.scim_token.group_map_updated",
        "scim_token",
        token.id,
        after={"group_map_keys": sorted((body.group_map or {}).keys())[:50]},
    )
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
    await record_fabric_audit(
        db, org_id, user.id, "intg.scim_token.revoked", "scim_token", token_id
    )
    await db.commit()


# ── R496: SCIM-shaped 404/405 for every unknown /scim/v2 path ──
# Registered LAST so every real route above wins; RFC 7644 clients (and
# scim2-tester's random_url / endpoint_methods checks) expect the error
# schema on 404s AND a 405 for a wrong METHOD on a known resource root.
_SCIM_ROOTS = {"ServiceProviderConfig", "ResourceTypes", "Schemas", "Users", "Groups", "Bulk"}


@scim_router.api_route(
    "/{rest:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
    dependencies=[Depends(rate_limit(240, 60))],
)
async def scim_not_found(rest: str):
    if rest.split("/", 1)[0] in _SCIM_ROOTS:
        return _scim_json(ScimError(405, "Method not allowed on this resource").body(), 405)
    return _scim_json(ScimError(404, "Resource not found").body(), 404)
