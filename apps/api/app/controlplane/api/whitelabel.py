"""White-label endpoints: branding, domains, site-context, blueprints,
provisioning, exports (ADR-014 §10.5)."""

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.branding import (
    TenantBlueprint,
    TenantBranding,
    TenantDomain,
    TenantExport,
    TenantProvisionRun,
)
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services import branding as branding_svc
from app.controlplane.services import domains as domain_svc
from app.controlplane.services import provisioning as provision_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import record_audit
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import (
    DataResponse,
    ListResponse,
    PaginationMeta,
    reject_ctrl_str,
    reject_header_str,
)

log = structlog.get_logger()

router = APIRouter(tags=["White-label"])

_BILLING_ROLES = ("billing_admin", "platform_admin")


class BrandingRequest(BaseModel):
    product_display_name: str | None = Field(default=None, max_length=100)
    theme_tokens: dict | None = None
    login_tagline: str | None = Field(default=None, max_length=200)
    email_from_name: str | None = Field(default=None, max_length=100)
    email_footer: str | None = Field(default=None, max_length=500)
    certificate_footer: str | None = Field(default=None, max_length=300)
    support_email: EmailStr | None = None
    support_url: str | None = Field(default=None, max_length=500)
    legal_links: list[dict] | None = Field(default=None, max_length=5)

    @field_validator(
        "product_display_name",
        "login_tagline",
        "email_footer",
        "certificate_footer",
    )
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)

    @field_validator("email_from_name")
    @classmethod
    def _hdr(cls, v, info):
        # R95[m7]: this value lands in the email From display-name — a
        # HEADER context. reject_ctrl_str allows \r\n (multi-line body
        # semantics); a CRLF here is header injection (BCC smuggling,
        # extra headers). Header-strict validator.
        return reject_header_str(v, info.field_name)


class CreateDomainRequest(BaseModel):
    hostname: str = Field(min_length=3, max_length=253)


class VerifyDomainRequest(BaseModel):
    token: str = Field(min_length=8, max_length=128)


class CreateBlueprintRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    config: dict

    @field_validator("name", "description")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class ProvisionRequest(BaseModel):
    blueprint_id: str = Field(min_length=26, max_length=26)
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    idempotency_key: str = Field(min_length=8, max_length=120)

    @field_validator("name")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


def _branding_response(b: TenantBranding | None) -> dict:
    if b is None:
        return {"theme_tokens": {}, "legal_links": []}
    return {
        "product_display_name": b.product_display_name,
        "logo_key": b.logo_key,
        "favicon_key": b.favicon_key,
        "theme_tokens": b.theme_tokens,
        "login_tagline": b.login_tagline,
        "email_from_name": b.email_from_name,
        "email_footer": b.email_footer,
        "certificate_footer": b.certificate_footer,
        "support_email": b.support_email,
        "support_url": b.support_url,
        "legal_links": b.legal_links,
    }


def _domain_response(d: TenantDomain, raw_token: str | None = None) -> dict:
    data = {
        "id": d.id,
        "hostname": d.hostname,
        "status": d.status,
        "is_primary": d.is_primary,
        "verified_at": d.verified_at.isoformat() if d.verified_at else None,
        "activated_at": d.activated_at.isoformat() if d.activated_at else None,
        "failure_reason": d.failure_reason,
        "tls_status": d.tls_status,
        "verification_record": f"{domain_svc.VERIFY_RECORD_PREFIX}.{d.hostname}",
    }
    if raw_token is not None:
        data["verification_token"] = raw_token  # shown ONCE
    return data


def _run_response(run: TenantProvisionRun) -> dict:
    return {
        "id": run.id,
        "blueprint_id": run.blueprint_id,
        "tenant_id": run.tenant_id,
        "status": run.status,
        "steps": [
            {"step": s.get("step"), "status": s.get("status"), "error": s.get("error")}
            for s in run.steps
            if s.get("step") != "snapshot_config"
        ],
        "error": run.error,
    }


# ── Branding ─────────────────────────────────────────────────


