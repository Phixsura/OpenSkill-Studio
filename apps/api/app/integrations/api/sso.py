"""SSO admin + protocol endpoints (ADR-018 §5/§15).

Admin surface is org-scoped (owner/admin). Protocol endpoints live OUTSIDE
the org prefix (IdPs and browsers hit them unauthenticated):
  GET /sso/login?email=        — IdP discovery by verified email domain
  GET /sso/oidc/authorize      — redirect into the IdP (state minted here)
  GET /sso/oidc/callback       — code exchange, id_token validation, session
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.config import settings
from app.exceptions import AppError
from app.integrations.services.domains import OrgDomainService
from app.integrations.services.identity import IdentityService
from app.integrations.services.sso_admin import SsoAdminService
from app.integrations.services.sso_oidc import OidcService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

admin_router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])
protocol_router = APIRouter(prefix="/sso", tags=["SSO"])


# ── schemas ──


class DomainResponse(BaseModel):
    id: str
    domain: str
    status: str
    verification_token: str
    verified_at: datetime | None
    created_at: datetime


class DomainClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    domain: str = Field(min_length=3, max_length=255)


class SsoConnectionResponse(BaseModel):
    """Write-only secret: the ciphertext column is structurally absent."""

    id: str
    org_id: str
    protocol: str
    status: str
    oidc_issuer: str | None
    oidc_client_id: str | None
    has_client_secret: bool
    attribute_map: dict
    enforce_sso: bool
    allow_jit: bool
    default_role: str
    created_at: datetime


class SsoCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    protocol: str
    oidc_issuer: str | None = Field(default=None, max_length=500)
    oidc_client_id: str | None = Field(default=None, max_length=255)
    oidc_client_secret: str | None = Field(default=None, max_length=500)
    idp_entity_id: str | None = Field(default=None, max_length=500)
    idp_sso_url: str | None = Field(default=None, max_length=500)
    idp_certificates: list[dict] = Field(default_factory=list, max_length=5)
    attribute_map: dict = Field(default_factory=dict)
    allow_jit: bool = False
    default_role: str = "student"


class SsoUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str | None = None
    oidc_issuer: str | None = Field(default=None, max_length=500)
    oidc_client_id: str | None = Field(default=None, max_length=255)
    oidc_client_secret: str | None = Field(default=None, max_length=500)
    attribute_map: dict | None = None
    enforce_sso: bool | None = None
    allow_jit: bool | None = None
    default_role: str | None = None


class BreakGlassRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(min_length=1, max_length=26)
    enabled: bool


class QueueResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str  # link | reject
    user_id: str | None = Field(default=None, max_length=26)


def _sso_response(conn) -> SsoConnectionResponse:
    return SsoConnectionResponse(
        id=conn.id,
        org_id=conn.org_id,
        protocol=conn.protocol,
        status=conn.status,
        oidc_issuer=conn.oidc_issuer,
        oidc_client_id=conn.oidc_client_id,
        has_client_secret=conn.oidc_client_secret_ct is not None,
        attribute_map=conn.attribute_map or {},
        enforce_sso=conn.enforce_sso,
        allow_jit=conn.allow_jit,
        default_role=conn.default_role,
        created_at=conn.created_at,
    )


async def _admin(org_id: str, user: User, db: AsyncSession):
    return await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)


# ── domains ──


@admin_router.get("/domains", response_model=DataResponse[list[DomainResponse]])
async def list_domains(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    rows = await OrgDomainService(db).list(org_id)
    return {"data": [DomainResponse.model_validate(r, from_attributes=True) for r in rows]}


@admin_router.post("/domains", response_model=DataResponse[DomainResponse], status_code=201)
async def claim_domain(
    org_id: str,
    body: DomainClaimRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await OrgDomainService(db).claim(org_id, body.domain)
    resp = DomainResponse.model_validate(row, from_attributes=True)
    await db.commit()
    return {"data": resp}


@admin_router.post("/domains/{domain_id}/verify", response_model=DataResponse[DomainResponse])
async def verify_domain(
    org_id: str,
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    row = await OrgDomainService(db).verify(org_id, domain_id)
    resp = DomainResponse.model_validate(row, from_attributes=True)
    await db.commit()
    return {"data": resp}


@admin_router.delete("/domains/{domain_id}", status_code=204)
async def delete_domain(
    org_id: str,
    domain_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    await OrgDomainService(db).delete(org_id, domain_id)
    await db.commit()


# ── SSO connections ──


@admin_router.get("/sso-connections", response_model=DataResponse[list[SsoConnectionResponse]])
async def list_sso_connections(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    return {"data": [_sso_response(c) for c in await SsoAdminService(db).list(org_id)]}


@admin_router.post(
    "/sso-connections", response_model=DataResponse[SsoConnectionResponse], status_code=201
)
async def create_sso_connection(
    org_id: str,
    body: SsoCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await SsoAdminService(db).create(
        org_id,
        protocol=body.protocol,
        oidc_issuer=body.oidc_issuer,
        oidc_client_id=body.oidc_client_id,
        oidc_client_secret=body.oidc_client_secret,
        idp_entity_id=body.idp_entity_id,
        idp_sso_url=body.idp_sso_url,
        idp_certificates=body.idp_certificates,
        attribute_map=body.attribute_map,
        allow_jit=body.allow_jit,
        default_role=body.default_role,
    )
    resp = _sso_response(conn)
    await db.commit()
    return {"data": resp}


@admin_router.get(
    "/sso-connections/{conn_id}", response_model=DataResponse[SsoConnectionResponse]
)
async def get_sso_connection(
    org_id: str,
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    return {"data": _sso_response(await SsoAdminService(db).get(org_id, conn_id))}


@admin_router.patch(
    "/sso-connections/{conn_id}", response_model=DataResponse[SsoConnectionResponse]
)
async def update_sso_connection(
    org_id: str,
    conn_id: str,
    body: SsoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    conn = await SsoAdminService(db).update(org_id, conn_id, **body.model_dump())
    resp = _sso_response(conn)
    await db.commit()
    return {"data": resp}


@admin_router.delete("/sso-connections/{conn_id}", status_code=204)
async def delete_sso_connection(
    org_id: str,
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    await SsoAdminService(db).delete(org_id, conn_id)
    await db.commit()


@admin_router.post("/break-glass", status_code=204)
async def set_break_glass(
    org_id: str,
    body: BreakGlassRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = await require_org_member(org_id, user, db, OrgRole.OWNER)
    await SsoAdminService(db).set_break_glass(
        org_id, body.user_id, enabled=body.enabled, actor_role=member.role
    )
    await db.commit()


# ── identity queue ──


@admin_router.get("/identity-queue", response_model=DataResponse[list[dict]])
async def list_identity_queue(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    items = await IdentityService(db).list_queue(org_id)
    return {
        "data": [
            {
                "id": i.id,
                "source": i.source,
                "subject": i.subject,
                "email": i.email,
                "reason": i.reason,
                "status": i.status,
                "created_at": i.created_at.isoformat(),
            }
            for i in items
        ]
    }


@admin_router.post("/identity-queue/{item_id}/resolve", response_model=DataResponse[dict])
async def resolve_identity_queue(
    org_id: str,
    item_id: str,
    body: QueueResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _admin(org_id, user, db)
    item = await IdentityService(db).resolve_queue_item(
        org_id, item_id, action=body.action, user_id=body.user_id, actor_id=user.id
    )
    await db.commit()
    return {"data": {"id": item.id, "status": item.status}}


# ── protocol endpoints (unauthenticated) ──


def _callback_uri(request: Request) -> str:
    # Single fixed redirect URI per environment (multi-tenant pattern).
    base = str(request.base_url).rstrip("/")
    return f"{base}/api/v1/sso/oidc/callback"


@protocol_router.get("/login")
async def sso_discovery(
    email: str = Query(min_length=3, max_length=255),
    db: AsyncSession = Depends(get_db),
):
    """IdP discovery: which org/connection handles this email domain?
    Returns only existence + the authorize URL — no org details (no oracle
    beyond what DNS already proves)."""
    org_id = await OrgDomainService(db).org_for_email_domain(email)
    if org_id is None:
        return {"data": {"sso": False}}
    from app.integrations.models import SsoConnection

    conn = (
        await db.execute(
            select(SsoConnection).where(
                SsoConnection.org_id == org_id,
                SsoConnection.status == "active",
            )
        )
    ).scalars().first()
    if conn is None:
        return {"data": {"sso": False}}
    return {
        "data": {
            "sso": True,
            "authorize_url": f"/api/v1/sso/oidc/authorize?connection={conn.id}",
        }
    }


# ── SAML protocol endpoints (P3b) ──


@protocol_router.get("/saml/metadata")
async def saml_sp_metadata():
    from fastapi.responses import Response as _Response

    from app.integrations.services.sso_saml import sp_metadata_xml

    return _Response(sp_metadata_xml(), media_type="application/samlmetadata+xml")


@protocol_router.get("/saml/authorize")
async def saml_authorize(
    connection: str = Query(min_length=1, max_length=26),
    db: AsyncSession = Depends(get_db),
):
    from app.integrations.services.sso_saml import SamlService

    url = await SamlService(db).build_authn_redirect(connection)
    await db.commit()
    return RedirectResponse(url, status_code=302)


@protocol_router.post("/saml/acs/{connection_id}")
async def saml_acs(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    from app.integrations.services.sso_saml import SamlService

    form = await request.form()
    saml_response = str(form.get("SAMLResponse", ""))
    relay_state = form.get("RelayState")
    if not saml_response:
        raise AppError("SSO_ASSERTION_INVALID", "SAMLResponse missing", 401)
    svc = SamlService(db)
    conn, result = await svc.handle_acs(
        connection_id=connection_id,
        saml_response_b64=saml_response,
        relay_state=str(relay_state) if relay_state is not None else None,
    )
    from app.services.auth import AuthService

    pair = await AuthService(db)._create_token_pair(result.user)  # noqa: SLF001
    result.user.last_login_at = datetime.now(UTC)
    import contextlib

    with contextlib.suppress(Exception):
        from app.integrations.facade import emit_event

        await emit_event(
            db,
            conn.org_id,
            "org.sso.login",
            subject=result.user.id,
            data={"user_id": result.user.id, "jit": result.jit_created, "via": "saml"},
        )
    await db.commit()
    body = {
        "access_token": pair.access_token,
        "refresh_token": pair.refresh_token,
        "token_type": "bearer",
        "jit_created": result.jit_created,
    }
    if settings.app_env in ("development", "test"):
        return {"data": body}
    return RedirectResponse(
        f"/auth/sso-complete#access_token={pair.access_token}&refresh_token={pair.refresh_token}",
        status_code=302,
    )


@protocol_router.get("/oidc/authorize")
async def oidc_authorize(
    request: Request,
    connection: str = Query(min_length=1, max_length=26),
    db: AsyncSession = Depends(get_db),
):
    url = await OidcService(db).build_authorize_redirect(
        connection, redirect_uri=_callback_uri(request)
    )
    await db.commit()
    return RedirectResponse(url, status_code=302)


@protocol_router.get("/oidc/callback")
async def oidc_callback(
    request: Request,
    state: str = Query(min_length=1, max_length=64),
    code: str = Query(default="", max_length=2000),
    error: str = Query(default="", max_length=200),
    db: AsyncSession = Depends(get_db),
):
    if error or not code:
        raise AppError("SSO_ASSERTION_INVALID", "IdP returned an error", 401)
    svc = OidcService(db)
    from app.integrations.facade import emit_event

    try:
        conn, result = await svc.handle_callback(
            state_value=state, code=code, redirect_uri=_callback_uri(request)
        )
    except AppError as exc:
        # Login audit (failure) — state row knows the connection when valid.
        await db.commit()  # persist consumed state + queue rows
        raise exc

    from app.services.auth import AuthService

    auth = AuthService(db)
    pair = await auth._create_token_pair(result.user)  # noqa: SLF001 — same-package pattern
    result.user.last_login_at = datetime.now(UTC)
    import contextlib

    with contextlib.suppress(Exception):
        await emit_event(
            db,
            conn.org_id,
            "org.sso.login",
            subject=result.user.id,
            data={"user_id": result.user.id, "jit": result.jit_created},
        )
    await db.commit()
    body = {
        "access_token": pair.access_token,
        "refresh_token": pair.refresh_token,
        "token_type": "bearer",
        "jit_created": result.jit_created,
    }
    if settings.app_env in ("development", "test"):
        return {"data": body}
    # Production: hand tokens to the SPA via fragment redirect.
    return RedirectResponse(
        f"/auth/sso-complete#access_token={pair.access_token}&refresh_token={pair.refresh_token}",
        status_code=302,
    )
