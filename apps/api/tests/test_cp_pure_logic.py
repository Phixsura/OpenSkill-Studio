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
