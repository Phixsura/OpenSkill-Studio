"""Billing endpoints: subscriptions, invoices, payments, webhooks
(ADR-014 §6.6)."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

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
    # R135: retried POSTs double-refunded — keyed retry returns the original.
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)

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

    @field_validator("quantity")
    @classmethod
    def _qty(cls, v):
        # R129[L0]: the string is written verbatim into a Numeric(18,6)
        # column — non-numeric ("two", "1,5") crashes at flush (asyncpg
        # DataError, no sqlstate → 500 past the R88 backstop), and "NaN" is
        # accepted by Postgres numeric and then rendered as NaN in every
        # invoice response. Bound-validate at the import boundary.
        try:
            d = Decimal(v)
        except InvalidOperation:
            raise ValueError("quantity must be a decimal number") from None
        if not d.is_finite():
            raise ValueError("quantity must be finite")
        # R130[29]: quantize to the column's scale FIRST — '0.0000001' passes
        # a raw > 0 check but Postgres stores it as 0.000000 (the value the
        # validator rejects as '0'), and '1E-20000' passes the bounds but
        # asyncpg cannot encode it (DataError at flush). Validate the value
        # that will actually be stored.
        try:
            d = d.quantize(Decimal("0.000001"))
        except InvalidOperation:
            raise ValueError("quantity out of range") from None
        if d <= 0 or d >= Decimal("1000000000000"):
            raise ValueError("quantity out of range")
        return str(d)


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
    # R113[A0]: same R64[18] guard as marketplace checkout — a mock-provider
    # subscription in production gives the customer a dead mock-checkout URL
    # and a subscription that can never collect money. Resolve the effective
    # provider: prefer Stripe when configured; hard-fail mock in production.
    if body.provider == "mock":
        from app.config import settings

        if settings.stripe_secret_key:
            # R123[L10]: only route to Stripe when the target plan price
            # actually has a Stripe price ref — otherwise the checkout dies
            # on PLAN_NOT_AVAILABLE deep in session creation. In non-prod,
            # fall back to mock (dev keeps working while refs are unset).
            from app.controlplane.models.plan import PlanPrice, PlanVersion, ProductPlan

            has_ref = (
                await db.execute(
                    select(PlanPrice.id)
                    .join(PlanVersion, PlanVersion.id == PlanPrice.plan_version_id)
                    .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
                    .where(
                        ProductPlan.key == body.plan_key,
                        PlanVersion.status == "active",
                        PlanPrice.currency == tenant.currency,
                        PlanPrice.interval == body.interval,
                        # R129[L3]: match downstream truthiness gates — an
                        # empty-string ref (the natural "cleared" payload)
                        # must route to the fallback, not to Stripe where
                        # the adapter rejects it deep with a 409.
                        PlanPrice.external_price_ref.isnot(None),
                        PlanPrice.external_price_ref != "",
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
            if has_ref is not None:
                body.provider = "stripe"
            elif settings.app_env == "production":
                raise AppError(
                    "BILLING_PROVIDER_UNCONFIGURED",
                    "This plan is not yet available for online checkout; contact support",
                    409,
                )
        elif settings.app_env == "production":
            raise AppError(
                "BILLING_PROVIDER_UNCONFIGURED",
                "Checkout payments are not configured; contact support",
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
    # R130[2]: seat basis = the PERIOD-START floor/plan (what the close's
    # base seats line covers), not the current post-prior-change values.
    start_seats, start_included, start_seat_price = await billing_svc._period_start_seat_basis(
        db, sub
    )
    # R131 ([5]): in the post-period-end gap, preview against the NEXT window
    # (where R81/R82[1] semantics actually prorate the change), not the
    # elapsed one whose days_left clamps to 0 (net 0 shown, ~full delta
    # billed).
    _at = billing_svc._now()
    pv_start, pv_end = sub.current_period_start, sub.current_period_end
    if _at >= pv_end:
        pv_start = pv_end
        pv_end = billing_svc._add_interval(pv_start, sub.interval)
    preview = billing_svc.proration_preview(
        period_start=pv_start,
        period_end=pv_end,
        at=_at,
        old_amount_minor=old_price.amount_minor if old_price else 0,
        new_amount_minor=new_price.amount_minor if new_price else 0,
        old_seats=start_seats,
        new_seats=body.seats if body.seats is not None else sub.seat_quantity,
        seat_price_minor=(new_price.overage_seat_amount_minor or 0) if new_price else 0,
        # R129[M5]: band-aware seat math — the preview must show the same
        # seat component the close's R123[C0] segment walk will invoice.
        billable_seats=await billing_svc._live_student_seats(db, tenant_id),
        old_included_seats=start_included,
        new_included_seats=new_price.included_seats if new_price else 0,
        old_seat_price_minor=start_seat_price,
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


@router.post(
    "/tenants/{tenant_id}/subscription/reactivate",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def reactivate_subscription(
    tenant_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """R82[M0]: un-cancel a pending cancellation before the period ends."""
    await tenant_svc.require_tenant_member(db, tenant_id, user, "owner")
    tenant = await db.get(TenantAccount, tenant_id)
    sub = await billing_svc.get_live_subscription(db, tenant_id)
    if sub is None:
        raise AppError("SUBSCRIPTION_NOT_FOUND", "No live subscription", 404)
    sub = await billing_svc.reactivate_subscription(
        db, tenant, sub, actor=make_actor(request, user, "tenant")
    )
    await db.commit()
    return DataResponse(data=await _subscription_response(db, sub))


# ── Tenant invoices / payments ───────────────────────────────


@router.get("/tenants/{tenant_id}/invoices", dependencies=[Depends(rate_limit(30, 60))])
async def list_invoices(
    tenant_id: str,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    q = select(Invoice).where(Invoice.tenant_id == tenant_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(Invoice.created_at.desc(), Invoice.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
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
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await tenant_svc.require_tenant_member(db, tenant_id, user)
    # R76[3]: a hard limit(100) with meta fabricated from the truncated slice
    # (total=len, has_more=False) made records beyond the cap silently
    # unreachable — the API lied about completeness. Real pagination.
    total = (
        await db.execute(
            select(func.count(PaymentRecord.id)).where(PaymentRecord.tenant_id == tenant_id)
        )
    ).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                select(PaymentRecord)
                .where(PaymentRecord.tenant_id == tenant_id)
                .order_by(PaymentRecord.created_at.desc(), PaymentRecord.id.desc())
                .offset(offset)
                .limit(per_page)
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
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
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
    # R43[15]: manual invoices must not be raised against cancelled/archived
    # tenants (finalize triggers rev-share accrual and dunning against an
    # account that can never pay). Suspended tenants stay invoiceable — debt
    # collection is exactly why they're suspended.
    from app.controlplane.models.tenant import TenantStatus

    if tenant.status in (TenantStatus.CANCELLED, TenantStatus.ARCHIVED):
        raise AppError(
            "TENANT_STATUS_CONFLICT",
            f"Cannot invoice a {tenant.status.value} tenant",
            409,
        )
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
        idempotency_key=body.idempotency_key,
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


@router.get(
    "/platform/billing/webhook-events",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_webhook_events(
    # R101[L24]: "duplicate" is a replay RESPONSE flag, never a stored status
    # — advertising it as a filter always returned an empty page.
    status: str | None = Query(default=None, pattern=r"^(received|processed|failed|ignored)$"),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=200),
    user: User = Depends(require_platform_role(*_BILLING_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    """R98[m16]: failed webhook events were unlistable — the replay endpoint
    needs the internal event id, but nothing exposed it (ops couldn't find
    the failed checkout.session.completed a paying customer was stuck on)."""
    from app.controlplane.models.billing import BillingWebhookEvent

    q = select(BillingWebhookEvent)
    if status:
        q = q.where(BillingWebhookEvent.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    offset = (page - 1) * per_page
    rows = (
        (
            await db.execute(
                q.order_by(BillingWebhookEvent.created_at.desc(), BillingWebhookEvent.id.desc())
                .offset(offset)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return ListResponse(
        data=[
            {
                "id": e.id,
                "provider": e.provider,
                "external_event_id": e.external_event_id,
                "event_type": e.event_type,
                "status": e.status,
                "error": e.error,
                "created_at": e.created_at.isoformat(),
            }
            for e in rows
        ],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(offset + per_page) < total
        ),
    )


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
        # R113[L13]: this 404 was copy-pasted with INVOICE_NOT_FOUND — ops
        # tooling keying on the machine code misdiagnosed a bad event id as a
        # missing invoice.
        raise AppError("WEBHOOK_EVENT_NOT_FOUND", "Webhook event not found", 404)
    if event.status != "failed":
        raise AppError("VALIDATION_ERROR", "Only failed events can be replayed", 409)
    parsed = ParsedWebhookEvent(
        external_event_id=event.external_event_id,
        event_type=event.event_type,
        data=event.payload,
    )
    # R113[M33]: a replay that failed AGAIN 500'd out of the endpoint — the
    # session rolled back, the fresh error was discarded (event kept the
    # stale one), and ops got no diagnosis. Mirror process_webhook: savepoint
    # the handler, record the new failure on the event, and return it.
    try:
        async with db.begin_nested():
            handled = await _apply_webhook_event(db, event.provider, parsed)
    except Exception as exc:  # noqa: BLE001 — recorded for the next replay
        event.status = "failed"
        event.error = str(exc)[:2000]
        event.processed_at = billing_svc._now()
        await db.commit()
        log.warning("cp_webhook_replay_failed", event_id=event.id, event_type=event.event_type)
        return DataResponse(data={"replayed": False, "error": str(exc)[:200]})
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