@router.get("/tenants/{tenant_id}/branding", dependencies=[Depends(rate_limit(60, 60))])
async def get_branding(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    branding = (
        await db.execute(select(TenantBranding).where(TenantBranding.tenant_id == tenant_id))
    ).scalar_one_or_none()
    return DataResponse(data=_branding_response(branding))


@router.put("/tenants/{tenant_id}/branding", dependencies=[Depends(rate_limit(20, 60))])
async def update_branding(
    tenant_id: str,
    body: BrandingRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner", "billing_admin")
    tenant = await db.get(TenantAccount, tenant_id)
    from app.controlplane import facade

    await facade.require_feature(db, tenant, "white_label")
    branding = await branding_svc.upsert_branding(
        db,
        tenant_id,
        body.model_dump(exclude_unset=True),
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    return DataResponse(data=_branding_response(branding))


# ── Domains ──────────────────────────────────────────────────


@router.get("/tenants/{tenant_id}/domains", dependencies=[Depends(rate_limit(30, 60))])
async def list_domains(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(TenantDomain)
                .where(TenantDomain.tenant_id == tenant_id)
                .order_by(TenantDomain.created_at)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_domain_response(d) for d in rows],
        meta=PaginationMeta(total=len(rows), page=1, per_page=len(rows) or 1, has_more=False),
    )


@router.post(
    "/tenants/{tenant_id}/domains",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_domain(
    tenant_id: str,
    body: CreateDomainRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    tenant_svc.require_tenant_active(tenant)
    from app.controlplane import facade

    await facade.require_feature(db, tenant, "custom_domain")
    domain, raw_token = await domain_svc.create_domain(
        db,
        tenant_id=tenant_id,
        hostname=body.hostname,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    return DataResponse(data=_domain_response(domain, raw_token))


async def _tenant_domain(db: AsyncSession, tenant_id: str, domain_id: str) -> TenantDomain:
    domain = await db.get(TenantDomain, domain_id)
    if domain is None or domain.tenant_id != tenant_id:
        raise AppError("DOMAIN_INVALID", "Domain not found", 404)
    return domain


@router.post(
    "/tenants/{tenant_id}/domains/{domain_id}/verify",
    dependencies=[Depends(rate_limit(6, 3600))],
)
async def verify_domain(
    tenant_id: str,
    domain_id: str,
    body: VerifyDomainRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    domain = await _tenant_domain(db, tenant_id, domain_id)
    try:
        domain = await domain_svc.verify_domain(
            db, domain, body.token, actor=make_actor(request, user, "tenant")
        )
    except AppError as exc:
        # A failed verify increments verify_attempts (and flips to 'failed' on
        # the 3rd) but the service raises before the endpoint's commit — without
        # this the increment rolls back and MAX_VERIFY_ATTEMPTS never persists
        # (attempts reset every request). Persist the counter, then re-raise.
        if exc.code == "DOMAIN_VERIFY_FAILED":
            await db.commit()
        raise
    await db.commit()
    return DataResponse(data=_domain_response(domain))


@router.post(
    "/tenants/{tenant_id}/domains/{domain_id}/activate",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def activate_domain(
    tenant_id: str,
    domain_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    from app.controlplane import facade

    await facade.require_feature(db, tenant, "custom_domain")
    domain = await _tenant_domain(db, tenant_id, domain_id)
    domain = await domain_svc.activate_domain(db, domain, actor=make_actor(request, user, "tenant"))
    await db.commit()
    return DataResponse(data=_domain_response(domain))


@router.post(
    "/tenants/{tenant_id}/domains/{domain_id}/disable",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def disable_domain(
    tenant_id: str,
    domain_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    domain = await _tenant_domain(db, tenant_id, domain_id)
    domain = await domain_svc.disable_domain(db, domain, actor=make_actor(request, user, "tenant"))
    await db.commit()
    return DataResponse(data=_domain_response(domain))


@router.delete(
    "/tenants/{tenant_id}/domains/{domain_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_domain(
    tenant_id: str,
    domain_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    domain = await _tenant_domain(db, tenant_id, domain_id)
    hostname = domain.hostname
    await db.delete(domain)  # frees the hostname
    # R60[45]: the hard delete frees the hostname for ANY tenant to register —
    # the only domain transition that wasn't audited.
    await record_audit(
        db,
        actor=make_actor(request, user, "tenant"),
        action="domain.deleted",
        target_type="domain",
        target_id=domain_id,
        tenant_id=tenant_id,
        before={"hostname": hostname},
    )
    await db.commit()


# ── Public site-context (white-label resolution) ─────────────


# R83[M4]: 60/min keyed by client IP throttled the SINGLE Next.js server IP
# that proxies ALL end-user traffic for every white-label host — one busy
# tenant's cache-miss burst dark-branded every other tenant for the window.
# The endpoint is a cheap indexed point-read served through the frontend's
# 300s revalidate cache; 600/min absorbs multi-tenant cache-miss bursts.
@router.get("/public/site-context", dependencies=[Depends(rate_limit(600, 60))])
async def site_context(
    host: str = Query(min_length=1, max_length=253),
    db: AsyncSession = Depends(get_db),
):
    """Explicit host parameter — the backend never consumes the Host header
    for tenant resolution (issue §39 host-poisoning defense)."""
    return DataResponse(data=await domain_svc.resolve_site_context(db, host))


# ── Blueprints ───────────────────────────────────────────────


@router.get("/platform/blueprints", dependencies=[Depends(rate_limit(30, 60))])
async def list_blueprints(
    user: User = Depends(require_platform_role(*_BILLING_ROLES, "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        (await db.execute(select(TenantBlueprint).order_by(TenantBlueprint.created_at.desc())))
        .scalars()
        .all()
    )
    data = [
        {
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "partner_id": b.partner_id,
            "is_active": b.is_active,
            "config": b.config,
        }
        for b in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post("/platform/blueprints", status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_blueprint(
    body: CreateBlueprintRequest,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    config = provision_svc.validate_blueprint_config(body.config)
    blueprint = TenantBlueprint(
        name=body.name, description=body.description, config=config, created_by=user.id
    )
    db.add(blueprint)
    await db.commit()
    return DataResponse(data={"id": blueprint.id, "name": blueprint.name})


@router.get("/partners/{partner_id}/blueprints", dependencies=[Depends(rate_limit(30, 60))])
async def partner_blueprints(
    partner_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.api.partners import require_partner_member

    await require_partner_member(db, partner_id, user)
    rows = (
        (
            await db.execute(
                select(TenantBlueprint).where(
                    (TenantBlueprint.partner_id == partner_id)
                    | (TenantBlueprint.partner_id.is_(None))
                )
            )
        )
        .scalars()
        .all()
    )
    data = [
        {"id": b.id, "name": b.name, "description": b.description, "is_active": b.is_active}
        for b in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


@router.post(
    "/partners/{partner_id}/blueprints",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_partner_blueprint(
    partner_id: str,
    body: CreateBlueprintRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.api.partners import require_partner_member

    await require_partner_member(db, partner_id, user, "admin")
    config = provision_svc.validate_blueprint_config(body.config)
    # R46[25]: entitlement overrides are a PLATFORM power (PUT /platform/
    # tenants/{id}/entitlements requires platform_admin). A partner admin
    # authoring them into a blueprint and provisioning it escalated arbitrary
    # hard overrides (unlimited seats/orgs/AI budget) with no platform review.
    if config.get("entitlement_overrides"):
        raise AppError(
            "BLUEPRINT_INVALID",
            "Partner blueprints cannot set entitlement overrides — "
            "contact the platform to configure plan entitlements",
            422,
        )
    # Partner blueprints may only reference publicly installable packs —
    # smuggling another tenant's private content is rejected at provision
    # time by the install gates anyway (defense in depth).
    blueprint = TenantBlueprint(
        name=body.name,
        description=body.description,
        partner_id=partner_id,
        config=config,
        created_by=user.id,
    )
    db.add(blueprint)
    await db.commit()
    return DataResponse(data={"id": blueprint.id, "name": blueprint.name})


# ── Provisioning ─────────────────────────────────────────────


@router.post(
    "/platform/provision-runs",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def platform_provision(
    body: ProvisionRequest,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    blueprint = await db.get(TenantBlueprint, body.blueprint_id)
    if blueprint is None:
        raise AppError("BLUEPRINT_INVALID", "Blueprint not found", 404)
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=body.blueprint_id,
        name=body.name,
        slug=body.slug,
        idempotency_key=body.idempotency_key,
        partner_id=blueprint.partner_id,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(data=_run_response(run))


@router.post(
    "/partners/{partner_id}/provision-runs",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def partner_provision(
    partner_id: str,
    body: ProvisionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.api.partners import require_partner_member
    from app.controlplane.models.partner import Partner

    await require_partner_member(db, partner_id, user, "admin")
    # R46[27]: a suspended/terminated partner must not provision new attributed
    # tenants — membership alone never checked partner.status.
    partner = await db.get(Partner, partner_id)
    if partner is None or partner.status != "active":
        raise AppError(
            "PARTNER_FORBIDDEN",
            "Partner account is not active",
            403,
        )
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=body.blueprint_id,
        name=body.name,
        slug=body.slug,
        idempotency_key=body.idempotency_key,
        partner_id=partner_id,
        actor=make_actor(request, user, "partner"),
    )
    await db.commit()
    return DataResponse(data=_run_response(run))


@router.get("/platform/provision-runs/{run_id}", dependencies=[Depends(rate_limit(60, 60))])
async def get_provision_run(
    run_id: str,
    user: User = Depends(require_platform_role(*_BILLING_ROLES, "platform_support")),
    db: AsyncSession = Depends(get_db),
):
    run = await db.get(TenantProvisionRun, run_id)
    if run is None:
        raise AppError("PROVISION_RUN_NOT_FOUND", "Provision run not found", 404)
    return DataResponse(data=_run_response(run))


@router.get(
    "/partners/{partner_id}/provision-runs/{run_id}",
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_partner_provision_run(
    partner_id: str,
    run_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.api.partners import require_partner_member

    await require_partner_member(db, partner_id, user)
    run = await db.get(TenantProvisionRun, run_id)
    if run is None or run.partner_id != partner_id:
        raise AppError("PROVISION_RUN_NOT_FOUND", "Provision run not found", 404)
    return DataResponse(data=_run_response(run))


@router.post(
    "/platform/provision-runs/{run_id}/retry",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def retry_provision_run(
    run_id: str,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.models.outbox import enqueue

    run = await db.get(TenantProvisionRun, run_id)
    if run is None:
        raise AppError("PROVISION_RUN_NOT_FOUND", "Provision run not found", 404)
    if run.status != "failed":
        raise AppError("PROVISION_CONFLICT", "Only failed runs can be retried", 409)
    enqueue(db, "provision.run", {"run_id": run.id})
    await db.commit()
    return DataResponse(data={"id": run.id, "requeued": True})


# ── Exports ──────────────────────────────────────────────────


@router.post(
    "/platform/tenants/{tenant_id}/exports",
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def create_export(
    tenant_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    export = await provision_svc.build_export(db, tenant_id, actor=make_actor(request, user))
    await db.commit()
    return DataResponse(data={"id": export.id, "status": export.status, "error": export.error})


@router.get(
    "/platform/tenants/{tenant_id}/exports/{export_id}",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_export(
    tenant_id: str,
    export_id: str,
    request: Request,
    user: User = Depends(require_platform_role("platform_admin")),
    db: AsyncSession = Depends(get_db),
):
    export = await db.get(TenantExport, export_id)
    if export is None or export.tenant_id != tenant_id:
        raise AppError("EXPORT_NOT_READY", "Export not found", 404)
    download_url = None
    if export.status == "completed" and export.file_key:
        from app.config import settings as app_settings
        from app.core.storage import get_s3_client

        async for client in get_s3_client():
            download_url = await client.generate_presigned_url(
                "get_object",
                # R65[23]: exports live in the dedicated private bucket.
                Params={"Bucket": app_settings.s3_export_bucket, "Key": export.file_key},
                ExpiresIn=900,
            )
        # R85[M7]: only export CREATION was audited — every presign mint
        # (each a fresh 15-min URL to the full PII bundle) was invisible.
        # WHO pulled a tenant's data and WHEN must be reconstructible.
        await record_audit(
            db,
            actor=make_actor(request, user),
            action="tenant.export_downloaded",
            target_type="tenant_export",
            target_id=export.id,
            tenant_id=tenant_id,
        )
        await db.commit()
    return DataResponse(
        data={"id": export.id, "status": export.status, "download_url": download_url}
    )
