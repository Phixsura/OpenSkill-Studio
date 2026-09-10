"""Control-plane pure-logic unit tests (no DB, no network).

Extended by each phase: quota math (P2), rating math (P4), proration (P6),
economics split (P8), hostname normalization (P10), etc.
"""

import pytest

from app.controlplane.models.tenant import (
    TENANT_BLOCKED_STATUSES,
    TENANT_TRANSITIONS,
    TenantStatus,
)
from app.controlplane.services.audit import AUDIT_ACTIONS, TENANT_VISIBLE_ACTIONS

# ── P1: tenant state machine ─────────────────────────────────


def test_transition_map_covers_all_statuses():
    assert set(TENANT_TRANSITIONS.keys()) == set(TenantStatus)


def test_archived_is_terminal():
    assert TENANT_TRANSITIONS[TenantStatus.ARCHIVED] == set()


def test_no_self_transitions():
    for src, targets in TENANT_TRANSITIONS.items():
        assert src not in targets


def test_suspended_can_only_reactivate_or_cancel():
    assert TENANT_TRANSITIONS[TenantStatus.SUSPENDED] == {
        TenantStatus.ACTIVE,
        TenantStatus.CANCELLED,
    }


def test_blocked_statuses_are_consumption_blocking():
    assert TenantStatus.SUSPENDED in TENANT_BLOCKED_STATUSES
    assert TenantStatus.CANCELLED in TENANT_BLOCKED_STATUSES
    assert TenantStatus.ARCHIVED in TENANT_BLOCKED_STATUSES
    # PAST_DUE and TRIAL are working accounts
    assert TenantStatus.PAST_DUE not in TENANT_BLOCKED_STATUSES
    assert TenantStatus.TRIAL not in TENANT_BLOCKED_STATUSES


# ── P1: audit registry ───────────────────────────────────────


def test_audit_actions_are_dotted_and_lowercase():
    for action in AUDIT_ACTIONS:
        assert "." in action
        assert action == action.lower()
        assert len(action) <= 60


def test_tenant_visible_is_strict_subset():
    assert TENANT_VISIBLE_ACTIONS < AUDIT_ACTIONS


def test_platform_only_actions_hidden_from_tenants():
    # Internal cost / settlement / impersonation actions must never be
    # visible through the tenant-scoped audit endpoint.
    for action in (
        "pricing.cost_rate_created",
        "fx.rate_created",
        "settlement.approved",
        "impersonation.grant_created",
        "impersonation.token_minted",
    ):
        assert action in AUDIT_ACTIONS
        assert action not in TENANT_VISIBLE_ACTIONS


@pytest.mark.asyncio
async def test_record_audit_rejects_unregistered_action():
    from app.controlplane.services.audit import SYSTEM_ACTOR, record_audit

    with pytest.raises(ValueError, match="Unregistered audit action"):
        await record_audit(
            None,  # db unused before validation
            actor=SYSTEM_ACTOR,
            action="tenant.definitely_not_registered",
            target_type="tenant",
            target_id="01JFAKEFAKEFAKEFAKEFAKEFAK",
        )


def test_every_recorded_action_literal_is_registered():
    """R24 drift guard: every `action="x.y"` literal passed to record_audit
    across the control-plane services is in AUDIT_ACTIONS — a new call site
    with an unregistered action would blow up at runtime, so catch it here."""
    import pathlib
    import re

    svc_dir = pathlib.Path(__file__).resolve().parent.parent / "app" / "controlplane" / "services"
    literals: set[str] = set()
    for f in svc_dir.glob("*.py"):
        for m in re.finditer(r'action="([a-z_]+\.[a-z_]+)"', f.read_text()):
            literals.add(m.group(1))
    assert literals, "no action literals found — scan path wrong?"
    unregistered = literals - AUDIT_ACTIONS
    assert not unregistered, f"unregistered audit actions in call sites: {unregistered}"


# ── P1: impersonation guard path rules ───────────────────────


def test_impersonation_write_whitelist_is_tight():
    from app.middleware.impersonation import _WRITE_WHITELIST

    allowed = [
        "/api/v1/notifications/01JXXXXXXXXXXXXXXXXXXXXXXX/read",
        "/api/v1/notifications/read-all",
    ]
    blocked = [
        "/api/v1/orgs",
        "/api/v1/auth/change-password",
        "/api/v1/tenants/01J/members",
        "/api/v1/providers/credentials",
        "/api/v1/notifications/read-all/extra",  # no prefix-match tricks
    ]
    for path in allowed:
        assert any(rx.match(path) for rx in _WRITE_WHITELIST), path
    for path in blocked:
        assert not any(rx.match(path) for rx in _WRITE_WHITELIST), path


