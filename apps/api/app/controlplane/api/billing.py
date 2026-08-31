"""Billing endpoints: subscriptions, invoices, payments, webhooks
(ADR-014 §6.6)."""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.api.deps import make_actor, require_platform_role
from app.controlplane.models.billing import (
    Invoice,
    InvoiceLine,
    PaymentRecord,
    Subscription,
)
from app.controlplane.models.plan import PlanVersion, ProductPlan
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services import billing as billing_svc
from app.controlplane.services import tenants as tenant_svc
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str

log = structlog.get_logger()

router = APIRouter(tags=["Billing"])

_BILLING_ROLES = ("billing_admin", "platform_admin")


class StartSubscriptionRequest(BaseModel):
    plan_key: str = Field(min_length=2, max_length=50)
    interval: str = Field(pattern=r"^(month|year)$")
    seats: int = Field(default=0, ge=0, le=1_000_000)
    provider: str = Field(pattern=r"^(manual|mock|stripe)$")


class ChangeSubscriptionRequest(BaseModel):
    plan_key: str | None = Field(default=None, min_length=2, max_length=50)
    seats: int | None = Field(default=None, ge=0, le=1_000_000)
    proration_mode: str | None = Field(default=None, pattern=r"^(immediate|next_period)$")


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = True


MAX_MINOR = 1_000_000_000_000_000  # 10^15, well under int8 (R88 overflow guard)


