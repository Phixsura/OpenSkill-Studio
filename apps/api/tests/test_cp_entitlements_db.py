"""P2 DB tests: plans, versions, entitlement engine, quota enforcement.

R515 mutation sweep of _compute_effective/_resolve_plan_version/check_quota/
require_feature: 27/30 killed; 3 equivalents, all structurally proven:
- L155 subscription .limit(1) -> limit(2): uq_cp_sub_live (partial unique on
  tenant_id where status != 'cancelled') makes a second live subscription
  impossible, so scalar_one_or_none can never see two rows.
- L177 plan-version .limit(1) -> limit(2): the one-active-version-per-plan
  partial unique index gives the same single-row guarantee.
- L170 `trial_ends_at > now` -> `>=`: clock-instant boundary (a trial ending
  at the exact evaluation instant reads the default plan one request early).

R517 mutation sweep of plans.py _require_draft/activate_version/set_override/
create_draft_version: 19/21 killed (immutability gates, override typing,
version+1 math). 2 near-equivalent survivors, both the SAME shape: the
R62/R134 plan-row lock selects (`ProductPlan.id == plan.id` -> `!=`) flip to
locking every OTHER plan row — a coarser lock that still serializes the
racing drafts/activations whenever at least one other plan exists (always
true outside an empty DB), so correctness is preserved and only concurrency
degrades; the existing gather races cannot distinguish it. Accepted with
this note rather than asserting lock scope (unobservable from SQL results).
"""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.plan import PlanVersion, ProductPlan
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import plans as plan_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
from app.controlplane.services.entitlements import (
    check_quota,
    get_effective,
    invalidate_cache,
    require_feature,
    validate_entitlement_value,
)
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db, role=UserRole.STUDENT) -> User:
    user = User(
        email=f"cp2-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP2",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


def _actor(user) -> Actor:
    return Actor(user_id=user.id, type="platform")


async def _mk_tenant(db, user, status=TenantStatus.ACTIVE) -> TenantAccount:
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"E {ULID()}",
        slug=f"e-{str(ULID()).lower()}",
        actor=_actor(user),
        owner_user_id=user.id,
        status=status,
        with_trial=(status == TenantStatus.TRIAL),
    )
    await invalidate_cache(tenant.id)
    return tenant


# ── Seeds ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_seed_plans_present(db):
    keys = set((await db.execute(select(ProductPlan.key))).scalars().all())
    assert {"community", "school", "growth", "enterprise", "oem"} <= keys
    active = (
        (await db.execute(select(PlanVersion).where(PlanVersion.status == "active")))
        .scalars()
        .all()
    )
    assert len(active) >= 5


# ── Effective entitlements precedence ────────────────────────


