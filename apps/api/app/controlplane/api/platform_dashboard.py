"""Platform ops console: dashboard aggregates + full trace chains
(ADR-014 §11.1, issue #27 §36–37).

Trace endpoints are the §37 acceptance core: an invoice line drills down to
every RatedUsage row with frozen cost/sell/FX snapshots and the underlying
usage event refs; a settlement entry drills down to its source invoice or
marketplace purchase (economics snapshot included) and its statement.
All read-only; platform roles only — these responses DO carry internal cost
and margin, which is exactly why no tenant-facing route reuses them.
"""

import re
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.controlplane.api.deps import require_platform_role
from app.controlplane.models.billing import (
    BillingWebhookEvent,
    Invoice,
    InvoiceLine,
    Subscription,
)
from app.controlplane.models.credit import TenantCreditBalance
from app.controlplane.models.marketplace import MarketplacePurchase
from app.controlplane.models.outbox import OutboxMessage
from app.controlplane.models.partner import (
    Partner,
    RevenueShareEntry,
    SettlementStatement,
)
from app.controlplane.models.plan import PlanPrice, PlanVersion
from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.models.usage import UsageEvent
from app.exceptions import AppError

log = structlog.get_logger()

router = APIRouter(prefix="/platform", tags=["Platform Ops"])

_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

READ_ROLES = ("platform_admin", "platform_support", "billing_admin")


def _period_bounds(period: str | None) -> tuple[str, datetime, datetime]:
    """Resolve ?period=YYYY-MM (default: current UTC month) to [start, end)."""
    if period is None:
        now = datetime.now(UTC)
        period = f"{now.year:04d}-{now.month:02d}"
    if not _PERIOD_RE.match(period):
        raise AppError("VALIDATION_ERROR", "period must be YYYY-MM", 422)
    year, month = int(period[:4]), int(period[5:7])
    start = datetime(year, month, 1, tzinfo=UTC)
    end = (
        datetime(year + 1, 1, 1, tzinfo=UTC)
        if month == 12
        else datetime(year, month + 1, 1, tzinfo=UTC)
    )
    return period, start, end


# ── Dashboard ────────────────────────────────────────────────


