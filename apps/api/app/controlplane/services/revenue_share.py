"""Revenue-share accrual + settlement statements (ADR-014 §7.2–7.3)."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

import structlog
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.billing import Invoice, InvoiceLine
from app.controlplane.models.partner import (
    Partner,
    RevenueShareEntry,
    RevenueShareRule,
    SettlementStatement,
)
from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services.audit import Actor, record_audit
from app.controlplane.services.rating import convert_minor, resolve_fx
from app.controlplane.worker import register_handler
from app.exceptions import AppError

log = structlog.get_logger()


def _now() -> datetime:
    return datetime.now(UTC)


def rule_specificity(
    rule: RevenueShareRule,
    *,
    tenant_id: str | None,
    plan_id: str | None,
    listing_id: str | None,
    country: str | None,
) -> int | None:
    """Score: tenant+8 | plan+4 | listing+2 | country+1. None = no match."""
    score = 0
    if rule.tenant_id is not None:
        if rule.tenant_id != tenant_id:
            return None
        score += 8
    if rule.plan_id is not None:
        if rule.plan_id != plan_id:
            return None
        score += 4
    if rule.listing_id is not None:
        if rule.listing_id != listing_id:
            return None
        score += 2
    if rule.country is not None:
        if rule.country != country:
            return None
        score += 1
    return score


def compute_share_minor(
    rule_type: str,
    *,
    rate: Decimal | None,
    amount_minor: int | None,
    base_minor: int,
    units: Decimal = Decimal(1),
) -> int:
    if rule_type in (
        "percentage_of_net_revenue",
        "percentage_of_gross_revenue",
        "percentage_of_margin",
    ):
        return int(
            (Decimal(base_minor) * (rate or 0) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
    if rule_type in ("fixed_amount_per_unit", "fixed_amount_per_seat"):
        return int(
            (Decimal(amount_minor or 0) * units).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
    raise AppError("RULE_PARAM_INVALID", f"Unknown rule type '{rule_type}'", 422)


def _rule_snapshot(rule: RevenueShareRule) -> dict:
    return {
        "rule_id": rule.id,
        "rule_type": rule.rule_type,
        "beneficiary_type": rule.beneficiary_type,
        "revenue_type": rule.revenue_type,
        "rate": str(rule.rate) if rule.rate is not None else None,
        "amount_minor": rule.amount_minor,
        "version": rule.version,
        "effective_from": rule.effective_from.isoformat(),
    }


async def _resolve_rule(
    db: AsyncSession,
    *,
    beneficiary_type: str,
    partner_id: str | None,
    revenue_types: list[str],
    at: datetime,
    tenant_id: str | None,
    plan_id: str | None = None,
    listing_id: str | None = None,
    country: str | None = None,
) -> RevenueShareRule | None:
    q = select(RevenueShareRule).where(
        RevenueShareRule.beneficiary_type == beneficiary_type,
        RevenueShareRule.status == "active",
        RevenueShareRule.revenue_type.in_([*revenue_types, "all"]),
        RevenueShareRule.effective_from <= at,
        or_(
            RevenueShareRule.effective_until.is_(None),
            RevenueShareRule.effective_until > at,
        ),
    )
    if partner_id is not None:
        q = q.where(RevenueShareRule.partner_id == partner_id)
    candidates = (await db.execute(q)).scalars().all()
    best_key: tuple | None = None
    best: RevenueShareRule | None = None
    for rule in candidates:
        score = rule_specificity(
            rule, tenant_id=tenant_id, plan_id=plan_id, listing_id=listing_id, country=country
        )
        if score is None:
            continue
        # exact revenue_type beats "all" at equal specificity; then version
        type_rank = 1 if rule.revenue_type != "all" else 0
        key = (score, type_rank, rule.version)
        if best_key is None or key > best_key:
            best_key, best = key, rule
    return best


async def _insert_entry(db: AsyncSession, **values) -> RevenueShareEntry | None:
    """Natural-key idempotent insert (replay-safe).

    The expression-based unique index can't be targeted by ON CONFLICT
    inference cleanly, so: pre-check + plain insert. Still race-safe — a
    concurrent loser hits the unique index (IntegrityError), and the outbox
    retry then finds the row in the pre-check and no-ops.
    """
    existing = (
        await db.execute(
            select(RevenueShareEntry.id)
            .where(
                RevenueShareEntry.source_type == values["source_type"],
                RevenueShareEntry.source_id == values["source_id"],
                RevenueShareEntry.beneficiary_type == values["beneficiary_type"],
                (
                    RevenueShareEntry.partner_id == values.get("partner_id")
                    if values.get("partner_id")
                    else RevenueShareEntry.partner_id.is_(None)
                ),
                (
                    RevenueShareEntry.beneficiary_org_id == values.get("beneficiary_org_id")
                    if values.get("beneficiary_org_id")
                    else RevenueShareEntry.beneficiary_org_id.is_(None)
                ),
                (
                    RevenueShareEntry.adjustment_of_id == values.get("adjustment_of_id")
                    if values.get("adjustment_of_id")
                    else RevenueShareEntry.adjustment_of_id.is_(None)
                ),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing is not None:
        return None
    entry = RevenueShareEntry(**values)
    db.add(entry)
    await db.flush()
    return entry


# ── Accrual handlers ─────────────────────────────────────────


def _revenue_base(invoice: Invoice) -> int:
    """Gross revenue base for percentage/fixed rules: the invoice subtotal."""
    return invoice.subtotal_minor


async def _current_plan_id(db: AsyncSession, tenant_id: str) -> str | None:
    """The tenant's current plan id (for plan-scoped rule matching, R56[27]).

    Rules may carry a plan_id dimension (+4 specificity), but accrue_for_invoice
    never passed one, so every plan-scoped rule was disqualified forever."""
    try:
        from app.controlplane.models.billing import Subscription
        from app.controlplane.models.plan import PlanVersion

        row = (
            await db.execute(
                select(PlanVersion.plan_id)
                .join(Subscription, Subscription.plan_version_id == PlanVersion.id)
                .where(
                    Subscription.tenant_id == tenant_id,
                    Subscription.status != "cancelled",
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        return row
    except ImportError:
        return None


async def _typed_base(db: AsyncSession, invoice: Invoice, revenue_type: str) -> int:
    """The slice of the invoice base a revenue_type-scoped rule accrues on
    (R56[23]): 'subscription' = plan + seats + proration lines; 'usage' = usage
    lines. A rule scoped to one type must not accrue on the whole subtotal —
    a 30% usage rule on a ¥100k-plan + ¥10k-usage invoice owes ¥3,000, not
    ¥33,000 (and license lines already accrue via the purchase path)."""
    line_types = ("plan", "seats", "proration") if revenue_type == "subscription" else ("usage",)
    total = (
        await db.execute(
            select(func.coalesce(func.sum(InvoiceLine.amount_minor), 0)).where(
                InvoiceLine.invoice_id == invoice.id,
                InvoiceLine.line_type.in_(line_types),
            )
        )
    ).scalar_one()
    return int(total)


async def accrue_for_invoice(db: AsyncSession, invoice_id: str) -> RevenueShareEntry | None:
    invoice = await db.get(Invoice, invoice_id)
    if invoice is None or invoice.status not in ("open", "paid"):
        return None
    tenant = await db.get(TenantAccount, invoice.tenant_id)
    if tenant is None or tenant.partner_id is None:
        return None  # unattributed — seller shares ride the purchase path
    partner = await db.get(Partner, tenant.partner_id)
    if partner is None or partner.status == "terminated":
        return None  # only TERMINATED stops accruing (ADR §7.6). SUSPENDED is
        # a temporary payout hold (handled at the settlement stage) — the
        # revenue is still earned, so accrue it; dropping it here would lose
        # the accrual permanently (invoice.finalized fires once, never re-runs).
    at = invoice.finalized_at or _now()
    rule = await _resolve_rule(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        revenue_types=["subscription", "usage"],
        at=at,
        tenant_id=tenant.id,
        plan_id=await _current_plan_id(db, tenant.id),
        country=tenant.country,
    )
    if rule is None:
        return None
    # Base per rule type. base_currency tracks which currency the base is
    # denominated in — margin_minor is computed in the PLATFORM currency
    # (rating converts both sides to platform_currency before subtracting),
    # while every invoice-line figure is in invoice.currency. Treating the
    # margin sum as invoice-currency mislabeled/misconverted it whenever the
    # two differ (R56[21]).
    base_currency = invoice.currency
    if rule.rule_type == "percentage_of_gross_revenue":
        base = _revenue_base(invoice)
        units = Decimal(1)
    elif rule.rule_type == "percentage_of_net_revenue":
        base = invoice.total_minor - invoice.tax_minor
        units = Decimal(1)
    elif rule.rule_type == "percentage_of_margin":
        from app.config import settings as _settings

        margin = (
            await db.execute(
                select(func.coalesce(func.sum(RatedUsage.margin_minor), 0))
                .join(InvoiceLine, InvoiceLine.id == RatedUsage.invoice_line_id)
                .where(InvoiceLine.invoice_id == invoice.id)
            )
        ).scalar_one()
        base = int(margin)  # NULL margins excluded by the SUM (count 0, ADR)
        base_currency = _settings.platform_currency
        units = Decimal(1)
    elif rule.rule_type == "fixed_amount_per_seat":
        seats = (
            await db.execute(
                select(func.coalesce(func.sum(InvoiceLine.quantity), 0)).where(
                    InvoiceLine.invoice_id == invoice.id,
                    InvoiceLine.line_type == "seats",
                )
            )
        ).scalar_one()
        base = _revenue_base(invoice)
        units = Decimal(seats)
    else:  # fixed_amount_per_unit — one unit per invoice
        base = _revenue_base(invoice)
        units = Decimal(1)

    # R56[23]: a rule scoped to ONE revenue_type must accrue on that slice of
    # the invoice, not the whole subtotal. "all" (and net/margin bases) keep
    # the full base.
    if rule.revenue_type in ("subscription", "usage") and rule.rule_type in (
        "percentage_of_gross_revenue",
        "fixed_amount_per_unit",
        "fixed_amount_per_seat",
    ):
        base = await _typed_base(db, invoice, rule.revenue_type)

    # R56[26]: fixed_amount rules carry their own amount_currency — honor it by
    # converting the fixed amount into the base currency before computing, so
    # $5.00/seat means $5.00/seat regardless of the invoice currency.
    amount_minor = rule.amount_minor
    if (
        rule.rule_type in ("fixed_amount_per_unit", "fixed_amount_per_seat")
        and rule.amount_minor is not None
        and rule.amount_currency
        and rule.amount_currency != base_currency
    ):
        fx_amt = await resolve_fx(db, rule.amount_currency, base_currency, at)
        if fx_amt is None:
            raise AppError(
                "REVSHARE_FX_MISSING",
                f"No FX rate {rule.amount_currency}->{base_currency} for fixed-amount rule",
                409,
            )
        amount_minor = convert_minor(
            rule.amount_minor, fx_amt[0], rule.amount_currency, base_currency
        )

    share = compute_share_minor(
        rule.rule_type,
        rate=rule.rate,
        amount_minor=amount_minor,
        base_minor=base,
        units=units,
    )
    # Convert to the partner's settlement currency at accrual time
    fx_snapshot = None
    if base_currency != partner.currency:
        fx = await resolve_fx(db, base_currency, partner.currency, at)
        if fx is None:
            log.warning(
                "cp_revshare_fx_missing",
                invoice_id=invoice.id,
                pair=f"{base_currency}->{partner.currency}",
            )
            # RAISE, don't return None: a None return signals "nothing to do"
            # and the outbox marks the message done → the accrual would be
            # SILENTLY LOST. Raising lets process_outbox_once retry with
            # backoff (ops adds the FX rate) and, past max attempts,
            # dead-letter into the platform dashboard's dead_outbox counter
            # instead of vanishing. All the None returns above are genuine
            # no-ops (unattributed / no rule / inactive partner) and stay.
            raise AppError(
                "REVSHARE_FX_MISSING",
                f"No FX rate {base_currency}->{partner.currency} for invoice accrual",
                409,
            )
        rate_val, fx_snapshot = fx
        share = convert_minor(share, rate_val, base_currency, partner.currency)
        base = convert_minor(base, rate_val, base_currency, partner.currency)
    return await _insert_entry(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        source_type="invoice",
        source_id=invoice.id,
        rule_id=rule.id,
        rule_snapshot=_rule_snapshot(rule),
        revenue_base_minor=base,
        share_amount_minor=share,
        currency=partner.currency,
        fx_rate_snapshot=fx_snapshot,
        period=at.strftime("%Y-%m"),
    )


async def accrue_for_purchase(db: AsyncSession, purchase_id: str) -> int:
    """Marketplace purchase → seller_org entry + optional partner entry,
    straight from the frozen economics snapshot (never today's settings)."""
    try:
        from app.controlplane.models.marketplace import MarketplacePurchase
    except ImportError:
        return 0
    purchase = await db.get(MarketplacePurchase, purchase_id)
    if purchase is None or purchase.status != "paid":
        return 0
    snapshot = purchase.economics_snapshot or {}
    period = _now().strftime("%Y-%m")
    created = 0
    seller_org_id = snapshot.get("seller_org_id")
    if seller_org_id and purchase.seller_share_minor:
        entry = await _insert_entry(
            db,
            beneficiary_type="seller_org",
            beneficiary_org_id=seller_org_id,
            source_type="marketplace_purchase",
            source_id=purchase.id,
            rule_id=(snapshot.get("seller_rule_snapshot") or {}).get("rule_id"),
            rule_snapshot=snapshot.get("seller_rule_snapshot") or {"from_economics_snapshot": True},
            revenue_base_minor=purchase.amount_minor,
            share_amount_minor=purchase.seller_share_minor,
            currency=purchase.currency,
            period=period,
        )
        created += 1 if entry else 0
    partner_id = snapshot.get("partner_id")
    if partner_id and purchase.partner_share_minor:
        # R56[22]: partner entries must be denominated in the PARTNER's
        # settlement currency (ADR-014 Decision 8 — statements are
        # single-currency). accrue_for_invoice converts; this path wrote
        # buyer-currency figures that generate_statement then summed into a
        # partner-currency statement unconverted.
        partner = await db.get(Partner, partner_id)
        share = purchase.partner_share_minor
        base = purchase.amount_minor
        fx_snapshot = None
        entry_currency = purchase.currency
        if partner is not None and partner.currency != purchase.currency:
            fx = await resolve_fx(db, purchase.currency, partner.currency, _now())
            if fx is None:
                raise AppError(
                    "REVSHARE_FX_MISSING",
                    f"No FX rate {purchase.currency}->{partner.currency} for purchase accrual",
                    409,
                )
            rate_val, fx_snapshot = fx
            share = convert_minor(share, rate_val, purchase.currency, partner.currency)
            base = convert_minor(base, rate_val, purchase.currency, partner.currency)
            entry_currency = partner.currency
        entry = await _insert_entry(
            db,
            beneficiary_type="partner",
            partner_id=partner_id,
            source_type="marketplace_purchase",
            source_id=purchase.id,
            rule_id=(snapshot.get("partner_rule_snapshot") or {}).get("rule_id"),
            rule_snapshot=snapshot.get("partner_rule_snapshot")
            or {"from_economics_snapshot": True},
            revenue_base_minor=base,
            share_amount_minor=share,
            currency=entry_currency,
            fx_rate_snapshot=fx_snapshot,
            period=period,
        )
        created += 1 if entry else 0
    return created


async def accrue_refund(db: AsyncSession, purchase_id: str) -> int:
    """Negative adjusted entries referencing the originals."""
    originals = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    RevenueShareEntry.source_type == "marketplace_purchase",
                    RevenueShareEntry.source_id == purchase_id,
                    RevenueShareEntry.adjustment_of_id.is_(None),
                    RevenueShareEntry.share_amount_minor > 0,
                )
            )
        )
        .scalars()
        .all()
    )
    created = 0
    for original in originals:
        entry = await _insert_entry(
            db,
            beneficiary_type=original.beneficiary_type,
            partner_id=original.partner_id,
            beneficiary_org_id=original.beneficiary_org_id,
            source_type=original.source_type,
            source_id=original.source_id,
            rule_id=original.rule_id,
            rule_snapshot=original.rule_snapshot,  # copied — never re-resolved
            revenue_base_minor=-original.revenue_base_minor,
            share_amount_minor=-original.share_amount_minor,
            currency=original.currency,
            period=_now().strftime("%Y-%m"),
            status="adjusted",
            adjustment_of_id=original.id,
        )
        created += 1 if entry else 0
    return created