# ── P1: entitlement registry (interim engine) ────────────────


def test_entitlement_defs_have_valid_types():
    from app.controlplane.services.entitlements import ENTITLEMENT_DEFS

    for key, d in ENTITLEMENT_DEFS.items():
        assert d.key == key
        assert d.type in ("bool", "int", "decimal")
        if d.type == "bool":
            assert isinstance(d.default, bool)
            assert not d.soft_capable  # soft only makes sense for numerics


# ── R1/R2: numeric-overflow input guards (adversarial regression) ──
# Every money/rate field bound at the SCHEMA so an over-range value is a
# clean 422, never a BIGINT/Numeric overflow 500 at the write boundary.


def test_money_fields_reject_over_int8():
    from pydantic import ValidationError

    from app.controlplane.api.billing import CreditNoteRequest, RecordPaymentRequest
    from app.controlplane.api.credits import (
        AdjustCreditRequest,
        BudgetPolicyRequest,
        GrantPromoRequest,
    )

    big = 10**19  # > int8 max (9.2e18)
    with pytest.raises(ValidationError):
        AdjustCreditRequest(amount_minor=big, currency="USD", reason="over")
    with pytest.raises(ValidationError):
        AdjustCreditRequest(amount_minor=-big, currency="USD", reason="under")
    with pytest.raises(ValidationError):
        GrantPromoRequest(
            amount_minor=big, currency="USD", expires_at="2027-01-01T00:00:00Z", reason="over"
        )
    with pytest.raises(ValidationError):
        BudgetPolicyRequest(scope_type="tenant", period="monthly", limit_minor=big, currency="USD")
    with pytest.raises(ValidationError):
        RecordPaymentRequest(amount_minor=big, method="other")
    with pytest.raises(ValidationError):
        CreditNoteRequest(amount_minor=big, reason="over")
    # A legitimate amount still passes
    AdjustCreditRequest(amount_minor=19900, currency="USD", reason="fine")


def test_decimal_string_fields_reject_nan_and_overflow():
    from pydantic import ValidationError

    from app.controlplane.api.partners import CreateRuleRequest
    from app.controlplane.api.pricing import (
        CreateCostRateRequest,
        CreateFxRateRequest,
        CreateReconReportRequest,
    )

    def cost(uc):
        return CreateCostRateRequest(
            provider="p",
            usage_type="image_generation",
            unit="images",
            currency="USD",
            unit_cost=uc,
            effective_from="2026-01-01T00:00:00Z",
        )

    # Numeric(18,8): integer part must stay < 10^10
    for bad in ("NaN", "Infinity", "9" * 30, "-1"):
        with pytest.raises((ValidationError, ValueError)):
            cost(bad)
    cost("0.018")  # ok

    def fx(rate):
        return CreateFxRateRequest(
            base_currency="USD",
            quote_currency="EUR",
            rate=rate,
            effective_from="2026-01-01T00:00:00Z",
        )

    for bad in ("NaN", "0", "-1", "9" * 30):
        with pytest.raises((ValidationError, ValueError)):
            fx(bad)
    fx("7.12")

    def rule(rate):
        return CreateRuleRequest(
            beneficiary_type="seller_org",
            revenue_type="all",
            rule_type="percentage_of_gross_revenue",
            rate=rate,
            effective_from="2026-01-01T00:00:00Z",
        )

    # Numeric(9,6): integer part < 10^3
    for bad in ("NaN", "9" * 15, "-1"):
        with pytest.raises((ValidationError, ValueError)):
            rule(bad)
    rule("10.5")

    def recon(qty):
        return CreateReconReportRequest(
            provider="p",
            usage_type="image_generation",
            period="2026-08",
            provider_reported_quantity=qty,
            provider_reported_cost_minor=1,
            currency="USD",
        )

    for bad in ("NaN", "Infinity", "9" * 20, "-1"):
        with pytest.raises((ValidationError, ValueError)):
            recon(bad)
    recon("1834")


# ── R49[39]: workflow-run quota month window is tenant-tz ────


