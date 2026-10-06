"""Experiment webhook emission tests (ADR-017 §4.18, round 284).

Org-scoped experiments fire tenant webhooks on status transitions and
decisions; platform-wide experiments never fan out (containment); a
delivery failure never breaks the caller (fail-safe).

Runs against the dev Postgres; rollback-per-test.
"""

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.models.user import User, UserRole, UserStatus

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture
def captured(monkeypatch):
    """Capture trigger_event calls; the webhook service itself is not under
    test here (it has its own suite) — the WIRE is."""
    calls: list[tuple[str, str, dict]] = []

    async def _fake(self, org_id, event_type, payload):
        calls.append((org_id, event_type, payload))

    from app.services.webhook import WebhookService

    monkeypatch.setattr(WebhookService, "trigger_event", _fake)
    return calls


def _spec() -> dict:
    return {
        "hypothesis": "webhooks fire on the org-scoped lifecycle",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "guardrails": [
                {"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}
            ],
        },
    }


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-wh-{ULID()}@example.com",
        display_name="W",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(db, *, org_scoped: bool):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    admin = await _mk_admin(db)
    scope_org_id = None
    if org_scoped:
        tenant = TenantAccount(name=f"wh-{str(ULID()).lower()}",
                               slug=f"wh-{str(ULID()).lower()}")
        db.add(tenant)
        await db.flush()
        org = Organization(name="wh", slug=f"wh-{str(ULID()).lower()}",
                           tenant_id=tenant.id)
        db.add(org)
        await db.flush()
        scope_org_id = org.id
    layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id, scope_org_id=scope_org_id,
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    return exp, admin, scope_org_id


async def test_org_scoped_transition_fires_status_changed(db, captured):
    exp, _admin, org_id = await _mk_running(db, org_scoped=True)
    assert [c[1] for c in captured] == ["experiment.status_changed"] * 3
    last_org, _etype, payload = captured[-1]
    assert last_org == org_id
    assert payload["experiment_id"] == exp.id
    assert payload["experiment_key"] == exp.key
    assert payload["from_status"] == "scheduled"
    assert payload["to_status"] == "running"


async def test_platform_wide_experiment_never_fans_out(db, captured):
    await _mk_running(db, org_scoped=False)
    assert captured == []  # containment: no tenant sees platform lifecycle


async def test_delivery_failure_never_breaks_transition(db, monkeypatch):
    async def _boom(self, org_id, event_type, payload):
        raise RuntimeError("delivery exploded")

    from app.services.webhook import WebhookService

    monkeypatch.setattr(WebhookService, "trigger_event", _boom)
    exp, _admin, _ = await _mk_running(db, org_scoped=True)
    assert (await ExperimentService(db).get(exp.id)).status == "running"