async def reverse_invoice_accruals(db: AsyncSession, invoice_id: str) -> int:
    """Void-invoice reversal (R56[24]): negate every accrued entry sourced from
    this invoice. Without this, voiding + re-invoicing the same usage accrued
    the partner share twice (invoice.finalized fires again on the re-close).
    Natural-key idempotent via adjustment_of_id, like accrue_refund."""
    originals = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    RevenueShareEntry.source_type == "invoice",
                    RevenueShareEntry.source_id == invoice_id,
                    RevenueShareEntry.adjustment_of_id.is_(None),
                    RevenueShareEntry.share_amount_minor > 0,
                )
            )
        )
        .scalars()
        .all()
    )
    created = 0
    for original in originals:
        entry = await _insert_entry(
            db,
            beneficiary_type=original.beneficiary_type,
            partner_id=original.partner_id,
            beneficiary_org_id=original.beneficiary_org_id,
            source_type=original.source_type,
            source_id=original.source_id,
            rule_id=original.rule_id,
            rule_snapshot=original.rule_snapshot,
            revenue_base_minor=-original.revenue_base_minor,
            share_amount_minor=-original.share_amount_minor,
            currency=original.currency,
            period=_now().strftime("%Y-%m"),
            status="adjusted",
            adjustment_of_id=original.id,
        )
        created += 1 if entry else 0
    return created