@router.get("/dashboard")
async def platform_dashboard(
    period: str | None = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    _user=Depends(require_platform_role(*READ_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    period, start, end = _period_bounds(period)

    # Tenants by status
    tenant_rows = (
        await db.execute(
            select(TenantAccount.status, func.count(TenantAccount.id)).group_by(
                TenantAccount.status
            )
        )
    ).all()
    by_status = {status.value: count for status, count in tenant_rows}

    # MRR: active subscriptions monthly-normalized (yearly ÷ 12)
    mrr_rows = (
        await db.execute(
            select(PlanPrice.amount_minor, PlanPrice.interval)
            .select_from(Subscription)
            .join(PlanVersion, PlanVersion.id == Subscription.plan_version_id)
            .join(
                PlanPrice,
                (PlanPrice.plan_version_id == PlanVersion.id)
                & (PlanPrice.currency == Subscription.currency)
                & (PlanPrice.interval == Subscription.interval),
            )
            .where(Subscription.status.in_(("active", "past_due", "cancel_at_period_end")))
        )
    ).all()
    mrr_minor = sum(amount // 12 if interval == "year" else amount for amount, interval in mrr_rows)

    # Usage + economics by type for the period
    usage_rows = (
        await db.execute(
            select(
                RatedUsage.usage_type,
                func.sum(RatedUsage.quantity).label("quantity"),
                func.sum(RatedUsage.billable_amount_minor).label("billable"),
                func.sum(RatedUsage.internal_cost_minor).label("cost"),
                func.sum(RatedUsage.margin_minor).label("margin"),
            )
            .where(
                RatedUsage.rated_at >= start,
                RatedUsage.rated_at < end,
                RatedUsage.status != "voided",
            )
            .group_by(RatedUsage.usage_type)
            .order_by(func.sum(RatedUsage.billable_amount_minor).desc())
        )
    ).all()
    usage_by_type = [
        {
            "usage_type": r.usage_type,
            "quantity": str(r.quantity or 0),
            "billable_minor": int(r.billable or 0),
            "cost_minor": int(r.cost or 0),
            "margin_minor": int(r.margin) if r.margin is not None else None,
        }
        for r in usage_rows
    ]
    totals = {
        "billable_minor": sum(u["billable_minor"] for u in usage_by_type),
        "internal_cost_minor": sum(u["cost_minor"] for u in usage_by_type),
        "margin_minor": sum(u["margin_minor"] or 0 for u in usage_by_type),
    }

    # Attention counters
    unrated = (
        await db.execute(
            select(func.count(UsageEvent.id))
            .outerjoin(RatedUsage, RatedUsage.usage_event_id == UsageEvent.id)
            .where(RatedUsage.id.is_(None))
        )
    ).scalar_one()
    blocked = (
        await db.execute(select(func.count(RatedUsage.id)).where(RatedUsage.status == "blocked"))
    ).scalar_one()
    totals["unrated_events"] = int(unrated)
    totals["blocked_rated"] = int(blocked)

    # Credits outstanding per currency
    credit_rows = (
        await db.execute(
            select(
                TenantCreditBalance.currency,
                func.sum(TenantCreditBalance.balance_minor).label("balance"),
                func.sum(TenantCreditBalance.reserved_minor).label("reserved"),
            ).group_by(TenantCreditBalance.currency)
        )
    ).all()
    credits_outstanding = [
        {
            "currency": r.currency,
            "balance_minor": int(r.balance or 0),
            "reserved_minor": int(r.reserved or 0),
        }
        for r in credit_rows
    ]

    # Settlement liabilities: accrued/adjusted share not yet settled
    liability_rows = (
        await db.execute(
            select(
                RevenueShareEntry.currency,
                func.sum(RevenueShareEntry.share_amount_minor).label("accrued"),
            )
            .where(RevenueShareEntry.status.in_(("accrued", "adjusted", "approved")))
            .group_by(RevenueShareEntry.currency)
        )
    ).all()
    settlement_liabilities = [
        {"currency": r.currency, "accrued_minor": int(r.accrued or 0)} for r in liability_rows
    ]

    # Marketplace GMV (paid purchases in period)
    gmv = (
        await db.execute(
            select(func.coalesce(func.sum(MarketplacePurchase.amount_minor), 0)).where(
                MarketplacePurchase.status == "paid",
                MarketplacePurchase.created_at >= start,
                MarketplacePurchase.created_at < end,
            )
        )
    ).scalar_one()

    # Attention lists
    past_due_tenants = (
        await db.execute(
            select(TenantAccount.id, TenantAccount.name, TenantAccount.slug)
            .where(TenantAccount.status == TenantStatus.PAST_DUE)
            .order_by(TenantAccount.updated_at.desc())
            .limit(20)
        )
    ).all()
    suspended_tenants = (
        await db.execute(
            select(TenantAccount.id, TenantAccount.name, TenantAccount.slug)
            .where(TenantAccount.status == TenantStatus.SUSPENDED)
            .order_by(TenantAccount.updated_at.desc())
            .limit(20)
        )
    ).all()
    failed_webhooks = (
        await db.execute(
            select(func.count(BillingWebhookEvent.id)).where(BillingWebhookEvent.status == "failed")
        )
    ).scalar_one()
    dead_outbox = (
        await db.execute(
            select(func.count(OutboxMessage.id)).where(OutboxMessage.status == "failed")
        )
    ).scalar_one()

    return {
        "data": {
            "period": period,
            "tenants": {"by_status": by_status, "total": sum(by_status.values())},
            "mrr_minor": mrr_minor,
            "usage": {"by_type": usage_by_type},
            "totals": totals,
            "credits_outstanding": credits_outstanding,
            "settlement_liabilities": settlement_liabilities,
            "marketplace_gmv_minor": int(gmv),
            "attention": {
                "past_due": [
                    {"tenant_id": t.id, "name": t.name, "slug": t.slug} for t in past_due_tenants
                ],
                "suspended": [
                    {"tenant_id": t.id, "name": t.name, "slug": t.slug} for t in suspended_tenants
                ],
                "failed_webhooks": int(failed_webhooks),
                "dead_outbox": int(dead_outbox),
            },
        }
    }


# ── Invoice explorer (ops console) ───────────────────────────


@router.get("/invoices")
async def platform_invoices(
    tenant_id: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1, le=1_000_000),
    per_page: int = Query(50, ge=1, le=200),
    _user=Depends(require_platform_role(*READ_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    query = select(Invoice)
    if tenant_id:
        query = query.where(Invoice.tenant_id == tenant_id)
    if status:
        query = query.where(Invoice.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    rows = (
        (
            await db.execute(
                query.order_by(Invoice.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    lines_by_invoice: dict[str, list[InvoiceLine]] = {}
    if rows:
        for line in (
            (
                await db.execute(
                    select(InvoiceLine)
                    .where(InvoiceLine.invoice_id.in_([i.id for i in rows]))
                    .order_by(InvoiceLine.sort_order)
                )
            )
            .scalars()
            .all()
        ):
            lines_by_invoice.setdefault(line.invoice_id, []).append(line)
    return {
        "data": [
            {
                "id": inv.id,
                "number": inv.number,
                "tenant_id": inv.tenant_id,
                "status": inv.status,
                "currency": inv.currency,
                "subtotal_minor": inv.subtotal_minor,
                "total_minor": inv.total_minor,
                "amount_due_minor": inv.amount_due_minor,
                "issued_at": inv.issued_at.isoformat() if inv.issued_at else None,
                "lines": [
                    {
                        "id": line.id,
                        "line_type": line.line_type,
                        "description": line.description,
                        "amount_minor": line.amount_minor,
                    }
                    for line in lines_by_invoice.get(inv.id, [])
                ],
            }
            for inv in rows
        ],
        "meta": {
            "total": int(total),
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < int(total),
        },
    }


# ── Settlement explorer (ops console) ────────────────────────


@router.get("/settlements")
async def platform_settlements(
    status: str | None = Query(None),
    period: str | None = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    page: int = Query(1, ge=1, le=1_000_000),
    per_page: int = Query(50, ge=1, le=200),
    _user=Depends(require_platform_role(*READ_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    query = select(SettlementStatement)
    if status:
        query = query.where(SettlementStatement.status == status)
    if period:
        query = query.where(SettlementStatement.period == period)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    rows = (
        (
            await db.execute(
                query.order_by(SettlementStatement.period.desc(), SettlementStatement.id.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    partner_ids = [s.partner_id for s in rows if s.partner_id]
    partners: dict[str, Partner] = {}
    if partner_ids:
        for p in (
            (await db.execute(select(Partner).where(Partner.id.in_(partner_ids)))).scalars().all()
        ):
            partners[p.id] = p
    return {
        "data": [
            {
                "id": s.id,
                "beneficiary_type": s.beneficiary_type,
                "partner_id": s.partner_id,
                "partner_name": partners[s.partner_id].name if s.partner_id in partners else None,
                "beneficiary_org_id": s.beneficiary_org_id,
                "period": s.period,
                "status": s.status,
                "currency": s.currency,
                "share_total_minor": s.share_total_minor,
                "net_amount_minor": s.net_amount_minor,
                "external_payment_ref": s.external_payment_ref,
            }
            for s in rows
        ],
        "meta": {
            "total": int(total),
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < int(total),
        },
    }


# ── Trace: invoice line → rated usage → provider call (issue §37) ──


@router.get("/trace/invoice-lines/{line_id}")
async def trace_invoice_line(
    line_id: str,
    page: int = Query(1, ge=1, le=1_000_000),
    per_page: int = Query(100, ge=1, le=500),
    _user=Depends(require_platform_role(*READ_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    line = await db.get(InvoiceLine, line_id)
    if line is None:
        raise AppError("TRACE_NOT_FOUND", "Invoice line not found", 404)
    invoice = await db.get(Invoice, line.invoice_id)

    total = (
        await db.execute(
            select(func.count(RatedUsage.id)).where(RatedUsage.invoice_line_id == line.id)
        )
    ).scalar_one()
    rated_rows = (
        (
            await db.execute(
                select(RatedUsage)
                .where(RatedUsage.invoice_line_id == line.id)
                .order_by(RatedUsage.rated_at, RatedUsage.id)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    event_ids = [r.usage_event_id for r in rated_rows]
    events: dict[str, UsageEvent] = {}
    if event_ids:
        for ev in (
            (await db.execute(select(UsageEvent).where(UsageEvent.id.in_(event_ids))))
            .scalars()
            .all()
        ):
            events[ev.id] = ev

    def _event_block(ev: UsageEvent | None) -> dict | None:
        if ev is None:
            return None
        return {
            "id": ev.id,
            "usage_type": ev.usage_type,
            "quantity": str(ev.quantity),
            "unit": ev.unit,
            "occurred_at": ev.occurred_at.isoformat(),
            "source": ev.source,
            "refs": {
                "org_id": ev.org_id,
                "workflow_run_id": ev.workflow_run_id,
                "evaluation_task_id": ev.evaluation_task_id,
                "project_id": ev.project_id,
                "provider": ev.provider,
                "model_or_service": ev.model_or_service,
            },
        }

    return {
        "data": {
            "line": {
                "id": line.id,
                "line_type": line.line_type,
                "description": line.description,
                "quantity": str(line.quantity),
                "amount_minor": line.amount_minor,
                "usage_summary": line.usage_summary,
            },
            "invoice": {
                "id": invoice.id,
                "number": invoice.number,
                "status": invoice.status,
                "tenant_id": invoice.tenant_id,
                "currency": invoice.currency,
            }
            if invoice
            else None,
            "rated_usage": [
                {
                    "id": r.id,
                    "usage_event_id": r.usage_event_id,
                    "usage_type": r.usage_type,
                    "quantity": str(r.quantity),
                    "billable_amount_minor": r.billable_amount_minor,
                    "billable_currency": r.billable_currency,
                    "internal_cost_minor": r.internal_cost_minor,
                    "internal_cost_currency": r.internal_cost_currency,
                    "margin_minor": r.margin_minor,
                    "status": r.status,
                    "rated_at": r.rated_at.isoformat(),
                    "cost_rate_snapshot": r.cost_rate_snapshot,
                    "sell_rate_snapshot": r.sell_rate_snapshot,
                    "fx_rate_snapshot": r.fx_rate_snapshot,
                    "usage_event": _event_block(events.get(r.usage_event_id)),
                }
                for r in rated_rows
            ],
            "counts": {"rated_rows": int(total), "page": page, "per_page": per_page},
        }
    }


# ── Trace: settlement entry → source → statement (issue §37) ──


@router.get("/trace/settlement-entries/{entry_id}")
async def trace_settlement_entry(
    entry_id: str,
    _user=Depends(require_platform_role(*READ_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    entry = await db.get(RevenueShareEntry, entry_id)
    if entry is None:
        raise AppError("TRACE_NOT_FOUND", "Settlement entry not found", 404)

    source: dict | None = None
    if entry.source_type in ("invoice", "invoice_line"):
        invoice_id = entry.source_id
        if entry.source_type == "invoice_line":
            src_line = await db.get(InvoiceLine, entry.source_id)
            invoice_id = src_line.invoice_id if src_line else None
        invoice = await db.get(Invoice, invoice_id) if invoice_id else None
        if invoice is not None:
            source = {
                "type": "invoice",
                "invoice_id": invoice.id,
                "number": invoice.number,
                "tenant_id": invoice.tenant_id,
                "status": invoice.status,
                "subtotal_minor": invoice.subtotal_minor,
                "total_minor": invoice.total_minor,
                "currency": invoice.currency,
            }
    elif entry.source_type == "marketplace_purchase":
        purchase = await db.get(MarketplacePurchase, entry.source_id)
        if purchase is not None:
            source = {
                "type": "marketplace_purchase",
                "purchase_id": purchase.id,
                "listing_id": purchase.listing_id,
                "buyer_tenant_id": purchase.buyer_tenant_id,
                "status": purchase.status,
                "amount_minor": purchase.amount_minor,
                "currency": purchase.currency,
                "economics_snapshot": purchase.economics_snapshot,
            }

    statement = (
        await db.get(SettlementStatement, entry.statement_id) if entry.statement_id else None
    )
    partner = await db.get(Partner, entry.partner_id) if entry.partner_id else None

    return {
        "data": {
            "entry": {
                "id": entry.id,
                "beneficiary_type": entry.beneficiary_type,
                "partner_id": entry.partner_id,
                "partner_name": partner.name if partner else None,
                "beneficiary_org_id": entry.beneficiary_org_id,
                "source_type": entry.source_type,
                "source_id": entry.source_id,
                "rule_id": entry.rule_id,
                "rule_snapshot": entry.rule_snapshot,
                "revenue_base_minor": entry.revenue_base_minor,
                "share_amount_minor": entry.share_amount_minor,
                "currency": entry.currency,
                "fx_rate_snapshot": entry.fx_rate_snapshot,
                "period": entry.period,
                "status": entry.status,
                "adjustment_of_id": entry.adjustment_of_id,
                "created_at": entry.created_at.isoformat(),
            },
            "source": source,
            "statement": {
                "id": statement.id,
                "period": statement.period,
                "status": statement.status,
                "net_amount_minor": statement.net_amount_minor,
                "currency": statement.currency,
            }
            if statement
            else None,
        }
    }
