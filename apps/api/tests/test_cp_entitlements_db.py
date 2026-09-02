"""P2 DB tests: plans, versions, entitlement engine, quota enforcement."""

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
        await engine.dispose()


# ── Validation ───────────────────────────────────────────────


def test_validate_entitlement_value_matrix():
    assert validate_entitlement_value("custom_domain", True) is True
    assert validate_entitlement_value("max_organizations", 5) == 5
    assert validate_entitlement_value("max_storage_gb", "12.5") == "12.5"
    assert validate_entitlement_value("max_ai_budget_usd_month", None) is None
    for key, bad in [
        ("nope_key", 1),
        ("custom_domain", "yes"),
        ("custom_domain", None),
        ("max_organizations", -1),
        ("max_organizations", True),  # bool is not an int here
        ("max_storage_gb", "NaN"),
        ("max_storage_gb", "-3"),
    ]:
        with pytest.raises(AppError):
            validate_entitlement_value(key, bad)


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
        await engine.dispose()