def test_tenant_month_start_uses_tenant_timezone():
    from datetime import UTC, datetime

    from app.services.workflow_runtime import _tenant_month_start

    # 2026-08-31 23:00 UTC = 2026-09-01 11:00 in Auckland (NZST, UTC+12) —
    # Auckland is already in September, so its month started Aug 31 12:00 UTC.
    at = datetime(2026, 8, 31, 23, 0, tzinfo=UTC)
    nz = _tenant_month_start("Pacific/Auckland", at)
    assert nz == datetime(2026, 8, 31, 12, 0, tzinfo=UTC)
    # The same instant in UTC is still August.
    utc = _tenant_month_start("UTC", at)
    assert utc == datetime(2026, 8, 1, 0, 0, tzinfo=UTC)
    # US/Pacific (UTC-7 PDT) is Aug 31 16:00 local — month started Aug 1 07:00 UTC.
    la = _tenant_month_start("America/Los_Angeles", at)
    assert la == datetime(2026, 8, 1, 7, 0, tzinfo=UTC)
    # Bad tz name falls back to UTC instead of crashing.
    bad = _tenant_month_start("Not/AZone", at)
    assert bad == utc


def test_manual_invoice_line_quantity_bound_validated():
    """R129[L0]: quantity is written verbatim into a Numeric(18,6) column —
    non-numeric crashes at flush (asyncpg DataError → 500 past the R88
    backstop) and 'NaN' is silently STORED and rendered NaN in the FE."""
    from pydantic import ValidationError

    from app.controlplane.api.billing import ManualInvoiceLineInput

    ok = ManualInvoiceLineInput(description="consulting", amount_minor=50000, quantity="2.5")
    # R130[29]: normalized to the column's scale — the stored value is what
    # gets validated (and returned), not the raw string.
    assert ok.quantity == "2.500000"
    for bad in (
        "two",
        "1,5",
        "NaN",
        "Infinity",
        "-Infinity",
        "0",
        "-3",
        "1e13",
        # R130[29]: quantizes to 0.000000 at the column's scale — a stored
        # zero the raw >0 check missed.
        "0.0000001",
        # R130[29]: passes raw bounds but asyncpg cannot encode it.
        "1E-20000",
    ):
        with pytest.raises(ValidationError):
            ManualInvoiceLineInput(description="x", amount_minor=1, quantity=bad)


def test_tenant_own_actions_are_tenant_visible():
    """R186: subscription.reactivated is emitted by the tenant's OWN
    reactivate action (billing page) but was filtered from the tenant-scoped
    audit endpoint — the tenant's timeline showed a cancel with no follow-up
    while the subscription was live again. Same for member add/remove
    (tenant-console actions)."""
    for action in (
        "subscription.reactivated",
        "tenant.member_added",
        "tenant.member_removed",
    ):
        assert action in AUDIT_ACTIONS
        assert action in TENANT_VISIBLE_ACTIONS, f"{action} is a tenant-own action"


# ── R208: validation-guard reject-branch coverage (branch-gap analysis) ──
# validate_policy_params (every pricing-policy create) and
# validate_entitlement_value (every plan-version/override write) are the
# pure entry gates for money-shaping config. Branch analysis showed their
# REJECT arcs largely untested — a weakened guard would let a divide-by-zero
# per_quantity, an int8-overflowing price, an unknown-key smuggle, or a
# negative/NaN entitlement into stored config that corrupts rating forever.


def test_validate_policy_params_rejects():
    from app.controlplane.services.pricing import validate_policy_params

    def rejects(pt, params):
        import pytest as _p

        from app.exceptions import AppError
        with _p.raises(AppError) as e:
            validate_policy_params(pt, params)
        assert e.value.code == "INVALID_POLICY_PARAMS"

    rejects("no_such_type", {})                                   # unknown policy type
    rejects("cost_plus_percentage", {"percentage": -1})           # negative dec
    rejects("cost_plus_percentage", {"percentage": "NaN"})        # non-finite
    rejects("cost_plus_percentage", {})                           # missing required key
    rejects("cost_plus_fixed", {"fixed_markup_minor": -5})        # negative int
    rejects("cost_plus_fixed", {"fixed_markup_minor": True})      # bool-is-not-int
    rejects("cost_plus_fixed", {"fixed_markup_minor": 10**16})    # int8 overflow ceiling
    rejects("cost_plus_fixed", {"fixed_markup_minor": 1, "per_quantity": 0})   # divide-by-zero
    rejects("fixed_unit_price", {"unit_price_minor": 1, "per_quantity": -2})   # negative divisor
    rejects("cost_plus_percentage", {"percentage": 5, "junk": 1})  # unknown key smuggle
    rejects("cost_plus_percentage", {"percentage": 5, "exclude_failed": "yes"})  # non-bool flag

    # positive controls — valid params pass and round-trip
    for pt, ok in [
        ("cost_plus_percentage", {"percentage": 20}),
        ("cost_plus_fixed", {"fixed_markup_minor": 500, "per_quantity": 1000}),
        ("fixed_unit_price", {"unit_price_minor": 30}),
        ("included_quota_then_overage", {"included_quota": 100, "overage_unit_price_minor": 5}),
    ]:
        assert validate_policy_params(pt, ok) == ok


