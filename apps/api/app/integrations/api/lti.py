"""LTI 1.3 protocol + admin endpoints (ADR-018 §8/§15).

Protocol endpoints are unauthenticated (the LMS drives the browser):
  GET/POST /lti/login   — OIDC third-party-initiated login
  POST     /lti/launch  — id_token launch (form_post)
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.config import settings
from app.core.rate_limit import rate_limit
from app.integrations.models import LtiDeployment, LtiRegistration
from app.integrations.services.lti import LtiService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

admin_router = APIRouter(prefix="/orgs/{org_id}/integrations/lti", tags=["Integrations"])
protocol_router = APIRouter(prefix="/lti", tags=["LTI"])


class LtiRegistrationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issuer: str = Field(min_length=8, max_length=500)
    client_id: str = Field(min_length=1, max_length=255)
    auth_login_url: str = Field(min_length=8, max_length=500)
    auth_token_url: str = Field(min_length=8, max_length=500)
    jwks_url: str = Field(min_length=8, max_length=500)
    deployment_ids: list[str] = Field(default_factory=list, max_length=50)
    allow_jit: bool = True
    default_role: str = "student"


class LtiRegistrationResponse(BaseModel):
    id: str
    issuer: str
    client_id: str
    auth_login_url: str
    auth_token_url: str
    jwks_url: str
    status: str
    allow_jit: bool
    default_role: str
    deployment_ids: list[str]
    created_at: datetime


class ResourceLinkMapRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deployment_id: str = Field(min_length=1, max_length=255)
    resource_link_id: str = Field(min_length=1, max_length=255)
    kind: str
    target_id: str = Field(min_length=1, max_length=26)
    grade_sync_enabled: bool = False


async def _reg_response(db: AsyncSession, reg: LtiRegistration) -> LtiRegistrationResponse:
    deployments = (
        await db.execute(
            select(LtiDeployment.deployment_id).where(LtiDeployment.registration_id == reg.id)
        )
    ).all()
    return LtiRegistrationResponse(
        id=reg.id,
        issuer=reg.issuer,
        client_id=reg.client_id,
        auth_login_url=reg.auth_login_url,
        auth_token_url=reg.auth_token_url,
        jwks_url=reg.jwks_url,
        status=reg.status,
        allow_jit=reg.allow_jit,
        default_role=reg.default_role,
        deployment_ids=[d for (d,) in deployments],
        created_at=reg.created_at,
    )


@admin_router.get("/registrations", response_model=DataResponse[list[LtiRegistrationResponse]])
async def list_registrations(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    regs = (
        await db.execute(
            select(LtiRegistration).where(LtiRegistration.org_id == org_id)
        )
    ).scalars().all()
    return {"data": [await _reg_response(db, r) for r in regs]}


@admin_router.post(
    "/registrations", response_model=DataResponse[LtiRegistrationResponse], status_code=201
)
async def create_registration(
    org_id: str,
    body: LtiRegistrationCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    reg = await LtiService(db).create_registration(
        org_id,
        issuer=body.issuer,
        client_id=body.client_id,
        auth_login_url=body.auth_login_url,
        auth_token_url=body.auth_token_url,
        jwks_url=body.jwks_url,
        deployment_ids=body.deployment_ids,
        allow_jit=body.allow_jit,
        default_role=body.default_role,
    )
    resp = await _reg_response(db, reg)
    await db.commit()
    return {"data": resp}


@admin_router.post(
    "/registrations/{reg_id}/resource-links", response_model=DataResponse[dict], status_code=201
)
async def map_resource_link(
    org_id: str,
    reg_id: str,
    body: ResourceLinkMapRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    link = await LtiService(db).map_resource_link(
        org_id,
        reg_id,
        deployment_id=body.deployment_id,
        resource_link_id=body.resource_link_id,
        kind=body.kind,
        target_id=body.target_id,
        grade_sync_enabled=body.grade_sync_enabled,
    )
    await db.commit()
    return {
        "data": {
            "id": link.id,
            "kind": link.kind,
            "target_id": link.target_id,
            "grade_sync_enabled": link.grade_sync_enabled,
        }
    }


class DeepLinkSelectRequest(BaseModel):
    """Instructor picked a platform resource to place in the LMS. The launch
    response (dev/test shape) carried the deep-linking claims the UI echoes
    back here; the endpoint returns the signed JWT + return URL for a
    browser form-post."""

    model_config = ConfigDict(extra="forbid")
    registration_id: str = Field(min_length=1, max_length=26)
    deployment_id: str = Field(min_length=1, max_length=255)
    return_url: str = Field(min_length=8, max_length=1000)
    data: str | None = Field(default=None, max_length=4000)
    kind: str
    target_id: str = Field(min_length=1, max_length=26)
    title: str = Field(min_length=1, max_length=200)


@admin_router.post("/deep-link/select", response_model=DataResponse[dict])
async def deep_link_select(
    org_id: str,
    body: DeepLinkSelectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    from app.integrations.models import LTI_RESOURCE_KINDS
    from app.integrations.security import validate_egress_url
    from app.integrations.services.lti import LtiService
    from app.integrations.services.lti_ags import (
        build_resource_link_item,
        sign_deep_linking_response,
    )

    if body.kind not in LTI_RESOURCE_KINDS:
        from app.exceptions import AppError

        raise AppError("LTI_RESOURCE_KIND_INVALID", "bad kind", 422)
    # The return URL is platform-asserted via the launch claims — still
    # egress-screened (a tampered claim must not point the browser at an
    # internal origin we vouch for).
    validate_egress_url(body.return_url)
    reg = await LtiService(db).get_registration(org_id, body.registration_id)
    launch_url = f"{str(request.base_url).rstrip('/')}/api/v1/lti/launch"
    item = build_resource_link_item(
        title=body.title, launch_url=launch_url, resource_id=f"{body.kind}:{body.target_id}"
    )
    jwt_value = await sign_deep_linking_response(
        db,
        reg,
        deployment_id=body.deployment_id,
        content_items=[item],
        data=body.data,
    )
    await db.commit()
    return {"data": {"return_url": body.return_url, "jwt": jwt_value}}


# ── protocol ──


@protocol_router.get("/jwks", dependencies=[Depends(rate_limit(30, 60))])
async def lti_tool_jwks(db: AsyncSession = Depends(get_db)):
    """The tool's public keys (platforms verify our AGS client assertions
    and deep-link JWTs against this)."""
    from app.integrations.services.lti_ags import ensure_tool_key, tool_jwks

    await ensure_tool_key(db)
    await db.commit()
    return await tool_jwks(db)


def _launch_redirect_uri(request: Request) -> str:
    return f"{str(request.base_url).rstrip('/')}/api/v1/lti/launch"


@protocol_router.get("/login", dependencies=[Depends(rate_limit(60, 60))])
@protocol_router.post("/login", dependencies=[Depends(rate_limit(60, 60))])
async def lti_login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # LMSes send initiation params as query (GET) or form (POST).
    if request.method == "POST":
        form = await request.form()
        params = {k: str(v) for k, v in form.items()}
    else:
        params = dict(request.query_params)
    iss = params.get("iss", "")[:500]
    login_hint = params.get("login_hint", "")[:500]
    target = params.get("target_link_uri", "")[:500]
    if not iss or not login_hint:
        from app.exceptions import AppError

        raise AppError("LTI_LAUNCH_INVALID", "iss and login_hint required", 422)
    url = await LtiService(db).login_initiation(
        iss=iss,
        login_hint=login_hint,
        client_id=params.get("client_id"),
        lti_message_hint=params.get("lti_message_hint"),
        target_link_uri=target,
        redirect_uri=_launch_redirect_uri(request),
    )
    await db.commit()
    return RedirectResponse(url, status_code=302)


@protocol_router.post("/launch", dependencies=[Depends(rate_limit(60, 60))])
async def lti_launch(
    request: Request,
    state: str = Form(min_length=1, max_length=64),
    id_token: str = Form(min_length=1, max_length=16384),
    db: AsyncSession = Depends(get_db),
):
    svc = LtiService(db)
    reg, link, result, claims = await svc.handle_launch(state_value=state, id_token=id_token)
    from app.services.auth import AuthService

    pair = await AuthService(db)._create_token_pair(result.user)  # noqa: SLF001
    result.user.last_login_at = datetime.now(UTC)
    import contextlib

    with contextlib.suppress(Exception):
        from app.integrations.facade import emit_event

        await emit_event(
            db,
            reg.org_id,
            "org.sso.login",
            subject=result.user.id,
            data={"user_id": result.user.id, "jit": result.jit_created, "via": "lti"},
        )
    await db.commit()
    body = {
        "access_token": pair.access_token,
        "refresh_token": pair.refresh_token,
        "token_type": "bearer",
        "jit_created": result.jit_created,
        "resource": (
            {"kind": link.kind, "target_id": link.target_id} if link is not None else None
        ),
        "message_type": claims.get(
            "https://purl.imsglobal.org/spec/lti/claim/message_type"
        ),
    }
    if settings.app_env in ("development", "test"):
        return {"data": body}
    target = "/"
    if link is not None:
        target = f"/launch/{link.kind}/{link.target_id}"
    return RedirectResponse(
        f"{target}#access_token={pair.access_token}&refresh_token={pair.refresh_token}",
        status_code=302,
    )
