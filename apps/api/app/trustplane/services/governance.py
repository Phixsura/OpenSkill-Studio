"""Governance Templates, Compliance Reporting & Tenant Policies service (ADR-017 Parts L, M, N)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.governance import (
    ComplianceReport,
    GovernanceTemplate,
    PolicyOverrideType,
    ReportStatus,
    ReportType,
    TemplateScope,
    TemplateStatus,
    TenantPolicyOverride,
)
from app.trustplane.services.audit import record_trust_audit

# ── Errors ───────────────────────────────────────────────────────────


class TemplateNotFoundError(AppError):
    def __init__(self):
        super().__init__("TEMPLATE_NOT_FOUND", "Governance template not found", 404)


class ReportNotFoundError(AppError):
    def __init__(self):
        super().__init__("REPORT_NOT_FOUND", "Compliance report not found", 404)


class PolicyOverrideNotFoundError(AppError):
    def __init__(self):
        super().__init__("POLICY_OVERRIDE_NOT_FOUND", "Tenant policy override not found", 404)


# ── Governance Templates ─────────────────────────────────────────────


async def create_template(
    db: AsyncSession,
    org_id: str | None,
    user_id: str,
    *,
    name: str,
    scope: str,
    config: dict,
    scope_value: str | None = None,
    description: str | None = None,
    parent_template_id: str | None = None,
    is_restrictive: bool = False,
) -> GovernanceTemplate:
    # Validate parent template belongs to same org or platform (IDOR guard)
    if parent_template_id and org_id:
        await get_template(db, parent_template_id, org_id)

    template = GovernanceTemplate(
        org_id=org_id,
        name=name,
        description=description,
        scope=TemplateScope(scope),
        scope_value=scope_value,
        status=TemplateStatus.DRAFT,
        config=config,
        parent_template_id=parent_template_id,
        is_restrictive=is_restrictive,
        created_by=user_id,
    )
    db.add(template)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id or "__platform__",
        actor_user_id=user_id,
        actor_type="user",
        action="template.created",
        target_type="governance_template",
        target_id=template.id,
        after={"name": name, "scope": scope},
    )
    return template


async def get_template(db: AsyncSession, template_id: str, org_id: str) -> GovernanceTemplate:
    result = await db.execute(
        select(GovernanceTemplate).where(
            GovernanceTemplate.id == template_id,
            (GovernanceTemplate.org_id == org_id) | (GovernanceTemplate.org_id.is_(None)),
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise TemplateNotFoundError()
    return template


async def list_templates(
    db: AsyncSession,
    org_id: str,
    *,
    scope: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[GovernanceTemplate], int]:
    base = select(GovernanceTemplate).where(
        (GovernanceTemplate.org_id == org_id) | (GovernanceTemplate.org_id.is_(None))
    )
    count_base = select(func.count()).select_from(GovernanceTemplate).where(
        (GovernanceTemplate.org_id == org_id) | (GovernanceTemplate.org_id.is_(None))
    )

    if scope:
        base = base.where(GovernanceTemplate.scope == scope)
        count_base = count_base.where(GovernanceTemplate.scope == scope)
    if status:
        base = base.where(GovernanceTemplate.status == status)
        count_base = count_base.where(GovernanceTemplate.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(GovernanceTemplate.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def activate_template(
    db: AsyncSession,
    template_id: str,
    org_id: str,
    user_id: str,
) -> GovernanceTemplate:
    result = await db.execute(
        select(GovernanceTemplate).where(
            GovernanceTemplate.id == template_id,
            GovernanceTemplate.org_id == org_id,
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise TemplateNotFoundError()

    template.status = TemplateStatus.ACTIVE
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="template.activated",
        target_type="governance_template",
        target_id=template_id,
    )
    return template


# ── Compliance Reports ───────────────────────────────────────────────


async def create_report(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    report_type: str,
    title: str,
    description: str | None = None,
    filters: dict | None = None,
) -> ComplianceReport:
    report = ComplianceReport(
        org_id=org_id,
        report_type=ReportType(report_type),
        status=ReportStatus.GENERATING,
        title=title,
        description=description,
        filters=filters,
        generated_by=user_id,
    )
    db.add(report)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="report.created",
        target_type="compliance_report",
        target_id=report.id,
        after={"report_type": report_type, "title": title},
    )
    return report


async def complete_report(
    db: AsyncSession,
    report_id: str,
    org_id: str,
    *,
    content: dict,
    system_count: int | None = None,
    finding_count: int | None = None,
) -> ComplianceReport:
    result = await db.execute(
        select(ComplianceReport).where(
            ComplianceReport.id == report_id, ComplianceReport.org_id == org_id
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise ReportNotFoundError()

    report.status = ReportStatus.COMPLETED
    report.content = content
    report.system_count = system_count
    report.finding_count = finding_count
    report.generated_at = datetime.now(UTC)
    await db.flush()
    return report


async def get_report(db: AsyncSession, report_id: str, org_id: str) -> ComplianceReport:
    result = await db.execute(
        select(ComplianceReport).where(
            ComplianceReport.id == report_id, ComplianceReport.org_id == org_id
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise ReportNotFoundError()
    return report


async def list_reports(
    db: AsyncSession,
    org_id: str,
    *,
    report_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ComplianceReport], int]:
    base = select(ComplianceReport).where(ComplianceReport.org_id == org_id)
    count_base = (
        select(func.count()).select_from(ComplianceReport).where(ComplianceReport.org_id == org_id)
    )

    if report_type:
        base = base.where(ComplianceReport.report_type == report_type)
        count_base = count_base.where(ComplianceReport.report_type == report_type)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(ComplianceReport.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Tenant Policy Overrides ─────────────────────────────────────────


async def create_policy_override(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    override_type: str,
    name: str,
    config: dict,
    description: str | None = None,
    template_id: str | None = None,
) -> TenantPolicyOverride:
    # Validate referenced template belongs to same org or platform (IDOR guard)
    if template_id:
        await get_template(db, template_id, org_id)

    override = TenantPolicyOverride(
        org_id=org_id,
        override_type=PolicyOverrideType(override_type),
        name=name,
        description=description,
        config=config,
        template_id=template_id,
        created_by=user_id,
    )
    db.add(override)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="tenant_policy.created",
        target_type="tenant_policy_override",
        target_id=override.id,
        after={"override_type": override_type, "name": name},
    )
    return override


async def list_policy_overrides(
    db: AsyncSession,
    org_id: str,
    *,
    override_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TenantPolicyOverride], int]:
    base = select(TenantPolicyOverride).where(TenantPolicyOverride.org_id == org_id)
    count_base = (
        select(func.count())
        .select_from(TenantPolicyOverride)
        .where(TenantPolicyOverride.org_id == org_id)
    )

    if override_type:
        base = base.where(TenantPolicyOverride.override_type == override_type)
        count_base = count_base.where(TenantPolicyOverride.override_type == override_type)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(TenantPolicyOverride.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_policy_override(
    db: AsyncSession, override_id: str, org_id: str
) -> TenantPolicyOverride:
    result = await db.execute(
        select(TenantPolicyOverride).where(
            TenantPolicyOverride.id == override_id,
            TenantPolicyOverride.org_id == org_id,
        )
    )
    override = result.scalar_one_or_none()
    if override is None:
        raise PolicyOverrideNotFoundError()
    return override