def test_validate_entitlement_value_rejects():
    from app.controlplane.services.entitlements import validate_entitlement_value
    from app.exceptions import AppError

    def rejects(key, val):
        import pytest as _p
        with _p.raises(AppError) as e:
            validate_entitlement_value(key, val)
        assert e.value.code == "UNKNOWN_ENTITLEMENT"

    rejects("no_such_key", 1)                       # unknown entitlement
    rejects("custom_domain", None)                  # bool cannot be null
    rejects("custom_domain", 1)                     # bool expects bool
    rejects("max_organizations", -1)                # int non-negative
    rejects("max_organizations", True)              # bool-is-not-int
    rejects("max_organizations", "5")               # int expects int, not str
    rejects("max_storage_gb", -0.5)                 # decimal non-negative
    rejects("max_storage_gb", "NaN")                # non-finite decimal
    rejects("max_storage_gb", "not-a-number")       # unparseable decimal

    # positive controls incl. the numeric-None-is-unlimited path
    assert validate_entitlement_value("custom_domain", True) is True
    assert validate_entitlement_value("max_organizations", 25) == 25
    assert validate_entitlement_value("max_storage_gb", None) is None      # unlimited
    assert validate_entitlement_value("max_storage_gb", "5.5") == "5.5"


# ── R209: rating pure-function guard coverage (branch-gap analysis) ──
# compute_billable_minor / compute_billable_exact are the per-policy-type
# rating kernels called at rate time on STORED policy params (validate runs
# at create, but a corrupted/legacy row or a bypassed create path reaches
# these). Their per_quantity<=0, unknown-type, exclude_failed, and
# included-quota branches were coverage gaps — each is a divide-by-zero or
# silent-mis-bill sentinel.


def test_compute_billable_guards():
    from decimal import Decimal

    from app.controlplane.services.rating import (
        compute_billable_exact,
        compute_billable_minor,
    )
    from app.exceptions import AppError

    def rejects(fn, pt, params, **kw):
        import pytest as _p
        base = dict(internal_cost_minor=1000, quantity=Decimal(5)) if fn is compute_billable_minor \
            else dict(internal_cost_exact=Decimal(1000), quantity=Decimal(5))
        base.update(kw)
        with _p.raises(AppError) as e:
            fn(pt, params, **base)
        assert e.value.code == "INVALID_POLICY_PARAMS"

    for fn in (compute_billable_minor, compute_billable_exact):
        # per_quantity <= 0 → divide-by-zero guard, all three per-based types
        rejects(fn, "cost_plus_fixed", {"fixed_markup_minor": 100, "per_quantity": 0})
        rejects(fn, "fixed_unit_price", {"unit_price_minor": 30, "per_quantity": -1})
        rejects(fn, "included_quota_then_overage",
                {"included_quota": 10, "overage_unit_price_minor": 5, "per_quantity": 0})
        # unknown policy type → terminal raise
        rejects(fn, "no_such_policy", {})

    # exclude_failed short-circuits to 0 on a failed event (both fns)
    assert compute_billable_minor(
        "cost_plus_percentage", {"percentage": 50, "exclude_failed": True},
        internal_cost_minor=1000, quantity=Decimal(1),
        usage_metadata={"status": "failed"},
    ) == 0
    assert compute_billable_exact(
        "cost_plus_percentage", {"percentage": 50, "exclude_failed": True},
        internal_cost_exact=Decimal(1000), quantity=Decimal(1),
        usage_metadata={"status": "failed"},
    ) == Decimal(0)

    # included_quota_then_overage: prior usage already past quota → only the
    # NEW increment over quota is billed (branch that computes already_over)
    billed = compute_billable_minor(
        "included_quota_then_overage",
        {"included_quota": 100, "overage_unit_price_minor": 10},
        internal_cost_minor=0, quantity=Decimal(50), prior_period_quantity=Decimal(120),
    )
    assert billed == 500  # all 50 new units are over quota → 50*10
    partial = compute_billable_minor(
        "included_quota_then_overage",
        {"included_quota": 100, "overage_unit_price_minor": 10},
        internal_cost_minor=0, quantity=Decimal(50), prior_period_quantity=Decimal(80),
    )
    assert partial == 300  # 80→130 crosses at 100: only 30 units over → 30*10


