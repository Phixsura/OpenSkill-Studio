"""Blueprint provisioning step machine + tenant export (ADR-014 §10.3–10.4).

The BlueprintConfig schema (extra=forbid) STRUCTURALLY cannot carry users,
progress, submissions, credentials, or billing records — issue §8 red line.

ADR exception: provisioning is an ORCHESTRATOR and may import a whitelist of
product services {OrgService, InstallationService, WorkflowInstallationService}
— the only place control-plane code calls product services.
"""

import json
from datetime import UTC, datetime

import structlog
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.branding import TenantBlueprint, TenantExport, TenantProvisionRun
from app.controlplane.models.outbox import enqueue
from app.controlplane.models.tenant import TenantAccount, TenantAccountType, TenantStatus
from app.controlplane.services.audit import SYSTEM_ACTOR, Actor, record_audit
from app.controlplane.worker import register_handler
from app.exceptions import AppError

log = structlog.get_logger()


# ── Strict blueprint config schema ───────────────────────────


class BlueprintPackRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pack_id: str = Field(min_length=26, max_length=26)
    version: str = Field(default="latest", max_length=50)


class BlueprintBranding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_display_name: str | None = Field(default=None, max_length=100)
    theme_tokens: dict = Field(default_factory=dict)
    login_tagline: str | None = Field(default=None, max_length=200)