async def accrue_credit_note(db: AsyncSession, credit_note_id: str, invoice_id: str) -> int:
    """Credit note → proportional negative adjustment on invoice accruals."""
    from app.controlplane.models.billing import CreditNote

    note = await db.get(CreditNote, credit_note_id)
    invoice = await db.get(Invoice, invoice_id)
    if note is None or invoice is None or invoice.total_minor <= 0:
        return 0
    ratio = Decimal(note.amount_minor) / Decimal(invoice.total_minor)
    originals = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    RevenueShareEntry.source_type == "invoice",
                    RevenueShareEntry.source_id == invoice.id,
                    RevenueShareEntry.adjustment_of_id.is_(None),
                    RevenueShareEntry.share_amount_minor > 0,
                )
            )
        )
        .scalars()
        .all()
    )
    created = 0
    for original in originals:
        delta = -int(
            (Decimal(original.share_amount_minor) * ratio).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        if delta == 0:
            continue
        # R56[28]: the adjustment's base must be in the ENTRY's currency (the
        # partner settlement currency the original was converted to), not the
        # raw invoice-currency note amount. Scale the original's (already
        # converted) base by the same ratio so refunds_minor sums stay
        # currency-consistent on the statement.
        base_delta = -int(
            (Decimal(original.revenue_base_minor) * ratio).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        entry = await _insert_entry(
            db,
            beneficiary_type=original.beneficiary_type,
            partner_id=original.partner_id,
            beneficiary_org_id=original.beneficiary_org_id,
            source_type="invoice_line",  # distinct natural key from the original
            source_id=note.id,
            rule_id=original.rule_id,
            rule_snapshot=original.rule_snapshot,
            revenue_base_minor=base_delta,
            share_amount_minor=delta,
            currency=original.currency,
            period=_now().strftime("%Y-%m"),
            status="adjusted",
            adjustment_of_id=original.id,
        )
        created += 1 if entry else 0
    return created


# ── Statements (ADR-014 §7.3) ────────────────────────────────


async def generate_statement(
    db: AsyncSession,
    *,
    beneficiary_type: str,
    partner_id: str | None,
    beneficiary_org_id: str | None,
    period: str,
    actor: Actor,
) -> SettlementStatement:
    if beneficiary_type == "partner":
        partner = await db.get(Partner, partner_id) if partner_id else None
        if partner is None:
            raise AppError("PARTNER_NOT_FOUND", "Partner not found", 404)
        currency = partner.currency
    else:
        if not beneficiary_org_id:
            raise AppError("VALIDATION_ERROR", "beneficiary_org_id required", 422)
        currency = "USD"  # seller orgs settle in platform currency (v1, ADR)

    existing = (
        await db.execute(
            select(SettlementStatement)
            .where(
                SettlementStatement.beneficiary_type == beneficiary_type,
                (
                    SettlementStatement.partner_id == partner_id
                    if partner_id
                    else SettlementStatement.partner_id.is_(None)
                ),
                (
                    SettlementStatement.beneficiary_org_id == beneficiary_org_id
                    if beneficiary_org_id
                    else SettlementStatement.beneficiary_org_id.is_(None)
                ),
                SettlementStatement.period == period,
            )
            # R73[8]: LOCK the statement row for the whole regenerate — the old
            # read-time status check raced finalize/approve: ops A regenerated
            # while ops B finalized, and A's unguarded total rewrites silently
            # mutated a finalized statement. FOR UPDATE + populate_existing
            # serializes generate against the transition endpoints (which now
            # also contend on this row via their guarded UPDATEs).
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    if existing is not None:
        if existing.status != "draft":
            raise AppError(
                "STATEMENT_STATUS_CONFLICT", "Statement already finalized for this period", 409
            )
        statement = existing
        # Regeneration: unbind previously collected rows
        await db.execute(
            update(RevenueShareEntry)
            .where(RevenueShareEntry.statement_id == statement.id)
            .values(statement_id=None)
        )
    else:
        statement = SettlementStatement(
            beneficiary_type=beneficiary_type,
            partner_id=partner_id,
            beneficiary_org_id=beneficiary_org_id,
            period=period,
            currency=currency,
        )
        db.add(statement)
        await db.flush()

    scope = [
        RevenueShareEntry.beneficiary_type == beneficiary_type,
        (
            RevenueShareEntry.partner_id == partner_id
            if partner_id
            else RevenueShareEntry.partner_id.is_(None)
        ),
        (
            RevenueShareEntry.beneficiary_org_id == beneficiary_org_id
            if beneficiary_org_id
            else RevenueShareEntry.beneficiary_org_id.is_(None)
        ),
        RevenueShareEntry.statement_id.is_(None),
        RevenueShareEntry.status.in_(["accrued", "adjusted"]),
    ]
    # Current-period entries + late adjustments from earlier periods (opening)
    current = (
        (
            await db.execute(
                select(RevenueShareEntry).where(*scope, RevenueShareEntry.period == period)
            )
        )
        .scalars()
        .all()
    )
    late = (
        (
            await db.execute(
                select(RevenueShareEntry).where(*scope, RevenueShareEntry.period < period)
            )
        )
        .scalars()
        .all()
    )
    gross = sum(e.revenue_base_minor for e in current if e.revenue_base_minor > 0)
    refunds = sum(e.revenue_base_minor for e in current if e.revenue_base_minor < 0)
    share_total = sum(e.share_amount_minor for e in current)
    opening = sum(e.share_amount_minor for e in late)
    for e in [*current, *late]:
        e.statement_id = statement.id
    statement.gross_revenue_minor = gross
    statement.refunds_minor = refunds
    statement.share_total_minor = share_total
    statement.opening_adjustments_minor = opening
    statement.net_amount_minor = share_total + opening + statement.manual_adjustments_minor
    await db.flush()
    return statement


_STATEMENT_TRANSITIONS = {
    "finalize": ("draft", "finalized", "settlement.finalized"),
    "approve": ("finalized", "approved", "settlement.approved"),
    "mark-paid": ("approved", "paid_externally", "settlement.marked_paid"),
}


async def transition_statement(
    db: AsyncSession,
    statement: SettlementStatement,
    action: str,
    *,
    actor: Actor,
    external_payment_ref: str | None = None,
) -> SettlementStatement:
    if action not in _STATEMENT_TRANSITIONS:
        raise AppError("VALIDATION_ERROR", f"Unknown action '{action}'", 422)
    expected, target, audit_action = _STATEMENT_TRANSITIONS[action]
    values: dict = {"status": target}
    if action == "finalize":
        values.update(finalized_by=actor.user_id, finalized_at=_now())
    elif action == "approve":
        values.update(approved_by=actor.user_id, approved_at=_now())
    elif action == "mark-paid":
        if not external_payment_ref:
            raise AppError("VALIDATION_ERROR", "external_payment_ref required", 422)
        values.update(external_payment_ref=external_payment_ref)
    result = await db.execute(
        update(SettlementStatement)
        .where(SettlementStatement.id == statement.id, SettlementStatement.status == expected)
        .values(**values)
    )
    if not result.rowcount:
        raise AppError("STATEMENT_STATUS_CONFLICT", "Statement state changed", 409)
    if action == "approve":
        await db.execute(
            update(RevenueShareEntry)
            .where(RevenueShareEntry.statement_id == statement.id)
            .values(status="approved")
        )
    elif action == "mark-paid":
        await db.execute(
            update(RevenueShareEntry)
            .where(RevenueShareEntry.statement_id == statement.id)
            .values(status="settled")
        )
    await record_audit(
        db,
        actor=actor,
        action=audit_action,
        target_type="settlement_statement",
        target_id=statement.id,
        partner_id=statement.partner_id,
        after={"period": statement.period, "net_minor": statement.net_amount_minor},
    )
    await db.refresh(statement)
    return statement


async def adjust_statement(
    db: AsyncSession,
    statement: SettlementStatement,
    *,
    amount_minor: int,
    reason: str,
    actor: Actor,
) -> SettlementStatement:
    from ulid import ULID as _ULID

    # R73[8]: re-read the statement LOCKED — the caller's copy may be stale
    # (concurrent finalize/approve/mark-paid), and the total mutations below
    # must not land on a statement that just left draft/finalized.
    statement = (
        await db.execute(
            select(SettlementStatement)
            .where(SettlementStatement.id == statement.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    if statement.status not in ("draft", "finalized"):
        raise AppError(
            "STATEMENT_STATUS_CONFLICT", "Only draft/finalized statements can be adjusted", 409
        )
    # R50[41]: the natural-key unique index covers (source_type, source_id,
    # beneficiary, adjustment_of_id) — a SECOND manual adjustment on the same
    # statement collided (500). Pre-generate the entry id and self-reference it
    # in adjustment_of_id so every manual adjustment carries a distinct key.
    entry_id = str(_ULID())
    entry = RevenueShareEntry(
        id=entry_id,
        beneficiary_type=statement.beneficiary_type,
        partner_id=statement.partner_id,
        beneficiary_org_id=statement.beneficiary_org_id,
        source_type="manual_adjustment",
        source_id=statement.id,
        rule_snapshot={"manual": True, "reason": reason},
        revenue_base_minor=0,
        share_amount_minor=amount_minor,
        currency=statement.currency,
        period=statement.period,
        status="adjusted",
        statement_id=statement.id,
        adjustment_of_id=entry_id,
    )
    db.add(entry)
    statement.manual_adjustments_minor += amount_minor
    statement.net_amount_minor += amount_minor
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="settlement.adjusted",
        target_type="settlement_statement",
        target_id=statement.id,
        partner_id=statement.partner_id,
        after={"amount_minor": amount_minor},
        reason=reason,
    )
    return statement


# ── Rule lifecycle ───────────────────────────────────────────


async def activate_rule(db: AsyncSession, rule: RevenueShareRule, *, actor: Actor):
    if rule.status != "draft":
        raise AppError("RULE_IMMUTABLE", "Only draft rules can be activated", 409)
    # Retire the previous active version of the same dimension set
    retired = await db.execute(
        update(RevenueShareRule)
        .where(
            RevenueShareRule.beneficiary_type == rule.beneficiary_type,
            (
                RevenueShareRule.partner_id == rule.partner_id
                if rule.partner_id
                else RevenueShareRule.partner_id.is_(None)
            ),
            RevenueShareRule.revenue_type == rule.revenue_type,
            (
                RevenueShareRule.tenant_id == rule.tenant_id
                if rule.tenant_id
                else RevenueShareRule.tenant_id.is_(None)
            ),
            (
                RevenueShareRule.plan_id == rule.plan_id
                if rule.plan_id
                else RevenueShareRule.plan_id.is_(None)
            ),
            (
                RevenueShareRule.listing_id == rule.listing_id
                if rule.listing_id
                else RevenueShareRule.listing_id.is_(None)
            ),
            # country is part of the rule's identity (uq_cp_revshare_rule_version,
            # rule_specificity +1 dim, resolved via tenant.country) — omitting it
            # here made activating a v2 for one country wrongly retire the active
            # rule of EVERY other country in the same dimension set (R35/C26).
            (
                RevenueShareRule.country == rule.country
                if rule.country
                else RevenueShareRule.country.is_(None)
            ),
            RevenueShareRule.status == "active",
        )
        .values(status="retired", effective_until=rule.effective_from)
        .returning(RevenueShareRule.id, RevenueShareRule.version)
    )
    retired_rows = retired.all()
    result = await db.execute(
        update(RevenueShareRule)
        .where(RevenueShareRule.id == rule.id, RevenueShareRule.status == "draft")
        .values(status="active")
    )
    if not result.rowcount:
        raise AppError("RULE_IMMUTABLE", "Rule state changed concurrently", 409)
    # R60[41]: each retirement is a payout-affecting transition in its own
    # right — audit it with the RETIRED rule as the target (the activation
    # event below only carries the new rule's id).
    for retired_id, retired_version in retired_rows:
        await record_audit(
            db,
            actor=actor,
            action="revshare.rule_retired",
            target_type="revshare_rule",
            target_id=retired_id,
            partner_id=rule.partner_id,
            after={"version": retired_version, "superseded_by": rule.id},
        )
    await record_audit(
        db,
        actor=actor,
        action="revshare.rule_activated",
        target_type="revshare_rule",
        target_id=rule.id,
        partner_id=rule.partner_id,
        after={"version": rule.version, "rule_type": rule.rule_type},
    )
    await db.refresh(rule)
    return rule


# ── Outbox handlers ──────────────────────────────────────────


@register_handler("invoice.finalized")
async def _handle_invoice_finalized(db: AsyncSession, payload: dict) -> None:
    await accrue_for_invoice(db, payload["invoice_id"])


@register_handler("purchase.paid")
async def _handle_purchase_paid(db: AsyncSession, payload: dict) -> None:
    await accrue_for_purchase(db, payload["purchase_id"])


@register_handler("purchase.refunded")
async def _handle_purchase_refunded(db: AsyncSession, payload: dict) -> None:
    await accrue_refund(db, payload["purchase_id"])


@register_handler("credit_note.applied")
async def _handle_credit_note(db: AsyncSession, payload: dict) -> None:
    await accrue_credit_note(db, payload["credit_note_id"], payload["invoice_id"])
