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

    async def _fake(self, org_id, event_type, payload, **kw):
        calls.append((org_id, event_type, payload))

    from app.services.webhook import WebhookService

    monkeypatch.setattr(WebhookService, "trigger_event", _fake)
    return calls


def _spec(guardrails: list[dict] | None = None) -> dict:
    return {
        "hypothesis": "webhooks fire on the org-scoped lifecycle",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "guardrails": guardrails
            if guardrails is not None
            else [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
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


async def _mk_running(db, *, org_scoped: bool,
                      guardrails: list[dict] | None = None):
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
    await svc.create_version(exp.id, spec=_spec(guardrails), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
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
    async def _boom(self, org_id, event_type, payload, **kw):
        raise RuntimeError("delivery exploded")

    from app.services.webhook import WebhookService

    monkeypatch.setattr(WebhookService, "trigger_event", _boom)
    exp, _admin, _ = await _mk_running(db, org_scoped=True)
    assert (await ExperimentService(db).get(exp.id)).status == "running"


async def test_guardrail_breach_emits_detail_then_pause(db, captured):
    """Round 285: the breach wire — detail event BEFORE the pause's
    status_changed, both to the owning org only."""
    from app.experiments.services.assignment import AssignmentService
    from app.experiments.services.guardrails import GuardrailService
    from app.experiments.services.metrics import MetricService

    await MetricService(db).ensure_seed_definitions()
    exp, _admin, org_id = await _mk_running(
        db, org_scoped=True,
        guardrails=[{"metric_key": "exposure_rate", "op": "lte",
                     "threshold": 0.4, "window_hours": 24}],
    )
    captured.clear()  # drop the lifecycle transitions; the breach is under test
    asvc = AssignmentService(db)
    for i in range(10):
        ctx = {"org_id": org_id}  # org-scoped eligibility needs org context
        r = await asvc.resolve(experiment_key=exp.key, unit_type="user",
                               unit_id=f"wh-{i}", context=ctx)
        assert r is not None
        await asvc.record_exposure(experiment_key=exp.key, unit_type="user",
                                   unit_id=f"wh-{i}", context=ctx)
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"]
    kinds = [c[1] for c in captured]
    assert kinds == ["experiment.guardrail_breach", "experiment.status_changed"]
    breach_org, _t, breach_payload = captured[0]
    assert breach_org == org_id
    assert breach_payload["action"] == "paused"
    assert breach_payload["breaches"][0]["metric_key"] == "exposure_rate"
    _o, _t2, pause_payload = captured[1]
    assert pause_payload["from_status"] == "running"
    assert pause_payload["to_status"] == "paused"


async def test_unmocked_trigger_path_subscribes_filters_delivers(db, monkeypatch):
    """Round 286: drop the trigger_event mock — the REAL path must accept an
    experiment.* subscription (whitelist), pass the tenant entitlement gate,
    match by event-type filter, and schedule delivery (HTTP layer mocked)."""
    import asyncio

    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.controlplane.services.entitlements import invalidate_cache
    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    admin = await _mk_admin(db)
    org = await OrgService(db).create(
        name=f"WHX {ULID()}", slug=f"whx-{str(ULID()).lower()}",
        description=None, created_by=admin.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)

    svc = WebhookService(db)
    # subscription CREATE must accept the new experiment.* types (whitelist)
    sub_decisions = await svc.create(
        org_id=org.id, url="https://example.com/exp-hook",
        events=["experiment.decision_recorded"],
    )
    sub_status = await svc.create(
        org_id=org.id, url="https://example.com/status-hook",
        events=["experiment.status_changed"],
    )

    scheduled: list[tuple[str, str]] = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append((webhook_id, event_type))

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    await emit_experiment_event(
        db, scope_org_id=org.id,
        event_type="experiment.decision_recorded",
        payload={"experiment_id": "x", "decision": "promote"},
    )
    await asyncio.sleep(0.05)
    # #80 (round 290): BEFORE the commit nothing may leave the building —
    # a rollback after this point must leak no phantom event
    assert scheduled == []
    try:
        await db.commit()
        await asyncio.sleep(0.05)  # fire-and-forget task
        # the decision sub got it; the status-only sub was filtered out
        assert scheduled == [(sub_decisions.id, "experiment.decision_recorded")]
        assert sub_status.id not in [w for w, _ in scheduled]
    finally:
        # the commit persisted real rows — sweep them (tenant cascades org,
        # org cascades subscriptions/memberships)
        from app.controlplane.models.tenant import TenantAccount as TenantAcc
        from app.models.organization import Organization as OrgModel

        org_row = await db.get(OrgModel, org.id)
        if org_row is not None:
            await db.delete(org_row)  # cascades subscriptions + memberships
            await db.flush()
        tenant_row = await db.get(TenantAcc, org.tenant_id)
        if tenant_row is not None:
            await db.delete(tenant_row)
        admin_row = await db.get(User, admin.id)
        if admin_row is not None:
            await db.delete(admin_row)
        await db.commit()


async def test_rollback_leaks_no_phantom_webhook(db, monkeypatch):
    """#80 (round 290): the caller's transaction rolls back — the webhook
    must never have left. Kill-proof for defer_until_commit."""
    import asyncio

    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.controlplane.services.entitlements import invalidate_cache
    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    admin = await _mk_admin(db)
    org = await OrgService(db).create(
        name=f"WHR {ULID()}", slug=f"whr-{str(ULID()).lower()}",
        description=None, created_by=admin.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)
    svc = WebhookService(db)
    await svc.create(org_id=org.id, url="https://example.com/ghost",
                     events=["experiment.decision_recorded"])

    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(webhook_id)

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    await emit_experiment_event(
        db, scope_org_id=org.id,
        event_type="experiment.decision_recorded",
        payload={"experiment_id": "ghost", "decision": "promote"},
    )
    await db.rollback()  # the decision never happened
    await asyncio.sleep(0.05)
    assert scheduled == [], "rollback must not leak a phantom webhook"


async def test_rollback_then_later_commit_fires_no_stale_webhook(db, monkeypatch):
    """#81 (round 291, #80's second act): the after_commit once-listener
    survives a rollback — if the SAME session then commits unrelated later
    work (the retry pattern), the rolled-back transaction's phantom event
    fired anyway. The listener must cancel on rollback."""
    import asyncio

    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.controlplane.services.entitlements import invalidate_cache
    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    admin = await _mk_admin(db)
    org = await OrgService(db).create(
        name=f"WHS {ULID()}", slug=f"whs-{str(ULID()).lower()}",
        description=None, created_by=admin.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)
    svc = WebhookService(db)
    await svc.create(org_id=org.id, url="https://example.com/stale",
                     events=["experiment.decision_recorded"])

    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(event_type)

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    # capture plain ids BEFORE commit — expired ORM attrs would lazy-load
    org_id_s, tenant_id_s, admin_id_s = org.id, org.tenant_id, admin.id
    # commit the fixture FIRST so the rollback below only drops the emit's txn
    await db.commit()
    try:
        await emit_experiment_event(
            db, scope_org_id=org_id_s,
            event_type="experiment.decision_recorded",
            payload={"experiment_id": "stale", "decision": "promote"},
        )
        await db.rollback()  # attempt 1 failed
        # attempt 2: unrelated later work on the SAME session commits
        # (re-fetch: the rollback expired the ORM objects)
        tenant2 = await db.get(TenantAccount, tenant_id_s)
        tenant2.status = TenantStatus.ACTIVE  # no-op write to have a txn
        await db.flush()
        await db.commit()
        await asyncio.sleep(0.05)
        assert scheduled == [], (
            "a rolled-back emission must not ride a LATER commit"
        )
    finally:
        from app.models.organization import Organization as OrgModel2

        org_row = await db.get(OrgModel2, org_id_s)
        if org_row is not None:
            await db.delete(org_row)
            await db.flush()
        tenant_row = await db.get(TenantAccount, tenant_id_s)
        if tenant_row is not None:
            await db.delete(tenant_row)
        admin_row = await db.get(User, admin_id_s)
        if admin_row is not None:
            await db.delete(admin_row)
        await db.commit()


async def test_emit_inside_savepoint_warns_loudly(db, monkeypatch):
    """Round 293 (the #80/#81 boundary): after_commit fires at the OUTER
    commit only, so an emit inside a begin_nested savepoint that later
    rolls back would still deliver. No caller does this today — the
    defensive warning must fire so a future one is caught in logs."""
    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.controlplane.services.entitlements import invalidate_cache
    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    admin = await _mk_admin(db)
    org = await OrgService(db).create(
        name=f"WHN {ULID()}", slug=f"whn-{str(ULID()).lower()}",
        description=None, created_by=admin.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)
    await WebhookService(db).create(
        org_id=org.id, url="https://example.com/sp",
        events=["experiment.decision_recorded"],
    )

    from structlog.testing import capture_logs

    with capture_logs() as cap:
        async with db.begin_nested():
            await emit_experiment_event(
                db, scope_org_id=org.id,
                event_type="experiment.decision_recorded",
                payload={"experiment_id": "sp"},
            )
    assert any(e["event"] == "webhook_defer_inside_savepoint" for e in cap), cap


async def _wh_fixture(db):
    """Org + ACTIVE tenant + one decision-event subscription; plain ids."""
    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.controlplane.services.entitlements import invalidate_cache
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    admin = await _mk_admin(db)
    org = await OrgService(db).create(
        name=f"WSP {ULID()}", slug=f"wsp-{str(ULID()).lower()}",
        description=None, created_by=admin.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)
    await WebhookService(db).create(
        org_id=org.id, url="https://example.com/sp",
        events=["experiment.decision_recorded"],
    )
    return org.id, org.tenant_id, admin.id


async def _wh_sweep(db, org_id, tenant_id, admin_id):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization as OrgM

    org_row = await db.get(OrgM, org_id)
    if org_row is not None:
        await db.delete(org_row)
        await db.flush()
    tenant_row = await db.get(TenantAccount, tenant_id)
    if tenant_row is not None:
        await db.delete(tenant_row)
    admin_row = await db.get(User, admin_id)
    if admin_row is not None:
        await db.delete(admin_row)
    await db.commit()


async def test_savepoint_rollback_cancels_the_emit(db, monkeypatch):
    """#82 (round 296): the outbox runner wraps EVERY handler in a
    begin_nested savepoint — a handler that emits (guardrail breach, the
    flagship case) then raises has its writes rolled back, but the
    after_commit listener fired at the per-message batch commit anyway:
    a phantom breach webhook. The cancel must scope to the emit's own
    savepoint."""
    import asyncio

    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.webhook import WebhookService

    org_id, tenant_id, admin_id = await _wh_fixture(db)
    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(event_type)

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    await db.commit()  # fixture committed; ids are plain strings
    try:
        # the outbox-runner shape: handler inside a savepoint, raising
        try:
            async with db.begin_nested():
                await emit_experiment_event(
                    db, scope_org_id=org_id,
                    event_type="experiment.decision_recorded",
                    payload={"experiment_id": "sp-phantom"},
                )
                raise RuntimeError("handler exploded after emit")
        except RuntimeError:
            pass
        await db.commit()  # the runner's per-message batch commit
        await asyncio.sleep(0.05)
        assert scheduled == [], (
            "a savepoint-rolled-back emit must not ride the outer commit"
        )
    finally:
        await _wh_sweep(db, org_id, tenant_id, admin_id)


async def test_savepoint_release_still_delivers(db, monkeypatch):
    """#82 counterpart: a handler that SUCCEEDS inside its savepoint must
    still deliver at the outer commit — the cancel must not overreach."""
    import asyncio

    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.webhook import WebhookService

    org_id, tenant_id, admin_id = await _wh_fixture(db)
    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(event_type)

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    await db.commit()
    try:
        async with db.begin_nested():
            await emit_experiment_event(
                db, scope_org_id=org_id,
                event_type="experiment.decision_recorded",
                payload={"experiment_id": "sp-ok"},
            )
        await db.commit()
        await asyncio.sleep(0.05)
        assert scheduled == ["experiment.decision_recorded"], scheduled
    finally:
        await _wh_sweep(db, org_id, tenant_id, admin_id)


async def test_unrelated_savepoint_rollback_must_not_cancel(db, monkeypatch):
    """#82 (round 296, the REAL direction): SQLAlchemy fires after_rollback
    on ANY savepoint rollback — in the outbox batch, message 1's successful
    emit was cancelled when message 2's unrelated savepoint rolled back:
    a legitimate breach webhook silently lost."""
    import asyncio

    from app.experiments.services.webhook_events import emit_experiment_event
    from app.services.webhook import WebhookService

    org_id, tenant_id, admin_id = await _wh_fixture(db)
    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(event_type)

    monkeypatch.setattr(
        WebhookService, "_deliver_background", staticmethod(counting_deliver)
    )
    await db.commit()
    try:
        # message 1: handler succeeds, savepoint releases
        async with db.begin_nested():
            await emit_experiment_event(
                db, scope_org_id=org_id,
                event_type="experiment.decision_recorded",
                payload={"experiment_id": "msg-1"},
            )
        # message 2: a LATER unrelated handler fails, its savepoint rolls back
        try:
            async with db.begin_nested():
                raise RuntimeError("sibling handler exploded")
        except RuntimeError:
            pass
        await db.commit()  # the batch commit — message 1 is COMMITTED
        await asyncio.sleep(0.05)
        assert scheduled == ["experiment.decision_recorded"], (
            "an unrelated savepoint rollback cancelled a committed emit"
        )
    finally:
        await _wh_sweep(db, org_id, tenant_id, admin_id)


async def test_webhook_org_cap_holds_under_concurrency(db, monkeypatch):
    """Defect #102 (#100/#101 family, platform-level): the 25-per-org
    webhook cap was a bare COUNT — two concurrent creators both read
    cap-1 and both inserted. WebhookService.create now locks the Org row
    (FOR UPDATE) before counting, so same-org creators serialize."""
    import asyncio as _aio
    import contextlib as _ctx

    import app.services.webhook as wh
    from app.controlplane.models.tenant import TenantAccount
    from app.exceptions import AppError as _AppError
    from app.models.organization import Organization
    from app.services.webhook import WebhookService

    tenant = TenantAccount(name=f"whc-{str(ULID()).lower()}",
                           slug=f"whc-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="whcap", slug=f"whc-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    db.add(org)
    await db.commit()  # writer sessions must SEE the org
    monkeypatch.setattr(wh, "MAX_WEBHOOKS_PER_ORG", 1, raising=False)

    gate = _aio.Event()
    arrived: list[int] = []

    async def gated_writer(tag: str) -> bool:
        async with AsyncSessionLocal() as s:
            try:
                await WebhookService(s).create(
                    org_id=org.id,
                    url=f"https://hooks.example.com/{tag}",
                    events=["pack.published"],
                )
                arrived.append(1)
                if len(arrived) >= 2:
                    gate.set()
                with _ctx.suppress(TimeoutError):
                    await _aio.wait_for(gate.wait(), timeout=1.0)
                await s.commit()
                return True
            except _AppError as e:
                # wave 52: pin code AND status on the cap refusal
                assert e.code == "WEBHOOK_LIMIT_REACHED"
                assert e.status_code == 422
                await s.rollback()
                return False

    results = await _aio.gather(gated_writer("a"), gated_writer("b"))
    from sqlalchemy import delete as _delete
    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    from app.models.webhook import WebhookSubscription as _Sub

    n = (
        await db.execute(
            _select(_func.count()).select_from(_Sub).where(_Sub.org_id == org.id)
        )
    ).scalar_one()
    # cleanup first (this test commits), then assert
    await db.execute(_delete(_Sub).where(_Sub.org_id == org.id))
    await db.commit()
    assert sum(results) == 1, f"exactly one webhook may land at cap=1, got {results}"
    assert n == 1, f"cap must be exact under concurrency, found {n} subscriptions"


async def test_webhook_invalid_event_pins_code_and_status(db):
    """Wave 52 killer (L179 422->423): an unknown event type is a 422
    INVALID_EVENT — pin both fields."""
    import pytest as _pytest

    from app.exceptions import AppError as _AppError
    from app.services.webhook import WebhookService

    with _pytest.raises(_AppError) as e:
        await WebhookService(db).create(
            org_id="O" * 26,
            url="https://hooks.example.com/x",
            events=["no.such.event"],
        )
    assert e.value.code == "INVALID_EVENT"
    assert e.value.status_code == 422


async def test_webhook_secret_rotation(db):
    """Defect #103 (industry staple): a leaked signing secret could only be
    retired by delete+recreate — receiver downtime and a new id anyway.
    rotate_secret mints a fresh secret in place (same id/url/events), is
    org-scoped (foreign org sees uniform 404), and the old secret stops
    signing."""
    import pytest as _pytest

    from app.controlplane.models.tenant import TenantAccount
    from app.exceptions import AppError as _AppError
    from app.models.organization import Organization
    from app.services.webhook import WebhookService

    tenant = TenantAccount(name=f"rot-{str(ULID()).lower()}",
                           slug=f"rot-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="rot", slug=f"rot-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    svc = WebhookService(db)
    sub = await svc.create(org.id, "https://hooks.example.com/rot",
                           ["pack.published"])
    old_secret = sub.secret
    rotated = await svc.rotate_secret(sub.id, org.id)
    assert rotated.id == sub.id
    assert rotated.secret != old_secret
    assert len(rotated.secret) == 64  # token_hex(32)
    assert rotated.url == "https://hooks.example.com/rot"
    # org containment: a foreign org gets the uniform 404
    with _pytest.raises(_AppError) as e:
        await svc.rotate_secret(sub.id, "X" * 26)
    assert e.value.code == "WEBHOOK_NOT_FOUND"
    assert e.value.status_code == 404  # wave 53: pin the status


async def test_webhook_mask_secret_boundary(db):
    """Wave 53 killer (len>8 boundary): exactly 8 chars masks fully;
    9 chars shows first/last 4 — the boundary is exclusive."""
    from datetime import UTC as _UTC
    from datetime import datetime as _dt

    from app.api.v1.endpoints.webhooks import WebhookResponse

    base = dict(id="W" * 26, org_id="O" * 26, url="https://x.example.com",
                events=["pack.published"], active=True,
                created_at=_dt.now(_UTC))
    assert WebhookResponse(secret="12345678", **base).secret == "****"
    assert WebhookResponse(secret="123456789", **base).secret == "1234****6789"


def test_webhook_empty_events_rejected():
    """Defect #104: events=[] passed validation and created a subscription
    that trigger_event's falsy guard treats as receive-EVERYTHING — an
    accidental wildcard. Empty means none, not all: 422 at the boundary."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.api.v1.endpoints.webhooks import CreateWebhookRequest

    with _pytest.raises(ValidationError):
        CreateWebhookRequest(url="https://hooks.example.com/x", events=[])


def test_webhook_events_cap_boundary():
    """Wave 54 killer (len>MAX boundary): exactly MAX_EVENTS_PER_WEBHOOK
    events is legal (the cap is inclusive); MAX+1 rejects."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.api.v1.endpoints.webhooks import CreateWebhookRequest
    from app.services.webhook import MAX_EVENTS_PER_WEBHOOK, VALID_EVENT_TYPES

    kinds = sorted(VALID_EVENT_TYPES)
    ok = CreateWebhookRequest(url="https://hooks.example.com/cap",
                              events=kinds[:MAX_EVENTS_PER_WEBHOOK])
    assert len(ok.events) == MAX_EVENTS_PER_WEBHOOK
    with _pytest.raises(ValidationError):
        CreateWebhookRequest(url="https://hooks.example.com/cap",
                             events=kinds[:MAX_EVENTS_PER_WEBHOOK + 1])


async def test_webhook_ops_write_audit_trail(db):
    """Defect #105: webhook create/delete/secret-rotate — credential
    lifecycle operations — left NO trace in the append-only commercial
    audit trail. With actor_user_id supplied, each op records its action;
    the audit payload NEVER carries the secret."""
    from sqlalchemy import select as _select

    from app.controlplane.models.audit import CommercialAuditEvent
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization
    from app.models.user import User, UserRole, UserStatus
    from app.services.webhook import WebhookService

    tenant = TenantAccount(name=f"aud-{str(ULID()).lower()}",
                           slug=f"aud-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="aud", slug=f"aud-{str(ULID()).lower()}",
                       tenant_id=tenant.id)
    actor = User(email=f"aud-{ULID()}@example.com", display_name="A",
                 role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add_all([org, actor])
    await db.flush()
    svc = WebhookService(db)
    sub = await svc.create(org.id, "https://hooks.example.com/aud",
                           ["pack.published"], actor_user_id=actor.id)
    await svc.rotate_secret(sub.id, org.id, actor_user_id=actor.id)
    sub_id = sub.id
    await svc.delete(sub.id, org.id, actor_user_id=actor.id)
    rows = (
        await db.execute(
            _select(CommercialAuditEvent).where(
                CommercialAuditEvent.target_type == "webhook",
                CommercialAuditEvent.target_id == sub_id,
            ).order_by(CommercialAuditEvent.created_at)
        )
    ).scalars().all()
    actions = [r.action for r in rows]
    assert actions == ["webhook.created", "webhook.secret_rotated", "webhook.deleted"]
    for r in rows:
        assert r.actor_user_id == actor.id
        assert r.tenant_id == tenant.id
        blob = str(r.before) + str(r.after)
        assert "secret" not in blob.lower(), "audit must never carry the secret"
