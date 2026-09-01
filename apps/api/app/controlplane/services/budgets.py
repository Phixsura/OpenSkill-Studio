"""Budget policies + multi-scope enforcement (ADR-014 §5.4).

ALL matching active policies are enforced (defense in layers — not
most-specific-only). Spent amounts come from RatedUsage billable sums.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.credit import BudgetPolicy
from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.models.usage import UsageEvent
from app.exceptions import AppError

log = structlog.get_logger()


@dataclass
class BudgetDecision:
    allowed: bool = True
    warnings: list[dict] = field(default_factory=list)


def _period_start(period: str, tz_name: str) -> datetime:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:  # noqa: BLE001 — bad tz falls back to UTC
        tz = UTC
    now_local = datetime.now(tz)
    if period == "daily":
        start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # monthly
        start = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(UTC)


def policy_matches(
    policy: BudgetPolicy,
    *,
    org_id: str | None,
    project_id: str | None,
    cohort_id: str | None,
    user_id: str | None,
    capability: str | None,
    usage_type: str | None,
) -> bool:
    """Scope + optional narrowing match (pure logic, unit-tested)."""
    scope_ok = (
        policy.scope_type == "tenant"
        or (policy.scope_type == "org" and policy.scope_id == org_id)
        or (policy.scope_type == "project" and project_id and policy.scope_id == project_id)
        or (policy.scope_type == "cohort" and cohort_id and policy.scope_id == cohort_id)
        or (policy.scope_type == "user" and user_id and policy.scope_id == user_id)
    )
    if not scope_ok:
        return False
    if policy.capability_key is not None and policy.capability_key != capability:
        return False
    return policy.usage_type is None or policy.usage_type == usage_type


async def _spent_minor(db: AsyncSession, tenant: TenantAccount, policy: BudgetPolicy) -> int:
    start = _period_start(policy.period, tenant.timezone)
    q = (
        # R75: sum the EXACT per-event amounts and round once — summing the
        # per-event rounded integers under-counts spend (sub-half-minor events
        # rounded to 0), letting a tenant creep past the budget invisibly.
        select(func.coalesce(func.sum(RatedUsage.billable_amount_exact), 0))
        .select_from(RatedUsage)
        .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
        .where(
            RatedUsage.tenant_id == tenant.id,
            # 'settled' = paid via credit reservation; still real spend for
            # budget purposes (only voided/blocked are excluded).
            RatedUsage.status.in_(["rated", "invoiced", "settled"]),
            RatedUsage.billable_currency == policy.currency,
            RatedUsage.rated_at >= start,
        )
    )
    if policy.scope_type == "org":
        q = q.where(RatedUsage.org_id == policy.scope_id)
    elif policy.scope_type == "project":
        q = q.where(UsageEvent.project_id == policy.scope_id)
    elif policy.scope_type == "user":
        q = q.where(UsageEvent.user_id == policy.scope_id)
    # cohort scope resolves through project metadata in v1 — no direct dim on
    # usage events; enforced only when project→cohort linkage exists (ADR note)
    if policy.usage_type is not None:
        q = q.where(RatedUsage.usage_type == policy.usage_type)
    total_exact = (await db.execute(q)).scalar_one()
    return int(Decimal(total_exact or 0).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


async def check(
    db: AsyncSession,
    tenant: TenantAccount,
    org_id: str | None,
    *,
    project_id: str | None = None,
    cohort_id: str | None = None,
    user_id: str | None = None,
    capability: str | None = None,
    usage_type: str | None = None,
    projected_minor: int = 0,
) -> BudgetDecision:
    decision = BudgetDecision()
    policies = (
        (
            await db.execute(
                select(BudgetPolicy).where(
                    BudgetPolicy.tenant_id == tenant.id,
                    BudgetPolicy.is_active.is_(True),
                )
            )
        )
        .scalars()
        .all()
    )
    matched = [
        p
        for p in policies
        if policy_matches(
            p,
            org_id=org_id,
            project_id=project_id,
            cohort_id=cohort_id,
            user_id=user_id,
            capability=capability,
            usage_type=usage_type,
        )
    ]

    # Tenant entitlement ceiling: max_ai_budget_usd_month acts as an implicit
    # tenant-scope monthly policy (no BudgetPolicy row needed).
    from app.controlplane.services.entitlements import get_effective

    eff = await get_effective(db, tenant)
    ceiling = eff.get("max_ai_budget_usd_month")
    if ceiling is not None:
        # R32/C5: denominate the implicit ceiling in the TENANT's currency, not
        # a hardcoded "USD". _spent_minor filters rated rows on
        # billable_currency == policy.currency, and rating always writes rows
        # in tenant.currency — so a hardcoded "USD" policy against a non-USD
        # tenant matched ZERO spend and the ceiling never fired. The
        # entitlement is a monthly AI budget in the tenant's own currency
        # (the "usd" in the key name is a legacy label; the number is minor
        # units of tenant.currency, and the seed/backfill use USD tenants).
        from app.controlplane.models.pricing import minor_multiplier

        implicit = BudgetPolicy(
            tenant_id=tenant.id,
            scope_type="tenant",
            period="monthly",
            limit_minor=int(Decimal(str(ceiling)) * minor_multiplier(tenant.currency)),
            currency=tenant.currency,
            hard_stop=True,
            warning_threshold_pct=80,
        )
        matched.append(implicit)

    for policy in matched:
        spent = await _spent_minor(db, tenant, policy)
        projected_total = spent + projected_minor
        if projected_total > policy.limit_minor:
            if policy.hard_stop:
                raise AppError(
                    "BUDGET_EXCEEDED",
                    f"Budget exceeded ({policy.scope_type}/{policy.period}: "
                    f"{projected_total} > {policy.limit_minor} {policy.currency})",
                    429,
                )
            decision.warnings.append(
                {"policy_id": policy.id, "scope": policy.scope_type, "over": True}
            )
        elif projected_total >= policy.limit_minor * policy.warning_threshold_pct // 100:
            decision.warnings.append(
                {"policy_id": policy.id, "scope": policy.scope_type, "threshold": True}
            )
    return decision


async def upsert_from_eval_settings(
    db: AsyncSession, tenant_id: str, org_id: str, monthly_budget_usd: float | None
) -> None:
    """Write-through from PUT /orgs/{id}/settings/evaluation (issue §17 —
    ONE budget system). None removes the org-scope policy."""
    existing = (
        await db.execute(
            select(BudgetPolicy).where(
                BudgetPolicy.tenant_id == tenant_id,
                BudgetPolicy.scope_type == "org",
                BudgetPolicy.scope_id == org_id,
                BudgetPolicy.period == "monthly",
                BudgetPolicy.capability_key.is_(None),
                BudgetPolicy.usage_type.is_(None),
            )
        )
    ).scalar_one_or_none()
    if monthly_budget_usd is None:
        if existing is not None:
            await db.delete(existing)
            await db.flush()
        return
    # R63[10]/R32: denominate the policy in the TENANT's currency, not a
    # hardcoded USD with a x100 multiplier. _spent_minor filters rated rows on
    # billable_currency == policy.currency, and rating writes rows in the
    # tenant's currency — a USD policy against a EUR/JPY tenant matched ZERO
    # spend (inert) and, for zero-decimal currencies (JPY/KRW), x100 was a
    # 100x limit. The "usd" in the field name is a legacy label; the number is
    # a budget amount in the tenant's own currency.
    from app.controlplane.models.pricing import minor_multiplier

    tenant = await db.get(TenantAccount, tenant_id)
    currency = tenant.currency if tenant is not None else "USD"
    limit_minor = int(Decimal(str(monthly_budget_usd)) * minor_multiplier(currency))
    if existing is not None:
        existing.limit_minor = limit_minor
        existing.currency = currency
        existing.is_active = True
    else:
        db.add(
            BudgetPolicy(
                tenant_id=tenant_id,
                scope_type="org",
                scope_id=org_id,
                period="monthly",
                limit_minor=limit_minor,
                currency=currency,
                hard_stop=True,
                metadata_={"source": "eval_settings"},
            )
        )
    await db.flush()