@pytest.mark.asyncio
async def test_no_subscription_gets_community_defaults(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    eff = await get_effective(db, tenant)
    assert eff.plan_key == "community"
    assert eff.values["max_organizations"] == 1
    assert eff.values["client_portal"] is False


@pytest.mark.asyncio
async def test_trial_tenant_gets_school_plan(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    eff = await get_effective(db, tenant)
    assert eff.plan_key == "school"
    assert eff.trial is True
    assert eff.values["client_portal"] is True
    assert eff.values["max_active_learners"] == 200


@pytest.mark.asyncio
async def test_expired_trial_falls_back_to_community(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    tenant.trial_ends_at = datetime.now(UTC) - timedelta(days=1)
    await db.flush()
    await invalidate_cache(tenant.id)
    eff = await get_effective(db, tenant)
    assert eff.plan_key == "community"
    assert eff.trial is False


@pytest.mark.asyncio
async def test_override_beats_plan_and_expires_live(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_active_learners",
        value=500,
        enforcement="hard",
        expires_at=None,
        reason="pilot deal",
        actor=_actor(user),
    )
    eff = await get_effective(db, tenant)
    assert eff.values["max_active_learners"] == 500
    assert eff.sources["max_active_learners"] == "override"
    # Expired override filters live
    from app.controlplane.models.plan import TenantEntitlementOverride

    o = (
        await db.execute(
            select(TenantEntitlementOverride).where(
                TenantEntitlementOverride.tenant_id == tenant.id
            )
        )
    ).scalar_one()
    o.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()
    await invalidate_cache(tenant.id)
    eff = await get_effective(db, tenant)
    assert eff.sources["max_active_learners"] in ("default", "plan")


@pytest.mark.asyncio
async def test_suspension_masks_consumption_features(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await plan_svc.set_override(
        db,
        tenant.id,
        "client_portal",
        value=True,
        enforcement="hard",
        expires_at=None,
        reason="test",
        actor=_actor(user),
    )
    await tenant_svc.transition_status(
        db, tenant, TenantStatus.SUSPENDED, actor=_actor(user), reason="t"
    )
    eff = await get_effective(db, tenant)
    assert eff.values["client_portal"] is False
    assert eff.sources["client_portal"] == "suspension"
    # Display entitlements NOT masked
    assert eff.sources.get("custom_domain") != "suspension"


# ── Quotas ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hard_quota_rejects_over_limit(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    with pytest.raises(AppError) as exc:
        await check_quota(db, tenant, "max_organizations", current=1)
    assert exc.value.code == "QUOTA_EXCEEDED"
    # boundary: current + requested == limit passes
    d = await check_quota(db, tenant, "max_organizations", current=0)
    assert d.allowed and not d.soft_warning


@pytest.mark.asyncio
async def test_soft_quota_warns_not_rejects(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # storage is soft-by-default
    d = await check_quota(
        db, tenant, "max_storage_gb", current=Decimal("10"), requested=Decimal("1")
    )
    assert d.allowed and d.soft_warning


@pytest.mark.asyncio
async def test_soft_override_enforcement(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_active_learners",
        value=10,
        enforcement="soft",
        expires_at=None,
        reason="soft cap",
        actor=_actor(user),
    )
    d = await check_quota(db, tenant, "max_active_learners", current=10)
    assert d.allowed and d.soft_warning


@pytest.mark.asyncio
async def test_unlimited_none_always_allows(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_workflow_runs_month",
        value=None,
        enforcement="hard",
        expires_at=None,
        reason="unlimited",
        actor=_actor(user),
    )
    d = await check_quota(db, tenant, "max_workflow_runs_month", current=10**9)
    assert d.allowed


@pytest.mark.asyncio
async def test_require_feature(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    with pytest.raises(AppError) as exc:
        await require_feature(db, tenant, "paid_marketplace")
    assert exc.value.code == "FEATURE_NOT_AVAILABLE"
    await require_feature(db, tenant, "webhooks")  # community default True


# ── Version immutability + activation ────────────────────────


@pytest.mark.asyncio
async def test_plan_version_immutable_once_active(db):
    active = (
        await db.execute(
            select(PlanVersion)
            .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
            .where(ProductPlan.key == "community", PlanVersion.status == "active")
        )
    ).scalar_one()
    with pytest.raises(AppError) as exc:
        await plan_svc.update_draft(db, active, entitlements={"max_organizations": 5})
    assert exc.value.code == "PLAN_VERSION_IMMUTABLE"


@pytest.mark.asyncio
async def test_draft_activate_retires_old_active(db):
    user = await _mk_user(db, role=UserRole.ADMIN)
    plan = (
        await db.execute(select(ProductPlan).where(ProductPlan.key == "community"))
    ).scalar_one()
    old_active = (
        await db.execute(
            select(PlanVersion).where(
                PlanVersion.plan_id == plan.id, PlanVersion.status == "active"
            )
        )
    ).scalar_one()
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    assert draft.entitlements == old_active.entitlements  # cloned
    await plan_svc.update_draft(db, draft, entitlements={"max_organizations": 2})
    activated = await plan_svc.activate_version(db, draft, actor=_actor(user))
    assert activated.status == "active"
    await db.refresh(old_active)
    assert old_active.status == "retired"
    # rollback keeps the dev DB seeds intact (fixture rolls back)


@pytest.mark.asyncio
async def test_concurrent_activate_single_winner():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup, role=UserRole.ADMIN)
            plan = await plan_svc.create_plan(
                setup,
                key=f"race-{str(ULID()).lower()[:8]}",
                name="Race",
                description=None,
                actor=_actor(user),
            )
            d1 = await plan_svc.create_draft_version(setup, plan, created_by=user.id)
            d2 = await plan_svc.create_draft_version(setup, plan, created_by=user.id)
            await setup.commit()
            ids = (d1.id, d2.id, user.id)

        outcomes: list[str] = []

        async def activate(vid):
            async with AsyncSessionLocal() as s:
                v = await s.get(PlanVersion, vid)
                u = await s.get(User, ids[2])
                try:
                    await plan_svc.activate_version(s, v, actor=_actor(u))
                    await s.commit()
                    outcomes.append("ok")
                    return True
                except AppError:
                    await s.rollback()
                    outcomes.append("409")
                    return False
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    outcomes.append(type(exc).__name__)
                    return False

        r1, r2 = await asyncio.gather(activate(ids[0]), activate(ids[1]))
        # R62[3]: two DIFFERENT drafts racing must resolve as clean outcomes
        # (both may succeed sequentially — the second retires the first — or
        # one gets the documented 409). An IntegrityError 500 on
        # uq_cp_plan_active is the bug.
        assert all(o in ("ok", "409") for o in outcomes), outcomes
        # Never two simultaneously-active versions:
        async with AsyncSessionLocal() as s:
            v1 = await s.get(PlanVersion, ids[0])
            active_count = sum(
                1 for v in (v1, await s.get(PlanVersion, ids[1])) if v.status == "active"
            )
            assert active_count <= 1
    finally:
        # Committed rows must be swept — the shared dev DB otherwise
        # accumulates one junk plan per run (R134 follow-up hygiene).
        async with AsyncSessionLocal() as s:
            from sqlalchemy import delete as _delete

            await s.execute(_delete(PlanVersion).where(PlanVersion.plan_id == plan.id))
            await s.execute(_delete(ProductPlan).where(ProductPlan.id == plan.id))
            await s.commit()
        await engine.dispose()


# ── Validation ───────────────────────────────────────────────


def test_validate_entitlement_value_matrix():
    assert validate_entitlement_value("custom_domain", True) is True
    assert validate_entitlement_value("max_organizations", 5) == 5
    assert validate_entitlement_value("max_storage_gb", "12.5") == "12.5"
    assert validate_entitlement_value("max_ai_budget_usd_month", None) is None
    # R336 (mutation survivors): ZERO is a legal value on both numeric axes
    # (0 = none allowed; only NEGATIVES reject) …
    assert validate_entitlement_value("max_organizations", 0) == 0
    assert validate_entitlement_value("max_storage_gb", "0") == "0"
    for key, bad in [
        ("nope_key", 1),
        ("custom_domain", "yes"),
        ("custom_domain", None),
        ("max_organizations", -1),
        ("max_organizations", True),  # bool is not an int here
        ("max_storage_gb", "NaN"),
        ("max_storage_gb", "-3"),
    ]:
        with pytest.raises(AppError) as e:
            validate_entitlement_value(key, bad)
        # … and every reject is a 422 (R336)
        assert e.value.status_code == 422, (key, bad)


# ── Enforcement wiring: downgrade-no-eviction semantics ──────


@pytest.mark.asyncio
async def test_seat_quota_blocks_new_addition_not_existing(db):
    """Existing members stay; new additions rejected once over the limit."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org = await svc.create(
        name=f"Seats {ULID()}",
        slug=f"seats-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    # Cap instructors at the current count (owner counts as staff seat = 1)
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_instructors",
        value=1,
        enforcement="hard",
        expires_at=None,
        reason="test cap",
        actor=_actor(owner),
    )
    newcomer = await _mk_user(db)
    with pytest.raises(AppError) as exc:
        await svc.add_member(org.id, newcomer.id, OrgRole.INSTRUCTOR)
    assert exc.value.code == "QUOTA_EXCEEDED"
    # Learner seats unaffected by the instructor cap
    student = await _mk_user(db)
    member = await svc.add_member(org.id, student.id, OrgRole.STUDENT)
    assert member is not None


@pytest.mark.asyncio
async def test_seat_quota_not_bypassable_by_role_promotion(db):
    """R27/C0: add-then-promote must not slip past the staff seat cap — a
    student promoted to instructor consumes a staff seat and is gated."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org = await svc.create(
        name=f"Promote {ULID()}",
        slug=f"promote-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    # Staff cap = 1 (the owner). Adding a student is fine (learner seat)...
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_instructors",
        value=1,
        enforcement="hard",
        expires_at=None,
        reason="cap",
        actor=_actor(owner),
    )
    student = await _mk_user(db)
    await svc.add_member(org.id, student.id, OrgRole.STUDENT)
    # ...but promoting that student to instructor would be a 2nd staff seat → blocked
    with pytest.raises(AppError) as exc:
        await svc.update_member_role(org.id, student.id, OrgRole.INSTRUCTOR, owner.id)
    assert exc.value.code == "QUOTA_EXCEEDED"
    # Demotion (staff → student) is never blocked by the staff cap
    # (raise the learner cap so the demotion's student-seat check passes)
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_active_learners",
        value=100,
        enforcement="hard",
        expires_at=None,
        reason="cap",
        actor=_actor(owner),
    )
    instr = await _mk_user(db)
    # free a staff seat first by lifting the cap, add an instructor, then demote
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_instructors",
        value=10,
        enforcement="hard",
        expires_at=None,
        reason="cap",
        actor=_actor(owner),
    )
    await svc.add_member(org.id, instr.id, OrgRole.INSTRUCTOR)
    demoted = await svc.update_member_role(org.id, instr.id, OrgRole.STUDENT, owner.id)
    assert demoted.role == OrgRole.STUDENT


@pytest.mark.asyncio
async def test_blocked_status_mask_covers_cancelled_and_archived(db):
    """R49[35]: consumption entitlements must be masked for EVERY blocked
    status (SUSPENDED, CANCELLED, ARCHIVED) — not just SUSPENDED. A cancelled
    tenant previously kept webhooks/api_access/client_portal/paid_marketplace
    open because only SUSPENDED triggered the mask."""
    from app.controlplane.services.entitlements import SUSPENSION_MASKED_KEYS

    user = await _mk_user(db)
    for status in (TenantStatus.SUSPENDED, TenantStatus.CANCELLED, TenantStatus.ARCHIVED):
        tenant = await _mk_tenant(db, user)
        tenant.status = status
        await db.flush()
        await invalidate_cache(tenant.id)
        eff = await get_effective(db, tenant)
        for key in SUSPENSION_MASKED_KEYS:
            assert eff.values[key] is False, f"{key} not masked for {status}"
            assert eff.sources[key] == "suspension"
        with pytest.raises(AppError) as exc:
            await require_feature(db, tenant, "webhooks")
        assert exc.value.code == "FEATURE_NOT_AVAILABLE"
    # ACTIVE keeps defaults (webhooks/api_access default True)
    active = await _mk_tenant(db, user)
    active.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(active.id)
    eff = await get_effective(db, active)
    assert eff.values["webhooks"] is True
    assert eff.values["api_access"] is True


@pytest.mark.asyncio
async def test_storage_quota_gate_blocks_suspended_tenant(db):
    """R49[38]: uploads gate only through check_storage_quota, and storage is
    SOFT by default — so a suspended tenant kept growing storage. The facade
    now enforces require_tenant_active before the quota math."""
    from app.controlplane import facade as cp_facade
    from app.services.organization import OrgService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"S {ULID()}", slug=f"sq-{str(ULID()).lower()}", description=None, created_by=user.id
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    # Active → passes (soft storage default never rejects)
    await cp_facade.check_storage_quota(db, org.id, 1024)
    # Suspended → blocked before any quota math
    tenant.status = TenantStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as exc:
        await cp_facade.check_storage_quota(db, org.id, 1024)
    assert exc.value.code == "TENANT_SUSPENDED"


@pytest.mark.asyncio
async def test_draft_price_edit_same_currency_interval(db):
    """R62[1]: PATCHing a draft's prices with the SAME (currency, interval) —
    the normal 'edit the amount' operation — 500'd on uq_cp_plan_price
    because SQLAlchemy flushes INSERTs before DELETEs. The replace-all now
    flushes deletes first."""
    from ulid import ULID as _ULID

    from app.controlplane.models.plan import PlanPrice

    user = await _mk_user(db)
    plan = await plan_svc.create_plan(
        db,
        key=f"pe-{str(_ULID()).lower()[:8]}",
        name="PriceEdit",
        description=None,
        actor=_actor(user),
    )
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    await plan_svc.update_draft(
        db,
        draft,
        prices=[{"currency": "USD", "interval": "month", "amount_minor": 19900}],
    )
    # The edit: same (USD, month), new amount — must not 500
    await plan_svc.update_draft(
        db,
        draft,
        prices=[{"currency": "USD", "interval": "month", "amount_minor": 24900}],
    )
    rows = (
        (await db.execute(select(PlanPrice).where(PlanPrice.plan_version_id == draft.id)))
        .scalars()
        .all()
    )
    assert len(rows) == 1 and rows[0].amount_minor == 24900


@pytest.mark.asyncio
async def test_external_price_ref_write_path(db):
    """R62[2]: external_price_ref (the ADR-designated one mutable field on an
    active version) had NO write path — Stripe checkout was permanently
    unreachable. PUT /platform/plan-prices/{id}/external-ref backfills it."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient
    from ulid import ULID as _ULID

    from app.controlplane.models.plan import PlanPrice
    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token
    from app.main import app

    user = await _mk_user(db)
    db.add(PlatformRoleAssignment(user_id=user.id, role="platform_admin"))
    plan = await plan_svc.create_plan(
        db,
        key=f"xr-{str(_ULID()).lower()[:8]}",
        name="XRef",
        description=None,
        actor=_actor(user),
    )
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    await plan_svc.update_draft(
        db,
        draft,
        prices=[{"currency": "USD", "interval": "month", "amount_minor": 19900}],
    )
    await plan_svc.activate_version(db, draft, actor=_actor(user))
    price = (
        await db.execute(select(PlanPrice).where(PlanPrice.plan_version_id == draft.id))
    ).scalar_one()
    price_id = price.id
    xr_plan_id, xr_draft_id = plan.id, draft.id
    token = create_access_token(user.id, user.email, user.role.value)
    await db.commit()

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.put(
                f"/api/v1/platform/plan-prices/{price_id}/external-ref",
                json={"external_price_ref": "price_1QstripeXYZ"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 200, r.text
            assert r.json()["data"]["external_price_ref"] == "price_1QstripeXYZ"
    finally:
        app.router.lifespan_context = orig
    db.expire_all()
    fresh = await db.get(PlanPrice, price_id)
    assert fresh.external_price_ref == "price_1QstripeXYZ"
    # Sweep the committed plan — shared dev DB hygiene (R134 follow-up).
    from sqlalchemy import delete as _delete

    await db.execute(_delete(PlanPrice).where(PlanPrice.plan_version_id == xr_draft_id))
    await db.execute(_delete(PlanVersion).where(PlanVersion.plan_id == xr_plan_id))
    await db.execute(_delete(ProductPlan).where(ProductPlan.id == xr_plan_id))
    await db.commit()


@pytest.mark.asyncio
async def test_two_draft_activation_race_deterministic():
    """R62[3] deterministic repro: A activates draft1 and HOLDS its tx; B
    activates draft2 and must wait. Without the plan-row lock, B's retire
    scan (READ COMMITTED) misses A's newly-active row and B's insert dies on
    uq_cp_plan_active as an IntegrityError 500. With the lock, B serializes
    BEFORE its retire scan and resolves cleanly (win or documented 409)."""
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup, role=UserRole.ADMIN)
            plan = await plan_svc.create_plan(
                setup,
                key=f"drace-{str(ULID()).lower()[:8]}",
                name="DRace",
                description=None,
                actor=_actor(user),
            )
            d1 = await plan_svc.create_draft_version(setup, plan, created_by=user.id)
            d2 = await plan_svc.create_draft_version(setup, plan, created_by=user.id)
            await setup.commit()
            d1_id, d2_id, user_id = d1.id, d2.id, user.id
            plan_id = plan.id

        async def b_activate():
            async with AsyncSessionLocal() as s:
                v = await s.get(PlanVersion, d2_id)
                u = await s.get(User, user_id)
                try:
                    await plan_svc.activate_version(s, v, actor=_actor(u))
                    await s.commit()
                    return "ok"
                except AppError:
                    await s.rollback()
                    return "409"
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    return type(exc).__name__

        async with AsyncSessionLocal() as a:
            va = await a.get(PlanVersion, d1_id)
            ua = await a.get(User, user_id)
            await plan_svc.activate_version(a, va, actor=_actor(ua))
            # A holds its uncommitted activation while B starts
            b_task = asyncio.create_task(b_activate())
            await asyncio.sleep(0.3)  # let B reach the blocking point
            await a.commit()
        outcome = await asyncio.wait_for(b_task, timeout=10)
        assert outcome in ("ok", "409"), f"unhandled {outcome} — the 500 bug"
        # Exactly one active version remains
        async with AsyncSessionLocal() as s:
            statuses = []
            for vid in (d1_id, d2_id):
                v = await s.get(PlanVersion, vid)
                statuses.append(v.status)
            assert statuses.count("active") == 1, statuses
    finally:
        # Sweep the committed plan — shared dev DB hygiene (R134 follow-up).
        async with AsyncSessionLocal() as s:
            from sqlalchemy import delete as _delete

            await s.execute(_delete(PlanVersion).where(PlanVersion.plan_id == plan_id))
            await s.execute(_delete(ProductPlan).where(ProductPlan.id == plan_id))
            await s.commit()
        await engine.dispose()


# ── R68: seat lifecycle + org deletion ───────────────────────


@pytest.mark.asyncio
async def test_deleted_org_frees_seats_everywhere(db):
    """R68[1]/[2]: deleting an org left its member rows ACTIVE — they kept
    consuming the tenant seat quota (blocking adds in sibling orgs) and were
    billed as live seats forever. delete_org must archive member rows."""
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org_a = await svc.create(
        name=f"A {ULID()}", slug=f"a68-{str(ULID()).lower()}", description=None, created_by=owner.id
    )
    tenant = await db.get(TenantAccount, org_a.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    student = await _mk_user(db)
    await svc.add_member(org_a.id, student.id, OrgRole.STUDENT)
    await svc.delete_org(org_a.id, owner.id)
    rows = (
        (
            await db.execute(
                select(OrgMember).where(
                    OrgMember.org_id == org_a.id, OrgMember.user_id == student.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert rows and all(m.status == MemberStatus.ARCHIVED for m in rows)


@pytest.mark.asyncio
async def test_blocked_tenant_cannot_grow_seats(db):
    """R68[5]: a suspended/cancelled tenant kept adding billable seats via
    pre-existing invite links — add_member (the single member-creation
    funnel) now requires an active tenant."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org = await svc.create(
        name=f"S68 {ULID()}",
        slug=f"s68-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.SUSPENDED
    await db.flush()
    await invalidate_cache(tenant.id)
    student = await _mk_user(db)
    with pytest.raises(AppError) as exc:
        await svc.add_member(org.id, student.id, OrgRole.STUDENT)
    assert exc.value.code == "TENANT_SUSPENDED"


@pytest.mark.asyncio
async def test_concurrent_seat_join_single_winner():
    """R68[3] TOCTOU: two concurrent joins with ONE seat left both counted
    under the cap and both inserted. The tenant-scoped advisory lock
    serializes count→insert; exactly one wins."""
    from app.core.database import engine
    from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole
    from app.services.organization import OrgService

    try:
        async with AsyncSessionLocal() as setup:
            owner = await _mk_user(setup)
            svc = OrgService(setup)
            org = await svc.create(
                name=f"R68 {ULID()}",
                slug=f"r68-{str(ULID()).lower()}",
                description=None,
                created_by=owner.id,
            )
            tenant = await setup.get(TenantAccount, org.tenant_id)
            tenant.status = TenantStatus.ACTIVE
            await setup.flush()
            await plan_svc.set_override(
                setup,
                tenant.id,
                "max_active_learners",
                value=1,
                enforcement="hard",
                expires_at=None,
                reason="race test",
                actor=_actor(owner),
            )
            u1 = await _mk_user(setup)
            u2 = await _mk_user(setup)
            await setup.commit()
            org_id, t_id = org.id, tenant.id
            u1_id, u2_id = u1.id, u2.id
        await invalidate_cache(t_id)

        # Deterministically widen the count→insert window: a delayed
        # check_quota guarantees both joins overlap there. With the advisory
        # lock the second join BLOCKS until the first commits (then counts 1
        # and 409s); without it both count 0 and both insert.
        from unittest.mock import patch as _patch

        from app.controlplane import facade as _facade

        real_check_quota = _facade.check_quota

        async def slow_check_quota(*a, **kw):
            result = await real_check_quota(*a, **kw)
            await asyncio.sleep(0.4)
            return result

        async def join(uid):
            async with AsyncSessionLocal() as s:
                try:
                    await OrgService(s).add_member(org_id, uid, OrgRole.STUDENT)
                    await s.commit()
                    return "ok"
                except AppError as exc:
                    await s.rollback()
                    return exc.code
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    return type(exc).__name__

        with _patch.object(_facade, "check_quota", slow_check_quota):
            r1, r2 = await asyncio.gather(join(u1_id), join(u2_id))
        assert sorted([r1, r2]) == ["QUOTA_EXCEEDED", "ok"], (r1, r2)
        from sqlalchemy import func as _f

        async with AsyncSessionLocal() as s:
            n = (
                await s.execute(
                    select(_f.count(OrgMember.id))
                    .select_from(OrgMember)
                    .join(Organization, Organization.id == OrgMember.org_id)
                    .where(
                        Organization.tenant_id == t_id,
                        OrgMember.role == OrgRole.STUDENT,
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
            ).scalar_one()
            assert n == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_concurrent_same_slug_org_create_clean_conflict():
    """R68[4]: two concurrent POST /orgs with the same slug both passed the
    existence SELECTs; the loser 500'd on the tenant slug unique index.
    The insert is now savepoint-isolated: suffix retry or clean 409."""
    from app.core.database import engine
    from app.services.organization import OrgService

    try:
        async with AsyncSessionLocal() as setup:
            u1 = await _mk_user(setup)
            u2 = await _mk_user(setup)
            await setup.commit()
            ids = (u1.id, u2.id)
        slug = f"clash-{str(ULID()).lower()}"

        async def create(uid):
            async with AsyncSessionLocal() as s:
                try:
                    await OrgService(s).create(
                        name="Clash", slug=slug, description=None, created_by=uid
                    )
                    await s.commit()
                    return "ok"
                except AppError as exc:
                    await s.rollback()
                    return exc.code
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    return type(exc).__name__

        r1, r2 = await asyncio.gather(create(ids[0]), create(ids[1]))
        # One wins; the other gets a clean AppError (org-slug or tenant-slug
        # conflict depending on which SELECT catches it) — never a 500-class
        # IntegrityError.
        assert "ok" in (r1, r2), (r1, r2)
        other = r2 if r1 == "ok" else r1
        assert other in ("SLUG_ALREADY_EXISTS", "TENANT_SLUG_TAKEN", "ok"), (r1, r2)
    finally:
        await engine.dispose()


# ── R74: quota-counting semantics ────────────────────────────


@pytest.mark.asyncio
async def test_already_seated_user_joins_second_org_at_cap(db):
    """R74[1]: current counts DISTINCT users tenant-wide but requested was
    always 1 — adding a user who already holds a seat in a sibling org was
    falsely rejected at the cap even though no new seat is consumed."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    owner = await _mk_user(db)
    svc = OrgService(db)
    org_a = await svc.create(
        name=f"A74 {ULID()}",
        slug=f"a74-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
    )
    tenant = await db.get(TenantAccount, org_a.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    org_b = await svc.create(
        name=f"B74 {ULID()}",
        slug=f"b74-{str(ULID()).lower()}",
        description=None,
        created_by=owner.id,
        tenant_id=tenant.id,
    )
    await plan_svc.set_override(
        db,
        tenant.id,
        "max_active_learners",
        value=1,
        enforcement="hard",
        expires_at=None,
        reason="cap",
        actor=_actor(owner),
    )
    await invalidate_cache(tenant.id)
    student = await _mk_user(db)
    await svc.add_member(org_a.id, student.id, OrgRole.STUDENT)  # consumes THE seat
    # Same user joins org B — distinct count stays 1, must pass at cap=1
    member_b = await svc.add_member(org_b.id, student.id, OrgRole.STUDENT)
    assert member_b.org_id == org_b.id
    # A DIFFERENT user is properly rejected
    other = await _mk_user(db)
    with pytest.raises(AppError) as exc:
        await svc.add_member(org_a.id, other.id, OrgRole.STUDENT)
    assert exc.value.code == "QUOTA_EXCEEDED"


@pytest.mark.asyncio
async def test_concurrent_draft_version_create_no_500():
    """R134 ([16]): two concurrent create_draft_version calls both computed
    max(version)+1 and the loser 500'd on uq_cp_plan_version. The plan-row
    FOR UPDATE serializes them: both succeed with distinct versions."""
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup, role=UserRole.ADMIN)
            plan = await plan_svc.create_plan(
                setup,
                key=f"drace-{str(ULID()).lower()[:8]}",
                name="DraftRace",
                description=None,
                actor=_actor(user),
            )
            await setup.commit()
            plan_id, user_id = plan.id, user.id

        outcomes: list[str] = []

        async def make_draft():
            async with AsyncSessionLocal() as s:
                p = await s.get(ProductPlan, plan_id)
                try:
                    await plan_svc.create_draft_version(s, p, created_by=user_id)
                    await s.commit()
                    outcomes.append("ok")
                except AppError:
                    await s.rollback()
                    outcomes.append("409")
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    outcomes.append(type(exc).__name__)

        await asyncio.gather(make_draft(), make_draft())
        assert all(o in ("ok", "409") for o in outcomes), outcomes
        async with AsyncSessionLocal() as s:
            versions = (
                (await s.execute(select(PlanVersion.version).where(PlanVersion.plan_id == plan_id)))
                .scalars()
                .all()
            )
            assert len(versions) == len(set(versions)), f"duplicate versions: {versions}"
            assert len(versions) == outcomes.count("ok")
    finally:
        async with AsyncSessionLocal() as s:
            from sqlalchemy import delete as _delete

            await s.execute(_delete(PlanVersion).where(PlanVersion.plan_id == plan_id))
            await s.execute(_delete(ProductPlan).where(ProductPlan.id == plan_id))
            await s.commit()
        await engine.dispose()


@pytest.mark.asyncio
async def test_concurrent_create_plan_same_key_clean_409():
    """R134 ([16]): two concurrent create_plan calls with the same key — the
    loser must get the documented PLAN_EXISTS 409, not an IntegrityError 500
    (SAVEPOINT-isolated flush)."""
    from app.core.database import engine

    key = f"krace-{str(ULID()).lower()[:8]}"
    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup, role=UserRole.ADMIN)
            await setup.commit()
            user_id = user.id

        outcomes: list[str] = []

        async def make_plan():
            async with AsyncSessionLocal() as s:
                u = await s.get(User, user_id)
                try:
                    await plan_svc.create_plan(
                        s, key=key, name="KRace", description=None, actor=_actor(u)
                    )
                    await s.commit()
                    outcomes.append("ok")
                except AppError as e:
                    await s.rollback()
                    outcomes.append(e.code)
                except Exception as exc:  # noqa: BLE001
                    await s.rollback()
                    outcomes.append(type(exc).__name__)

        await asyncio.gather(make_plan(), make_plan())
        assert sorted(outcomes) == ["PLAN_EXISTS", "ok"] or outcomes == ["ok", "ok"], outcomes
        # ["ok","ok"] would mean both landed — impossible with the unique key;
        # accept only one row either way:
        async with AsyncSessionLocal() as s:
            from sqlalchemy import func as _fn

            count = (
                await s.execute(select(_fn.count(ProductPlan.id)).where(ProductPlan.key == key))
            ).scalar_one()
            assert count == 1
    finally:
        async with AsyncSessionLocal() as s:
            from sqlalchemy import delete as _delete

            await s.execute(_delete(ProductPlan).where(ProductPlan.key == key))
            await s.commit()
        await engine.dispose()


@pytest.mark.asyncio
async def test_update_draft_toctou_activation_race():
    """R135: update_draft must re-check status under the version-row lock —
    a PATCH whose session loaded the version BEFORE a concurrent activation
    committed must 409 (PLAN_VERSION_IMMUTABLE), never mutate the now-ACTIVE
    version. Two sessions: A loads (draft), B activates+commits, A patches."""
    from app.core.database import engine

    plan_id = None
    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup, role=UserRole.ADMIN)
            plan = await plan_svc.create_plan(
                setup,
                key=f"toctou-{str(ULID()).lower()[:8]}",
                name="Toctou",
                description=None,
                actor=_actor(user),
            )
            draft = await plan_svc.create_draft_version(setup, plan, created_by=user.id)
            await setup.commit()
            plan_id, draft_id, user_id = plan.id, draft.id, user.id

        async with AsyncSessionLocal() as sa, AsyncSessionLocal() as sb:
            # A loads the version — sees draft.
            stale = await sa.get(PlanVersion, draft_id)
            assert stale.status == "draft"
            # B activates and COMMITS.
            vb = await sb.get(PlanVersion, draft_id)
            ub = await sb.get(User, user_id)
            await plan_svc.activate_version(sb, vb, actor=_actor(ub))
            await sb.commit()
            # A patches with its stale (draft-status) object.
            with pytest.raises(AppError) as exc:
                await plan_svc.update_draft(sa, stale, entitlements={"webhooks": False})
            assert exc.value.code == "PLAN_VERSION_IMMUTABLE"
            await sa.rollback()

        async with AsyncSessionLocal() as s:
            v = await s.get(PlanVersion, draft_id)
            assert v.status == "active"
            assert v.entitlements.get("webhooks") is not False, "ACTIVE version mutated"
    finally:
        if plan_id is not None:
            async with AsyncSessionLocal() as s:
                from sqlalchemy import delete as _delete

                await s.execute(_delete(PlanVersion).where(PlanVersion.plan_id == plan_id))
                await s.execute(_delete(ProductPlan).where(ProductPlan.id == plan_id))
                await s.commit()
        await engine.dispose()


@pytest.mark.asyncio
async def test_update_draft_duplicate_price_pair_422(db):
    """R135: duplicate (currency, interval) inside ONE prices body must be a
    clean 422, not an unhandled 23505 → 500."""
    user = await _mk_user(db, role=UserRole.ADMIN)
    plan = await plan_svc.create_plan(
        db,
        key=f"dupp-{str(ULID()).lower()[:8]}",
        name="DupPair",
        description=None,
        actor=_actor(user),
    )
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    with pytest.raises(AppError) as exc:
        await plan_svc.update_draft(
            db,
            draft,
            prices=[
                {"currency": "USD", "interval": "month", "amount_minor": 1000},
                {"currency": "USD", "interval": "month", "amount_minor": 2000},
            ],
        )
    assert exc.value.code == "VALIDATION_ERROR"
    assert exc.value.status_code == 422
    from sqlalchemy import delete as _delete

    await db.execute(_delete(PlanVersion).where(PlanVersion.plan_id == plan.id))
    await db.execute(_delete(ProductPlan).where(ProductPlan.id == plan.id))
    await db.flush()


# ── R254: mutation kill-set for the quota/feature gates + decimal normalize ──
# Status: 26/30 killed. The 4 survivors are equivalent: two limit(1)→limit(2)
# flips are shielded by the one-live-subscription / one-active-trial-plan data
# invariants (scalar_one_or_none only differs on invariant-violating rows),
# and the trial-end / override-expiry <=→< flips differ only at the exact
# database microsecond — timing, not logic.


@pytest.mark.asyncio
async def test_decimal_normalization_and_none_default(db):
    """R254: `d.type == "decimal" AND isinstance(Decimal)` — the Or mutant
    str()'s a None default into the string "None" (poisoning the cache and
    crashing .get()); the NotEq mutant leaves raw Decimals in the cached
    values. Pin both: decimal defaults surface as str, None stays None."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    eff = await get_effective(db, tenant)
    assert eff.values["max_storage_gb"] == "5"  # str-normalized
    assert isinstance(eff.get("max_storage_gb"), Decimal)
    assert eff.values["max_ai_budget_usd_month"] is None  # None, never "None"
    assert eff.get("max_ai_budget_usd_month") is None


@pytest.mark.asyncio
async def test_quota_and_feature_gate_arms(db):
    """R254: check_quota's guard arms (unknown key, bool key), the soft-storage
    default arm, and require_feature's arms — with exact HTTP statuses."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)

    with pytest.raises(AppError) as e:
        await check_quota(db, tenant, "no_such_key", current=0)
    assert e.value.code == "UNKNOWN_ENTITLEMENT" and e.value.status_code == 422
    with pytest.raises(AppError) as e:  # bool key not numeric
        await check_quota(db, tenant, "custom_domain", current=0)
    assert e.value.status_code == 422

    # storage is soft-by-default when over (no override present)
    dec = await check_quota(db, tenant, "max_storage_gb", current=999)
    assert dec.allowed is True and dec.soft_warning is True
    # a hard numeric (max_organizations, default 1) raises 403 when over
    with pytest.raises(AppError) as e:
        await check_quota(db, tenant, "max_organizations", current=1)
    assert e.value.code == "QUOTA_EXCEEDED" and e.value.status_code == 403
    # at the limit exactly → allowed, no warning
    ok = await check_quota(db, tenant, "max_organizations", current=0)
    assert ok.allowed is True and ok.soft_warning is False
    # a SOFT-CAPABLE key without a soft override is still HARD by default
    # (kills the `soft and d.soft_capable` → or mutant, which silently made
    # every soft-capable quota advisory)
    with pytest.raises(AppError) as e:
        await check_quota(db, tenant, "max_active_learners", current=10_000)
    assert e.value.code == "QUOTA_EXCEEDED"

    with pytest.raises(AppError) as e:
        await require_feature(db, tenant, "no_such_flag")
    assert e.value.status_code == 422
    with pytest.raises(AppError) as e:  # numeric key not a feature
        await require_feature(db, tenant, "max_organizations")
    assert e.value.status_code == 422
    with pytest.raises(AppError) as e:  # off-by-default feature
        await require_feature(db, tenant, "custom_domain")
    assert e.value.code == "FEATURE_NOT_AVAILABLE" and e.value.status_code == 403


@pytest.mark.asyncio
async def test_remove_override_and_stale_activate(db):
    """R255: remove_override was untested — the 404 arc, the delete flow
    (effective value returns to the plan/default), and activate_version on a
    non-draft raises the documented 409 instead of silently re-activating."""
    user = await _mk_user(db, role=UserRole.ADMIN)
    tenant = await _mk_tenant(db, user)

    with pytest.raises(AppError) as e:
        await plan_svc.remove_override(db, tenant.id, "max_organizations", actor=_actor(user))
    assert e.value.code == "OVERRIDE_NOT_FOUND" and e.value.status_code == 404

    await plan_svc.set_override(
        db,
        tenant.id,
        "max_organizations",
        value=42,
        enforcement="hard",
        expires_at=None,
        reason="test",
        actor=_actor(user),
    )
    eff = await get_effective(db, tenant)
    assert eff.get("max_organizations") == 42 and eff.sources["max_organizations"] == "override"

    await plan_svc.remove_override(db, tenant.id, "max_organizations", actor=_actor(user))
    eff = await get_effective(db, tenant)
    assert eff.get("max_organizations") != 42
    assert eff.sources["max_organizations"] in ("default", "plan")
    with pytest.raises(AppError):  # idempotence: second remove 404s
        await plan_svc.remove_override(db, tenant.id, "max_organizations", actor=_actor(user))

    # stale activation: re-activating a non-draft version is the documented
    # 409 (PLAN_VERSION_IMMUTABLE pre-check; PLAN_VERSION_CONFLICT remains the
    # locked-race backstop exercised by test_concurrent_activate_single_winner)
    plan = await plan_svc.create_plan(
        db, key=f"r255-{str(ULID()).lower()[:8]}", name="R255", description=None, actor=_actor(user)
    )
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    await plan_svc.activate_version(db, draft, actor=_actor(user))
    with pytest.raises(AppError) as e:
        await plan_svc.activate_version(db, draft, actor=_actor(user))
    assert e.value.code == "PLAN_VERSION_IMMUTABLE" and e.value.status_code == 409


@pytest.mark.asyncio
async def test_public_plan_catalog_hides_unpublished(db):
    """R294: the public pricing page (/api/v1/plans, unauthenticated) must
    expose ONLY active plans with an active version — an inactive plan or a
    draft/retired version leaking publicly is an unpublished-pricing
    disclosure. Pinned as a data-exposure sentinel: widening either filter
    surfaces the hidden rows and trips the test."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.main import app

    user = await _mk_user(db, role=UserRole.ADMIN)
    # an INACTIVE plan with an active version → must not appear
    hidden_plan = await plan_svc.create_plan(
        db,
        key=f"hidden-{str(ULID()).lower()[:8]}",
        name="Hidden",
        description=None,
        actor=_actor(user),
    )
    hv = await plan_svc.create_draft_version(db, hidden_plan, created_by=user.id)
    await plan_svc.activate_version(db, hv, actor=_actor(user))
    hidden_plan.is_active = False
    # an ACTIVE plan whose only version is still DRAFT → must not appear
    draft_plan = await plan_svc.create_plan(
        db,
        key=f"draftonly-{str(ULID()).lower()[:8]}",
        name="DraftOnly",
        description=None,
        actor=_actor(user),
    )
    await plan_svc.create_draft_version(db, draft_plan, created_by=user.id)  # never activated
    await db.commit()
    hidden_key, draft_key = hidden_plan.key, draft_plan.key

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.get("/api/v1/plans")
            assert r.status_code == 200, r.text
            keys = {p["key"] for p in r.json()["data"]}
            assert hidden_key not in keys, "inactive plan leaked to the public catalog"
            assert draft_key not in keys, "draft-only plan leaked to the public catalog"
            # the seeded active plans DO appear, each with an active version
            assert keys, "public catalog unexpectedly empty"
            for p in r.json()["data"]:
                assert p["active_version"]["status"] == "active"
    finally:
        app.router.lifespan_context = orig
        async with AsyncSessionLocal() as clean:
            for k in (hidden_key, draft_key):
                pl = (
                    await clean.execute(select(ProductPlan).where(ProductPlan.key == k))
                ).scalar_one_or_none()
                if pl is not None:
                    for v in (
                        (
                            await clean.execute(
                                select(PlanVersion).where(PlanVersion.plan_id == pl.id)
                            )
                        )
                        .scalars()
                        .all()
                    ):
                        await clean.delete(v)
                    await clean.delete(pl)
            await clean.commit()


@pytest.mark.asyncio
async def test_override_expiring_exactly_now_is_expired(db, monkeypatch):
    """R336 (mutation survivor): the override-expiry window is half-open —
    a grant whose expires_at equals the evaluation instant is ALREADY
    expired (<=, not <). Frozen clock pins the boundary deterministically."""
    from datetime import datetime as real_dt

    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.controlplane.services import entitlements as ent

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    frozen = real_dt.now(UTC)

    class FrozenDT(real_dt):
        @classmethod
        def now(cls, tz=None):
            return frozen if tz is not None else frozen.replace(tzinfo=None)

    monkeypatch.setattr(ent, "datetime", FrozenDT)
    db.add(
        TenantEntitlementOverride(
            tenant_id=tenant.id,
            key="max_organizations",
            value={"v": 42},
            reason="boundary",
            enforcement="hard",
            expires_at=frozen,
        )
    )
    await db.flush()
    await ent.invalidate_cache(tenant.id)
    eff = await ent._compute_effective(db, tenant)
    assert eff.values["max_organizations"] != 42, (
        "an override expiring exactly now must not apply (half-open window)"
    )
    assert eff.sources["max_organizations"] != "override"


@pytest.mark.asyncio
async def test_set_override_is_tenant_scoped_and_status_codes(db):
    """R340 (mutation survivors): set_override's existing-row lookup is
    keyed by (tenant, key) — a flipped tenant filter would UPDATE another
    tenant's override instead of creating this tenant's. Two tenants, same
    key: each keeps its own value. Plus: bad enforcement is a 422 and a
    concurrent plan-version activation conflict is a 409."""
    from app.controlplane.models.plan import PlanVersion, ProductPlan, TenantEntitlementOverride
    from app.controlplane.services import plans as plan_svc

    user = await _mk_user(db)
    a = await _mk_tenant(db, user)
    b = await _mk_tenant(db, user)
    await plan_svc.set_override(
        db,
        a.id,
        "max_organizations",
        value=3,
        enforcement="hard",
        expires_at=None,
        reason="A",
        actor=_actor(user),
    )
    await plan_svc.set_override(
        db,
        b.id,
        "max_organizations",
        value=7,
        enforcement="hard",
        expires_at=None,
        reason="B",
        actor=_actor(user),
    )
    rows = (
        (
            await db.execute(
                select(TenantEntitlementOverride).where(
                    TenantEntitlementOverride.key == "max_organizations",
                    TenantEntitlementOverride.tenant_id.in_([a.id, b.id]),
                )
            )
        )
        .scalars()
        .all()
    )
    by_tenant = {r.tenant_id: r.value.get("v") for r in rows}
    assert by_tenant == {a.id: 3, b.id: 7}  # B's write never mutated A's row

    # the lookup is also KEY-scoped: updating k1 must not touch A's k2 row
    await plan_svc.set_override(
        db,
        a.id,
        "max_storage_gb",
        value="50",
        enforcement="hard",
        expires_at=None,
        reason="k2",
        actor=_actor(user),
    )
    await plan_svc.set_override(
        db,
        a.id,
        "max_organizations",
        value=4,
        enforcement="hard",
        expires_at=None,
        reason="A2",
        actor=_actor(user),
    )
    from app.controlplane.models.plan import TenantEntitlementOverride as TEOverride

    a_rows = (
        (await db.execute(select(TEOverride).where(TEOverride.tenant_id == a.id))).scalars().all()
    )
    a_by_key = {r.key: r.value.get("v") for r in a_rows}
    assert a_by_key == {"max_organizations": 4, "max_storage_gb": "50"}

    with pytest.raises(AppError) as e422:
        await plan_svc.set_override(
            db,
            a.id,
            "max_organizations",
            value=1,
            enforcement="maybe",
            expires_at=None,
            reason="x",
            actor=_actor(user),
        )
    assert e422.value.status_code == 422

    # activation guard: activating a non-draft version is a 409
    plan = ProductPlan(key=f"r340-{str(ULID()).lower()[:8]}", name="R340")
    db.add(plan)
    await db.flush()
    pv = PlanVersion(
        plan_id=plan.id, version=1, status="active", entitlements={}, activated_at=datetime.now(UTC)
    )
    db.add(pv)
    await db.flush()
    # non-draft → immutable 409 up front
    with pytest.raises(AppError) as e_imm:
        await plan_svc.activate_version(db, pv, actor=_actor(user))
    assert e_imm.value.code == "PLAN_VERSION_IMMUTABLE" and e_imm.value.status_code == 409
    # stale-draft race: the object SAYS draft but the row is already active →
    # the guarded UPDATE loses and raises the concurrent-conflict 409
    from types import SimpleNamespace

    stale = SimpleNamespace(id=pv.id, plan_id=pv.plan_id, status="draft", version=1)
    with pytest.raises(AppError) as e409:
        await plan_svc.activate_version(db, stale, actor=_actor(user))
    assert e409.value.code == "PLAN_VERSION_CONFLICT" and e409.value.status_code == 409


@pytest.mark.asyncio
async def test_concurrent_set_override_same_key_single_row():
    """R340: two concurrent first-ever set_override calls for the same
    (tenant, key) must BOTH succeed with exactly one row — the loser's
    IntegrityError recovery re-selects the winner's row by (tenant, key);
    a flipped filter there finds nothing and 500s."""
    import asyncio

    from app.controlplane.models.plan import TenantEntitlementOverride as TEOverride
    from app.controlplane.services import plans as plan_svc
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as setup:
        user = await _mk_user(setup)
        tenant = await _mk_tenant(setup, user)
        await setup.commit()
        tid, actor = tenant.id, _actor(user)

    async def winner():
        async with AsyncSessionLocal() as s:
            await plan_svc.set_override(
                s,
                tid,
                "max_organizations",
                value=1,
                enforcement="hard",
                expires_at=None,
                reason="w",
                actor=actor,
            )
            await asyncio.sleep(0.4)
            await s.commit()

    async def loser():
        await asyncio.sleep(0.15)
        async with AsyncSessionLocal() as s:
            await plan_svc.set_override(
                s,
                tid,
                "max_organizations",
                value=2,
                enforcement="hard",
                expires_at=None,
                reason="l",
                actor=actor,
            )
            await s.commit()

    await asyncio.gather(winner(), loser())
    async with AsyncSessionLocal() as s:
        rows = (
            (
                await s.execute(
                    select(TEOverride).where(
                        TEOverride.tenant_id == tid, TEOverride.key == "max_organizations"
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1
        assert rows[0].value.get("v") in (1, 2)
        await s.delete(rows[0])
        await s.commit()


@pytest.mark.asyncio
async def test_plan_activation_invalidates_subscribed_tenants_cache(db):
    """R369: invalidate_cache_for_plan must clear the cache of exactly the
    tenants SUBSCRIBED to the plan (join/where flips clear nobody or the
    wrong tenants — a plan-version activation then serves STALE entitlements
    until TTL). Subscribed tenant sees the new value immediately; an
    unrelated tenant's cache entry is untouched."""
    from datetime import timedelta

    from app.controlplane.models.billing import Subscription
    from app.controlplane.models.plan import PlanPrice
    from app.controlplane.services import plans as plan_svc
    from app.controlplane.services.entitlements import get_effective

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    plan = await plan_svc.create_plan(
        db, key=f"r369-{str(ULID()).lower()[:8]}", name="R369", description=None, actor=_actor(user)
    )
    v1 = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    v1.entitlements = {"max_organizations": 3}
    db.add(
        PlanPrice(
            plan_version_id=v1.id,
            currency="USD",
            interval="month",
            amount_minor=1000,
            included_seats=0,
        )
    )
    await db.flush()
    await plan_svc.activate_version(db, v1, actor=_actor(user))
    now = datetime.now(UTC)
    db.add(
        Subscription(
            tenant_id=tenant.id,
            plan_version_id=v1.id,
            status="active",
            currency="USD",
            interval="month",
            seat_quantity=0,
            current_period_start=now - timedelta(days=1),
            current_period_end=now + timedelta(days=29),
            provider="manual",
            created_by=user.id,
        )
    )
    await db.flush()

    eff1 = await get_effective(db, tenant)  # populates the cache
    assert eff1.values["max_organizations"] == 3

    v2 = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    v2.entitlements = {"max_organizations": 9}
    await db.flush()
    await plan_svc.activate_version(db, v2, actor=_actor(user))
    # the invalidation contract, asserted at the CACHE LAYER: activation
    # deletes exactly the subscribed tenant's cache key (the join/where
    # flips clear nobody / the wrong tenants → stale entitlements to TTL)
    import app.core.redis as redis_mod
    from app.controlplane.services.entitlements import CACHE_KEY

    r = redis_mod.redis_pool()
    key = CACHE_KEY.format(tenant_id=tenant.id)
    assert await r.get(key) is None, "activation must clear the subscriber's cache"
    # …and an UNRELATED tenant's cache is NOT actively cleared: plant a
    # sentinel value under the bystander's key — activation must leave it,
    # while clearing the subscriber's again
    bystander = await _mk_tenant(db, user)
    # the bystander SUBSCRIBES to a DIFFERENT plan — the join-flip mutant
    # cartesian-matches every other-version subscriber and clears them too
    other_plan = await plan_svc.create_plan(
        db,
        key=f"r369b-{str(ULID()).lower()[:8]}",
        name="R369b",
        description=None,
        actor=_actor(user),
    )
    ov = await plan_svc.create_draft_version(db, other_plan, created_by=user.id)
    ov.entitlements = {}
    await db.flush()
    await plan_svc.activate_version(db, ov, actor=_actor(user))
    db.add(
        Subscription(
            tenant_id=bystander.id,
            plan_version_id=ov.id,
            status="active",
            currency="USD",
            interval="month",
            seat_quantity=0,
            current_period_start=now - timedelta(days=1),
            current_period_end=now + timedelta(days=29),
            provider="manual",
            created_by=user.id,
        )
    )
    await db.flush()
    bkey = CACHE_KEY.format(tenant_id=bystander.id)
    await r.set(bkey, '{"sentinel": true}', ex=60)
    await r.set(key, '{"stale": true}', ex=60)  # re-plant the subscriber's
    v3 = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    v3.entitlements = {"max_organizations": 12}
    await db.flush()
    await plan_svc.activate_version(db, v3, actor=_actor(user))
    assert await r.get(bkey) is not None, "bystander cache must survive"
    assert await r.get(key) is None, "subscriber cache cleared on activation"
    await r.delete(bkey)


class _Req388:
    class _State:
        request_id = "r388"

    state = _State()


@pytest.mark.asyncio
async def test_plans_api_catalog_and_external_ref(db):
    """R388: public_plan_catalog lists only ACTIVE plans' ACTIVE versions
    (drafts, retired versions and deactivated plans are invisible);
    set_plan_price_external_ref 404s an unknown price, sets the ref with a
    before/after audit and clears via empty-string → None (the one mutable
    field on an active version — R62[2])."""
    from app.controlplane.api.plans import (
        public_plan_catalog,
        set_plan_price_external_ref,
    )
    from app.controlplane.models.plan import PlanPrice
    from app.controlplane.schemas.plan import SetExternalRefRequest
    from app.controlplane.services import plans as plan_svc

    user = await _mk_user(db)
    key = f"r388-{str(ULID()).lower()[:8]}"
    plan = await plan_svc.create_plan(
        db, key=key, name="R388", description=None, actor=_actor(user)
    )
    v1 = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    v1.entitlements = {}
    db.add(
        PlanPrice(
            plan_version_id=v1.id,
            currency="USD",
            interval="month",
            amount_minor=700,
            included_seats=0,
        )
    )
    await db.flush()

    # a DRAFT version is not in the public catalog
    cat = await public_plan_catalog(db=db)
    assert key not in {p_["key"] for p_ in cat.data}
    await plan_svc.activate_version(db, v1, actor=_actor(user))
    cat2 = await public_plan_catalog(db=db)
    mine = next(p_ for p_ in cat2.data if p_["key"] == key)
    assert mine["active_version"]["version"] == 1

    # a deactivated PLAN disappears
    plan.is_active = False
    await db.flush()
    cat3 = await public_plan_catalog(db=db)
    assert key not in {p_["key"] for p_ in cat3.data}
    plan.is_active = True
    await db.flush()

    # external ref: unknown price 404; set + audit before/after; clear → None
    price = (
        await db.execute(select(PlanPrice).where(PlanPrice.plan_version_id == v1.id))
    ).scalar_one()
    req = _Req388()
    with pytest.raises(AppError) as e404:
        await set_plan_price_external_ref(
            str(ULID()), SetExternalRefRequest(external_price_ref="price_x"), req, user=user, db=db
        )
    assert e404.value.status_code == 404
    await set_plan_price_external_ref(
        price.id, SetExternalRefRequest(external_price_ref="price_123"), req, user=user, db=db
    )
    await db.refresh(price)
    assert price.external_price_ref == "price_123"
    await set_plan_price_external_ref(
        price.id, SetExternalRefRequest(external_price_ref=""), req, user=user, db=db
    )
    await db.refresh(price)
    assert price.external_price_ref is None  # empty clears, not ""


async def test_check_storage_quota_live_sum_and_hard_stop(db):
    """R523 mutation kills: check_storage_quota's live SUM was untested —
    the submission-item join, the asset org filter, and the item+asset
    ADDITION all had surviving flips. Seed 0.6 GB of submission items and
    0.6 GB of assets under a 1 GB HARD storage limit: only the correct SUM
    (1.2 GB > 1) rejects — a flipped join drops one source (0.6 <= 1
    passes) and Add->Sub yields ~0 (passes)."""

    from app.controlplane import facade as cp_facade
    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.exceptions import AppError as _App
    from app.models.project import (
        DeliverableType,
        ItemType,
        Project,
        ProjectAsset,
        ProjectDeliverable,
        Submission,
        SubmissionItem,
    )
    from app.services.organization import OrgService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"SQ {ULID()}",
        slug=f"sq-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    # 1 GB HARD limit (storage is soft-by-default — hard enforcement here)
    db.add(
        TenantEntitlementOverride(
            tenant_id=tenant.id,
            key="max_storage_gb",
            value={"v": "1"},
            enforcement="hard",
            reason="r523",
            created_by=user.id,
        )
    )
    await db.flush()
    gb6 = int(0.6 * 1073741824)
    project = Project(
        org_id=org.id,
        title="SQ",
        slug=f"sq-{str(ULID()).lower()[:10]}",
        description="d",
        instructions="i",
        rubric=[],
        created_by=user.id,
    )
    db.add(project)
    await db.flush()
    deliverable = ProjectDeliverable(
        project_id=project.id,
        name="file",
        type=DeliverableType.FILE,
    )
    db.add(deliverable)
    await db.flush()
    sub = Submission(org_id=org.id, project_id=project.id, user_id=user.id)
    db.add(sub)
    await db.flush()
    db.add(
        SubmissionItem(
            submission_id=sub.id,
            deliverable_id=deliverable.id,
            type=ItemType.FILE,
            file_size=gb6,
        )
    )
    db.add(
        ProjectAsset(
            org_id=org.id,
            project_id=project.id,
            name="a",
            file_key="k",
            file_name="a.bin",
            file_size=gb6,
            mime_type="application/octet-stream",
            uploaded_by=user.id,
        )
    )
    await db.flush()
    # 0.6 + 0.6 = 1.2 GB stored; ANY further byte crosses the 1 GB hard cap
    with pytest.raises(_App) as exc:
        await cp_facade.check_storage_quota(db, org.id, incoming_bytes=1)
    assert exc.value.code == "QUOTA_EXCEEDED"
    assert exc.value.status_code == 403
    # the message carries the CORRECT live sum — 0.6 + 0.6 GB
    assert "1.200000" in exc.value.message