class RecordPaymentRequest(BaseModel):
    amount_minor: int = Field(gt=0, le=MAX_MINOR)
    method: str = Field(pattern=r"^(manual_bank_transfer|other)$")
    external_ref: str | None = Field(default=None, max_length=120)
    reference_note: str | None = Field(default=None, max_length=500)
    received_at: datetime | None = None

    @field_validator("reference_note", "external_ref")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class VoidInvoiceRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class CreditNoteRequest(BaseModel):
    amount_minor: int = Field(gt=0, le=MAX_MINOR)
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class ManualInvoiceLineInput(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    amount_minor: int = Field(ge=-MAX_MINOR, le=MAX_MINOR)
    quantity: str = "1"

    @field_validator("description")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class ManualInvoiceRequest(BaseModel):
    lines: list[ManualInvoiceLineInput] = Field(min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=2000)
    due_days: int = Field(default=14, ge=0, le=365)

    @field_validator("notes")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


async def _subscription_response(db: AsyncSession, sub: Subscription) -> dict:
    version = await db.get(PlanVersion, sub.plan_version_id)
    plan = await db.get(ProductPlan, version.plan_id) if version else None
    return {
        "id": sub.id,
        "status": sub.status,
        "plan_key": plan.key if plan else None,
        "plan_version": version.version if version else None,
        "currency": sub.currency,
        "interval": sub.interval,
        "seat_quantity": sub.seat_quantity,
        "trial_ends_at": sub.trial_ends_at.isoformat() if sub.trial_ends_at else None,
        "current_period_start": sub.current_period_start.isoformat(),
        "current_period_end": sub.current_period_end.isoformat(),
        "cancel_at_period_end": sub.cancel_at_period_end,
        "provider": sub.provider,
    }


def _invoice_response(invoice: Invoice, lines: list[InvoiceLine] | None = None) -> dict:
    data = {
        "id": invoice.id,
        "number": invoice.number,
        "status": invoice.status,
        "currency": invoice.currency,
        "subtotal_minor": invoice.subtotal_minor,
        "credit_applied_minor": invoice.credit_applied_minor,
        "tax_minor": invoice.tax_minor,
        "total_minor": invoice.total_minor,
        "amount_due_minor": invoice.amount_due_minor,
        "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
        "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
        "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
        "notes": invoice.notes,
    }
    if lines is not None:
        data["lines"] = [
            {
                "id": line.id,
                "line_type": line.line_type,
                "description": line.description,
                "quantity": str(line.quantity),
                "unit_amount_minor": line.unit_amount_minor,
                "amount_minor": line.amount_minor,
                "usage_summary": line.usage_summary,
            }
            for line in lines
        ]
    return data


# ── Tenant subscription ──────────────────────────────────────


@router.get("/tenants/{tenant_id}/subscription", dependencies=[Depends(rate_limit(60, 60))])
async def get_subscription(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    sub = await billing_svc.get_live_subscription(db, tenant_id)
    if sub is None:
        return DataResponse(data={"status": "none"})
    return DataResponse(data=await _subscription_response(db, sub))


@router.post(
    "/tenants/{tenant_id}/subscription",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def start_subscription(
    tenant_id: str,
    body: StartSubscriptionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    tenant_svc.require_tenant_active(tenant)
    # Manual provider = platform-admin-driven; tenants use mock/stripe checkout
    if body.provider == "manual":
        from app.controlplane.services.tenants import has_platform_role

        if not await has_platform_role(db, user, "platform_admin", "billing_admin"):
            raise AppError(
                "MANUAL_BILLING_MODE",
                "Manual subscriptions are created by platform billing admins",
                409,
            )
    sub, checkout_url = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key=body.plan_key,
        interval=body.interval,
        seats=body.seats,
        provider=body.provider,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    if checkout_url is not None:
        return DataResponse(data={"checkout_url": checkout_url})
    return DataResponse(data=await _subscription_response(db, sub))


@router.post(
    "/tenants/{tenant_id}/subscription/change-preview",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def change_preview(
    tenant_id: str,
    body: ChangeSubscriptionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    sub = await billing_svc.get_live_subscription(db, tenant_id)
    if sub is None:
        raise AppError("SUBSCRIPTION_NOT_FOUND", "No live subscription", 404)
    from app.controlplane.models.plan import PlanPrice

    old_price = (
        await db.execute(
            select(PlanPrice).where(
                PlanPrice.plan_version_id == sub.plan_version_id,
                PlanPrice.currency == sub.currency,
                PlanPrice.interval == sub.interval,
            )
        )
    ).scalar_one_or_none()
    if body.plan_key:
        _, new_price = await billing_svc._resolve_plan_price(
            db, body.plan_key, sub.currency, sub.interval
        )
    else:
        new_price = old_price
    preview = billing_svc.proration_preview(
        period_start=sub.current_period_start,
        period_end=sub.current_period_end,
        at=billing_svc._now(),
        old_amount_minor=old_price.amount_minor if old_price else 0,
        new_amount_minor=new_price.amount_minor if new_price else 0,
        old_seats=sub.seat_quantity,
        new_seats=body.seats if body.seats is not None else sub.seat_quantity,
        seat_price_minor=(new_price.overage_seat_amount_minor or 0) if new_price else 0,
    )
    return DataResponse(data=preview)


@router.post(
    "/tenants/{tenant_id}/subscription/change",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def change_subscription(
    tenant_id: str,
    body: ChangeSubscriptionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    tenant_svc.require_tenant_active(tenant)
    sub = await billing_svc.get_live_subscription(db, tenant_id)
    if sub is None:
        raise AppError("SUBSCRIPTION_NOT_FOUND", "No live subscription", 404)
    if body.plan_key is None and body.seats is None:
        raise AppError("VALIDATION_ERROR", "Nothing to change", 422)
    result = await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key=body.plan_key,
        seats=body.seats,
        proration_mode=body.proration_mode,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    return DataResponse(data=result)


@router.post(
    "/tenants/{tenant_id}/subscription/cancel",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def cancel_subscription(
    tenant_id: str,
    body: CancelSubscriptionRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    sub = await billing_svc.get_live_subscription(db, tenant_id)
    if sub is None:
        raise AppError("SUBSCRIPTION_NOT_FOUND", "No live subscription", 404)
    sub = await billing_svc.cancel_subscription(
        db,
        tenant,
        sub,
        at_period_end=body.at_period_end,
        actor=make_actor(request, user, "tenant"),
    )
    await db.commit()
    return DataResponse(data=await _subscription_response(db, sub))


# ── Tenant invoices / payments ───────────────────────────────


@router.get("/tenants/{tenant_id}/invoices", dependencies=[Depends(rate_limit(30, 60))])
async def list_invoices(
    tenant_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(Invoice).where(Invoice.tenant_id == tenant_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (await db.execute(q.order_by(Invoice.created_at.desc()).offset(offset).limit(per_page)))
        .scalars()
        .all()
    )
    return ListResponse(
        data=[_invoice_response(i) for i in rows],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


@router.get(
    "/tenants/{tenant_id}/invoices/{invoice_id}",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_invoice(
    tenant_id: str,
    invoice_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None or invoice.tenant_id != tenant_id:
        raise AppError("INVOICE_NOT_FOUND", "Invoice not found", 404)
    lines = (
        (
            await db.execute(
                select(InvoiceLine)
                .where(InvoiceLine.invoice_id == invoice.id)
                .order_by(InvoiceLine.sort_order)
            )
        )
        .scalars()
        .all()
    )
    payments = (
        (await db.execute(select(PaymentRecord).where(PaymentRecord.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    data = _invoice_response(invoice, lines)
    data["payments"] = [
        {
            "id": p.id,
            "amount_minor": p.amount_minor,
            "method": p.method,
            "status": p.status,
            "received_at": p.received_at.isoformat() if p.received_at else None,
        }
        for p in payments
    ]
    return DataResponse(data=data)


@router.get("/tenants/{tenant_id}/payments", dependencies=[Depends(rate_limit(30, 60))])
async def list_payments(
    tenant_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    rows = (
        (
            await db.execute(
                select(PaymentRecord)
                .where(PaymentRecord.tenant_id == tenant_id)
                .order_by(PaymentRecord.created_at.desc())
                .limit(100)
            )
        )
        .scalars()
        .all()
    )
    data = [
        {
            "id": p.id,
            "invoice_id": p.invoice_id,
            "amount_minor": p.amount_minor,
            "currency": p.currency,
            "method": p.method,
            "status": p.status,
            "received_at": p.received_at.isoformat() if p.received_at else None,
        }
        for p in rows
    ]
    return ListResponse(
        data=data,
        meta=PaginationMeta(total=len(data), page=1, per_page=len(data) or 1, has_more=False),
    )


# ── Platform manual ops ──────────────────────────────────────


@router.post(
    "/platform/tenants/{tenant_id}/invoices",
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_manual_invoice(
    tenant_id: str,
    body: ManualInvoiceRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from datetime import timedelta

    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    invoice = Invoice(
        tenant_id=tenant_id,
        currency=tenant.currency,
        provider="manual",
        notes=body.notes,
        issued_at=billing_svc._now(),
        due_at=billing_svc._now() + timedelta(days=body.due_days),
        created_by=user.id,
    )
    db.add(invoice)
    await db.flush()
    subtotal = 0
    for i, line in enumerate(body.lines):
        db.add(
            InvoiceLine(
                invoice_id=invoice.id,
                line_type="manual",
                description=line.description,
                quantity=line.quantity,
                amount_minor=line.amount_minor,
                sort_order=i,
            )
        )
        subtotal += line.amount_minor
    invoice.subtotal_minor = subtotal
    invoice.total_minor = max(subtotal, 0)
    invoice.amount_due_minor = invoice.total_minor
    await db.commit()
    return DataResponse(data=_invoice_response(invoice))


@router.post("/platform/invoices/{invoice_id}/finalize", dependencies=[Depends(rate_limit(20, 60))])
async def finalize_invoice(
    invoice_id: str,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None:
        raise AppError("INVOICE_NOT_FOUND", "Invoice not found", 404)
    invoice = await billing_svc.finalize_invoice(db, invoice, actor=make_actor(request, user))
    await db.commit()
    return DataResponse(data=_invoice_response(invoice))


@router.post(
    "/platform/invoices/{invoice_id}/payments",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def record_payment(
    invoice_id: str,
    body: RecordPaymentRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None:
        raise AppError("INVOICE_NOT_FOUND", "Invoice not found", 404)
    payment = await billing_svc.record_payment(
        db,
        invoice,
        amount_minor=body.amount_minor,
        method=body.method,
        external_ref=body.external_ref,
        reference_note=body.reference_note,
        received_at=body.received_at,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(
        data={"id": payment.id, "amount_minor": payment.amount_minor, "status": payment.status}
    )


@router.post("/platform/invoices/{invoice_id}/void", dependencies=[Depends(rate_limit(20, 60))])
async def void_invoice(
    invoice_id: str,
    body: VoidInvoiceRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None:
        raise AppError("INVOICE_NOT_FOUND", "Invoice not found", 404)
    invoice = await billing_svc.void_invoice(
        db, invoice, reason=body.reason, actor=make_actor(request, user)
    )
    await db.commit()
    return DataResponse(data=_invoice_response(invoice))


@router.post(
    "/platform/invoices/{invoice_id}/credit-notes",
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def issue_credit_note(
    invoice_id: str,
    body: CreditNoteRequest,
    request: Request,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None:
        raise AppError("INVOICE_NOT_FOUND", "Invoice not found", 404)
    note = await billing_svc.issue_credit_note(
        db,
        invoice,
        amount_minor=body.amount_minor,
        reason=body.reason,
        actor=make_actor(request, user),
    )
    await db.commit()
    return DataResponse(
        data={"id": note.id, "amount_minor": note.amount_minor, "status": note.status}
    )


@router.post("/platform/billing/close-periods", dependencies=[Depends(rate_limit(10, 60))])
async def close_due_periods(
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    count = await billing_svc.scan_due_periods(db)
    await db.commit()
    return DataResponse(data={"enqueued": count})


@router.post(
    "/platform/billing/webhook-events/{event_id}/replay",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def replay_webhook_event(
    event_id: str,
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from app.controlplane.models.billing import BillingWebhookEvent
    from app.controlplane.services.billing import _apply_webhook_event
    from app.controlplane.services.billing_providers.base import ParsedWebhookEvent

    event = await db.get(BillingWebhookEvent, event_id)
    if event is None:
        raise AppError("INVOICE_NOT_FOUND", "Webhook event not found", 404)
    if event.status != "failed":
        raise AppError("VALIDATION_ERROR", "Only failed events can be replayed", 409)
    parsed = ParsedWebhookEvent(
        external_event_id=event.external_event_id,
        event_type=event.event_type,
        data=event.payload,
    )
    handled = await _apply_webhook_event(db, event.provider, parsed)
    event.status = "processed" if handled else "ignored"
    event.error = None
    event.processed_at = billing_svc._now()
    await db.commit()
    return DataResponse(data={"status": event.status})


# ── Public webhook receiver ──────────────────────────────────


@router.post("/billing/webhooks/{provider_key}", dependencies=[Depends(rate_limit(60, 60))])
async def billing_webhook(
    provider_key: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Unauthenticated + signature-verified. Replays short-circuit via the
    (provider, external_event_id) unique key — single-effect guarantee."""
    raw_body = await request.body()
    result = await billing_svc.process_webhook(db, provider_key, dict(request.headers), raw_body)
    await db.commit()
    return DataResponse(data=result)