# ── R223: revenue_share pure-function coverage (specificity + share math) ──


def test_rule_specificity_scoring():
    """rule_specificity: tenant+8|plan+4|listing+2|country+1, None on any
    dimension mismatch. Precise weights were never asserted — a swapped
    constant silently reorders which rev-share rule wins."""
    from types import SimpleNamespace

    from app.controlplane.services.revenue_share import rule_specificity

    def rule(**kw):
        base = dict(tenant_id=None, plan_id=None, listing_id=None, country=None)
        base.update(kw)
        return SimpleNamespace(**base)

    ctx = dict(tenant_id="T", plan_id="P", listing_id="L", country="US")
    # global rule (no dimensions) scores 0
    assert rule_specificity(rule(), **ctx) == 0
    # each dimension's exact weight
    assert rule_specificity(rule(tenant_id="T"), **ctx) == 8
    assert rule_specificity(rule(plan_id="P"), **ctx) == 4
    assert rule_specificity(rule(listing_id="L"), **ctx) == 2
    assert rule_specificity(rule(country="US"), **ctx) == 1
    # all four → 15, and tenant outweighs plan+listing+country (8 > 4+2+1=7)
    assert rule_specificity(rule(tenant_id="T", plan_id="P", listing_id="L", country="US"), **ctx) == 15
    # any mismatch → None (rule does not apply)
    assert rule_specificity(rule(tenant_id="OTHER"), **ctx) is None
    assert rule_specificity(rule(plan_id="OTHER"), **ctx) is None
    assert rule_specificity(rule(listing_id="OTHER"), **ctx) is None
    assert rule_specificity(rule(country="CA"), **ctx) is None


def test_compute_share_minor_by_type():
    """compute_share_minor: percentage types use rate×base/100; fixed types
    use amount×units; unknown type raises. Rounding is HALF_UP."""
    from decimal import Decimal

    from app.controlplane.services.revenue_share import compute_share_minor
    from app.exceptions import AppError

    # 30% of 10000 = 3000
    assert compute_share_minor("percentage_of_gross_revenue",
                               rate=Decimal(30), amount_minor=None, base_minor=10000) == 3000
    # HALF_UP rounding: 33% of 101 = 33.33 → 33
    assert compute_share_minor("percentage_of_net_revenue",
                               rate=Decimal(33), amount_minor=None, base_minor=101) == 33
    # fixed per seat: 500 × 7 units = 3500
    assert compute_share_minor("fixed_amount_per_seat",
                               rate=None, amount_minor=500, base_minor=0, units=Decimal(7)) == 3500
    import pytest as _p
    with _p.raises(AppError) as e:
        compute_share_minor("bogus_type", rate=None, amount_minor=0, base_minor=0)
    assert e.value.code == "RULE_PARAM_INVALID"


# ── R224: Stripe unit-amount conversion (the R81 100x-JPY critical path) ──


def test_stripe_unit_amount_by_currency_class():
    """_stripe_unit_amount recovers major from platform minor then re-expresses
    in Stripe's convention. R81 was a 100x over-credit when JPY (zero-decimal,
    platform minor==major) was ×100'd into Stripe. Pin every currency class
    AND the round-trip identity against _platform_minor_from_stripe."""
    from app.controlplane.services.billing_providers.stripe import (
        _platform_minor_from_stripe,
        _stripe_unit_amount,
    )

    # USD: platform 500 minor ($5.00) → Stripe 500 (cents). Identity factor.
    assert _stripe_unit_amount(500, "USD") == 500
    # JPY zero-decimal: platform 5000 minor (¥5000, minor==major) → Stripe 5000,
    # NOT 500000 (the R81 bug: ×100 on an already-whole-yen amount).
    assert _stripe_unit_amount(5000, "JPY") == 5000
    assert _stripe_unit_amount(5000, "jpy") == 5000  # case-insensitive (R81 root)
    # KWD three-decimal: platform 1500 minor (KWD 15.00, ×100) → Stripe 15000 (×1000)
    assert _stripe_unit_amount(1500, "KWD") == 15000

    # Round-trip identity across all three classes
    for cur, minor in [("USD", 12345), ("JPY", 9999), ("KWD", 45600), ("EUR", 100)]:
        stripe_amt = _stripe_unit_amount(minor, cur)
        assert _platform_minor_from_stripe(stripe_amt, cur) == minor, cur
