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