class BlueprintOrg(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name_template: str = Field(default="{tenant_name}", max_length=200)


class BlueprintConfig(BaseModel):
    """extra=forbid everywhere: users/progress/credentials/billing keys are
    structurally impossible."""

    model_config = ConfigDict(extra="forbid")
    plan_key: str | None = Field(default=None, max_length=50)
    entitlement_overrides: dict = Field(default_factory=dict)
    branding: BlueprintBranding | None = None
    org: BlueprintOrg = Field(default_factory=BlueprintOrg)
    skill_packs: list[BlueprintPackRef] = Field(default_factory=list, max_length=20)
    workflow_packs: list[BlueprintPackRef] = Field(default_factory=list, max_length=20)
    feature_settings: dict = Field(default_factory=dict)


def validate_blueprint_config(config: dict) -> dict:
    from app.controlplane.services.branding import validate_theme_tokens
    from app.controlplane.services.entitlements import validate_entitlement_value

    parsed = BlueprintConfig.model_validate(config)
    for key, value in parsed.entitlement_overrides.items():
        validate_entitlement_value(key, value)
    if parsed.branding is not None:
        validate_theme_tokens(parsed.branding.theme_tokens)
    return parsed.model_dump()


# ── Step machine ─────────────────────────────────────────────

STEPS = [
    "snapshot_config",
    "create_tenant",
    "create_org",
    "apply_branding",
    "apply_entitlement_overrides",
    "create_subscription",
    "install_skill_packs",
    "install_workflow_packs",
    "finalize",
]


def _step_done(run: TenantProvisionRun, step: str) -> bool:
    return any(s.get("step") == step and s.get("status") == "done" for s in run.steps)


def _mark(run: TenantProvisionRun, step: str, status: str, error: str | None = None, **extra):
    steps = list(run.steps)
    steps.append(
        {
            "step": step,
            "status": status,
            "error": error,
            "at": datetime.now(UTC).isoformat(),
            **extra,
        }
    )
    run.steps = steps


async def create_provision_run(
    db: AsyncSession,
    *,
    blueprint_id: str,
    name: str,
    slug: str,
    idempotency_key: str,
    partner_id: str | None,
    actor: Actor,
) -> TenantProvisionRun:
    existing = (
        await db.execute(
            select(TenantProvisionRun).where(TenantProvisionRun.idempotency_key == idempotency_key)
        )
    ).scalar_one_or_none()
    if existing is not None:
        # R72[3]: the divergence guard must compare EVERY requested parameter.
        # Ignoring requested_slug silently swallowed an operator's corrected
        # slug on retry (the old run resumed with the colliding slug), and
        # ignoring partner_id let a different partner reusing the same key
        # read another partner's run (cross-partner disclosure — the key is
        # globally unique, not partner-scoped).
        if (
            existing.requested_name != name
            or existing.blueprint_id != blueprint_id
            or existing.requested_slug != slug
            or existing.partner_id != partner_id
        ):
            raise AppError(
                "PROVISION_CONFLICT",
                "This idempotency key was used with different parameters",
                409,
            )
        return existing  # idempotent replay returns the run
    blueprint = await db.get(TenantBlueprint, blueprint_id)
    if blueprint is None or not blueprint.is_active:
        raise AppError("BLUEPRINT_INVALID", "Blueprint not found or inactive", 404)
    if blueprint.partner_id is not None and blueprint.partner_id != partner_id:
        # Partner blueprints are usable only by that partner (platform bypasses
        # by passing the blueprint's own partner)
        raise AppError("BLUEPRINT_INVALID", "Blueprint not found or inactive", 404)
    run = TenantProvisionRun(
        blueprint_id=blueprint_id,
        requested_name=name,
        requested_slug=slug,
        partner_id=partner_id,
        idempotency_key=idempotency_key,
        created_by=actor.user_id,
    )
    db.add(run)
    await db.flush()
    enqueue(db, "provision.run", {"run_id": run.id})
    return run


async def execute_provision_run(db: AsyncSession, run_id: str) -> None:
    """Resumable: completed steps are skipped; a failure marks the run failed
    (retry re-enqueues and resumes from the failed step)."""
    run = await db.get(TenantProvisionRun, run_id)
    if run is None or run.status == "completed":
        return
    result = await db.execute(
        update(TenantProvisionRun)
        .where(
            TenantProvisionRun.id == run_id,
            TenantProvisionRun.status.in_(["pending", "failed", "running"]),
        )
        .values(status="running", error=None)
    )
    if not result.rowcount:
        return
    await db.refresh(run)
    blueprint = await db.get(TenantBlueprint, run.blueprint_id)
    creator = run.created_by

    try:
        # 0. snapshot config (consistency across blueprint edits mid-run)
        if not _step_done(run, "snapshot_config"):
            config = validate_blueprint_config(blueprint.config if blueprint else {})
            _mark(run, "snapshot_config", "done", config=config)
            await db.flush()
        config = next(s["config"] for s in run.steps if s["step"] == "snapshot_config")

        # 1. tenant (ACTIVE — blueprint provisioning is a commercial act, ADR)
        if not _step_done(run, "create_tenant"):
            from app.controlplane.services.tenants import create_tenant

            tenant = await create_tenant(
                db,
                name=run.requested_name,
                slug=run.requested_slug,
                actor=SYSTEM_ACTOR,
                status=TenantStatus.ACTIVE,
                with_trial=False,
                account_type=(
                    TenantAccountType.PARTNER_MANAGED
                    if run.partner_id
                    else TenantAccountType.DIRECT
                ),
                partner_id=run.partner_id,
                owner_user_id=creator,
            )
            run.tenant_id = tenant.id
            _mark(run, "create_tenant", "done", tenant_id=tenant.id)
            await db.flush()
        tenant = await db.get(TenantAccount, run.tenant_id)

        # 2. org
        org_id = next((s.get("org_id") for s in run.steps if s["step"] == "create_org"), None)
        if not _step_done(run, "create_org"):
            from sqlalchemy import select as _select
            from ulid import ULID as _ULID

            from app.models.organization import Organization as _Org
            from app.services.organization import OrgService

            org_name = config["org"]["name_template"].replace("{tenant_name}", run.requested_name)[
                :100
            ]
            # R46[26]: Organization.slug is GLOBALLY unique, and the operator's
            # requested_slug can collide with any existing org — the verbatim
            # insert died on the unique index with no fallback, wedging the run.
            # Probe and suffix (same -tXXXX pattern as tenant auto-create).
            org_slug = run.requested_slug[:100]
            for _attempt in range(3):
                taken = (
                    await db.execute(_select(_Org.id).where(_Org.slug == org_slug).limit(1))
                ).scalar_one_or_none()
                if taken is None:
                    break
                org_slug = f"{run.requested_slug[:92]}-{str(_ULID()).lower()[-4:]}"
            org = await OrgService(db).create(
                name=org_name,
                slug=org_slug,
                description=None,
                created_by=creator,
                tenant_id=tenant.id,
            )
            org_id = org.id
            _mark(run, "create_org", "done", org_id=org.id)
            await db.flush()

        # 3. branding
        if not _step_done(run, "apply_branding"):
            if config.get("branding"):
                from app.controlplane.models.branding import TenantBranding

                db.add(
                    TenantBranding(
                        tenant_id=tenant.id,
                        product_display_name=config["branding"].get("product_display_name"),
                        theme_tokens=config["branding"].get("theme_tokens", {}),
                        login_tagline=config["branding"].get("login_tagline"),
                    )
                )
            _mark(run, "apply_branding", "done")
            await db.flush()

        # 4. entitlement overrides
        if not _step_done(run, "apply_entitlement_overrides"):
            from app.controlplane.services.plans import set_override

            for key, value in (config.get("entitlement_overrides") or {}).items():
                await set_override(
                    db,
                    tenant.id,
                    key,
                    value=value,
                    enforcement="hard",
                    expires_at=None,
                    reason="blueprint provisioning",
                    actor=SYSTEM_ACTOR,
                )
            _mark(run, "apply_entitlement_overrides", "done")
            await db.flush()

        # 5. subscription (manual provider, immediate active)
        if not _step_done(run, "create_subscription"):
            if config.get("plan_key"):
                from app.controlplane.services.billing import start_subscription

                await start_subscription(
                    db,
                    tenant,
                    plan_key=config["plan_key"],
                    interval="month",
                    seats=0,
                    provider="manual",
                    actor=SYSTEM_ACTOR,
                )
            _mark(run, "create_subscription", "done")
            await db.flush()

        # 6-7. content installs (ADR-approved product-service imports)
        if not _step_done(run, "install_skill_packs"):
            from app.services.installation import InstallationService

            for ref in config.get("skill_packs", []):
                version = None if ref["version"] == "latest" else ref["version"]
                try:
                    # R46[28]: each pack install runs in a SAVEPOINT so a
                    # mid-copy failure rolls back THAT pack's partial content
                    # (categories/skills already flushed) instead of committing
                    # it — the retry then re-installs cleanly rather than
                    # duplicating the committed half.
                    async with db.begin_nested():
                        await InstallationService(db).install_pack(
                            org_id, ref["pack_id"], version, creator
                        )
                except AppError as exc:
                    # Resume-safe: this step has no per-pack progress marker, so
                    # a retry re-runs the whole loop. Packs installed before an
                    # earlier failure are already committed → treat their
                    # ALREADY_INSTALLED as success, else resume never completes.
                    if exc.code == "ALREADY_INSTALLED":
                        continue
                    raise AppError(
                        "BLUEPRINT_PACK_UNAVAILABLE",
                        f"Skill pack {ref['pack_id']} not installable: {exc.message}",
                        422,
                    ) from exc
            _mark(run, "install_skill_packs", "done")
            await db.flush()

        if not _step_done(run, "install_workflow_packs"):
            from app.services.workflow_installation import WorkflowInstallationService

            for ref in config.get("workflow_packs", []):
                version = None if ref["version"] == "latest" else ref["version"]
                try:
                    async with db.begin_nested():  # R46[28] — see skill packs
                        await WorkflowInstallationService(db).install(
                            org_id, ref["pack_id"], version, creator
                        )
                except AppError as exc:
                    if exc.code == "ALREADY_INSTALLED":
                        continue  # resume-safe (see install_skill_packs above)
                    raise AppError(
                        "BLUEPRINT_PACK_UNAVAILABLE",
                        f"Workflow pack {ref['pack_id']} not installable: {exc.message}",
                        422,
                    ) from exc
            _mark(run, "install_workflow_packs", "done")
            await db.flush()

        # 8. finalize
        if not _step_done(run, "finalize"):
            _mark(run, "finalize", "done")
        run.status = "completed"
        await record_audit(
            db,
            actor=SYSTEM_ACTOR,
            action="tenant.provisioned",
            target_type="tenant",
            target_id=tenant.id,
            tenant_id=tenant.id,
            partner_id=run.partner_id,
            after={"run_id": run.id, "blueprint_id": run.blueprint_id},
        )
        await db.flush()
    except Exception as exc:  # noqa: BLE001 — failure is a resumable state
        failed_step = next((s for s in STEPS if not _step_done(run, s)), "unknown")
        _mark(run, failed_step, "failed", error=str(exc)[:500])
        run.status = "failed"
        run.error = str(exc)[:2000]
        await db.flush()
        log.error("cp_provision_failed", run_id=run.id, step=failed_step, error=str(exc))


@register_handler("provision.run")
async def _handle_provision(db: AsyncSession, payload: dict) -> None:
    await execute_provision_run(db, payload["run_id"])


# ── Tenant export (ADR-014 §10.4) ────────────────────────────

EXPORT_SCHEMA_VERSION = 1
# R85[6]: per-collection row cap — an export must never OOM the API process.
EXPORT_MAX_ROWS = 50_000


async def build_export(db: AsyncSession, tenant_id: str, *, actor: Actor) -> TenantExport:
    """Whitelist-constructed JSON bundle → S3. Structurally excluded:
    credentials, cost rates, rated internal-cost fields, other tenants' rows,
    token hashes, platform-only audit actions. No SELECT * anywhere."""
    # R65[21]: snapshot-consistent reads — the bundle is assembled across many
    # queries; under READ COMMITTED a concurrent invoice finalize/credit write
    # produced an internally torn export (e.g. an invoice whose lines were read
    # after a void). REPEATABLE READ pins one snapshot for the whole build.
    # SET TRANSACTION must be the FIRST statement of a transaction, and the
    # endpoint's auth dependency has already queried — commit to close the
    # current tx, then upgrade the fresh one.
    from sqlalchemy import text as _text

    await db.commit()
    await db.execute(_text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    export = TenantExport(tenant_id=tenant_id, requested_by=actor.user_id)
    db.add(export)
    await db.flush()

    from sqlalchemy import func as _f

    from app.controlplane.models.billing import Invoice, InvoiceLine, Subscription
    from app.controlplane.models.branding import TenantBranding, TenantDomain
    from app.controlplane.models.credit import CreditLedgerEntry
    from app.controlplane.models.marketplace import LicenseGrant
    from app.controlplane.models.usage import UsageEvent
    from app.models.organization import MemberStatus, Organization, OrgMember
    from app.models.user import User

    bundle: dict = {
        "export_schema": EXPORT_SCHEMA_VERSION,
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "status": tenant.status.value,
            "currency": tenant.currency,
            "timezone": tenant.timezone,
            "created_at": tenant.created_at.isoformat(),
        },
    }
    orgs = (
        (await db.execute(select(Organization).where(Organization.tenant_id == tenant_id)))
        .scalars()
        .all()
    )
    bundle["organizations"] = []
    for org in orgs:
        members = (
            await db.execute(
                select(OrgMember.role, User.email, User.display_name)
                .join(User, User.id == OrgMember.user_id)
                .where(OrgMember.org_id == org.id, OrgMember.status == MemberStatus.ACTIVE)
            )
        ).all()
        bundle["organizations"].append(
            {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "status": org.status.value,
                "members": [
                    {"email": email, "display_name": name, "role": role.value}
                    for role, email, name in members
                ],
            }
        )
    sub = (
        await db.execute(
            select(Subscription).where(
                Subscription.tenant_id == tenant_id, Subscription.status != "cancelled"
            )
        )
    ).scalar_one_or_none()
    bundle["subscription"] = (
        {
            "status": sub.status,
            "interval": sub.interval,
            "currency": sub.currency,
            "current_period_end": sub.current_period_end.isoformat(),
        }
        if sub
        else None
    )
    # R85[6]: was one SELECT per invoice for its lines (100k invoices = 100k
    # sequential round-trips inside one HTTP request holding a REPEATABLE
    # READ tx) and every collection unbounded in RAM. One LEFT-JOINed query,
    # ordered, with a hard row cap per collection; a truncated export says so
    # in the bundle instead of OOMing the API process.
    truncated: list[str] = []
    inv_rows = (
        await db.execute(
            select(Invoice, InvoiceLine)
            .outerjoin(InvoiceLine, InvoiceLine.invoice_id == Invoice.id)
            .where(Invoice.tenant_id == tenant_id)
            .order_by(Invoice.created_at, Invoice.id, InvoiceLine.sort_order)
            .limit(EXPORT_MAX_ROWS)
        )
    ).all()
    if len(inv_rows) >= EXPORT_MAX_ROWS:
        truncated.append("invoices")
    bundle["invoices"] = []
    _by_inv: dict = {}
    for invoice, line in inv_rows:
        entry = _by_inv.get(invoice.id)
        if entry is None:
            entry = {
                "number": invoice.number,
                "status": invoice.status,
                "currency": invoice.currency,
                "total_minor": invoice.total_minor,
                "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
                "lines": [],
            }
            _by_inv[invoice.id] = entry
            bundle["invoices"].append(entry)
        if line is not None:
            entry["lines"].append(
                {
                    "type": line.line_type,
                    "description": line.description,
                    "amount_minor": line.amount_minor,
                }
            )
    ledger = (
        (
            await db.execute(
                select(CreditLedgerEntry)
                .where(CreditLedgerEntry.tenant_id == tenant_id)
                .order_by(CreditLedgerEntry.created_at, CreditLedgerEntry.id)
                .limit(EXPORT_MAX_ROWS)
            )
        )
        .scalars()
        .all()
    )
    if len(ledger) >= EXPORT_MAX_ROWS:
        truncated.append("credit_ledger")
    bundle["credit_ledger"] = [
        {
            "entry_type": e.entry_type,
            "amount_minor": e.amount_minor,
            "balance_after_minor": e.balance_after_minor,
            "currency": e.currency,
            "created_at": e.created_at.isoformat(),
        }
        for e in ledger
    ]
    grants = (
        (
            await db.execute(
                select(LicenseGrant)
                .where(LicenseGrant.tenant_id == tenant_id)
                .order_by(LicenseGrant.created_at, LicenseGrant.id)
                .limit(EXPORT_MAX_ROWS)
            )
        )
        .scalars()
        .all()
    )
    if len(grants) >= EXPORT_MAX_ROWS:
        truncated.append("licenses")
    bundle["licenses"] = [
        {
            "product_type": g.product_type,
            "product_id": g.product_id,
            "scope": g.scope,
            "status": g.status,
            "source": g.source,
        }
        for g in grants
    ]
    usage = (
        await db.execute(
            select(
                UsageEvent.usage_type,
                _f.to_char(UsageEvent.occurred_at, "YYYY-MM").label("month"),
                _f.sum(UsageEvent.quantity).label("quantity"),
            )
            .where(UsageEvent.tenant_id == tenant_id)
            .group_by(UsageEvent.usage_type, "month")
        )
    ).all()
    bundle["usage_monthly"] = [
        {"usage_type": u.usage_type, "month": u.month, "quantity": str(u.quantity)} for u in usage
    ]
    branding = (
        await db.execute(select(TenantBranding).where(TenantBranding.tenant_id == tenant_id))
    ).scalar_one_or_none()
    bundle["branding"] = (
        {
            "product_display_name": branding.product_display_name,
            "theme_tokens": branding.theme_tokens,
            "logo_key": branding.logo_key,
        }
        if branding
        else None
    )
    domains = (
        (await db.execute(select(TenantDomain).where(TenantDomain.tenant_id == tenant_id)))
        .scalars()
        .all()
    )
    bundle["domains"] = [{"hostname": d.hostname, "status": d.status} for d in domains]
    if truncated:
        bundle["truncated_collections"] = truncated

    # Upload to S3
    try:
        from app.config import settings as app_settings
        from app.core.storage import get_s3_client

        file_key = f"exports/{tenant_id}/{export.id}.json"
        async for client in get_s3_client():
            # R65[23]: dedicated PRIVATE bucket — the shared s3_bucket also
            # serves portfolio covers via unsigned direct URLs, so a guessable
            # key prefix on the same bucket policy risked exposing PII bundles.
            try:
                await client.head_bucket(Bucket=app_settings.s3_export_bucket)
            except Exception:  # noqa: BLE001 — first use creates it
                await client.create_bucket(Bucket=app_settings.s3_export_bucket)
            await client.put_object(
                Bucket=app_settings.s3_export_bucket,
                Key=file_key,
                Body=json.dumps(bundle, ensure_ascii=False).encode(),
                ContentType="application/json",
            )
        export.file_key = file_key
        export.status = "completed"
        export.completed_at = datetime.now(UTC)
    except Exception as exc:  # noqa: BLE001
        export.status = "failed"
        export.error = str(exc)[:2000]
    await record_audit(
        db,
        actor=actor,
        action="tenant.export_created",
        target_type="tenant",
        target_id=tenant_id,
        tenant_id=tenant_id,
        after={"export_id": export.id, "status": export.status},
    )
    await db.flush()
    return export
