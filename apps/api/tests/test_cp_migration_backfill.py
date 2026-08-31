"""P12: backfill correctness invariants (migration cp01a0000001).

These are PROPERTY tests over the live schema+data rather than a
migration-rerun harness — test_deployment.py already exercises the alembic
chain, and concurrent DDL against the shared dev DB deadlocks. Every
invariant here is one the backfill promised:

  1. organizations.tenant_id is NOT NULL (enforced) and FK-valid
  2. no org points at a missing tenant (RESTRICT holds)
  3. backfilled tenant slugs are unique
  4. grandfathering overrides (reason='migration grandfathering') only exist
     for registry keys and carry non-expiring hard/soft values
  5. seed plans exist: 5 plans, each with exactly one ACTIVE version
"""

import pytest
from sqlalchemy import func, select, text

from app.controlplane.models.plan import (
    PlanVersion,
    ProductPlan,
    TenantEntitlementOverride,
)
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.services.entitlements import ENTITLEMENT_DEFS
from app.core.database import AsyncSessionLocal
from app.models.organization import Organization


@pytest.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_every_org_has_a_tenant(db):
    # Column is NOT NULL at the schema level
    nullable = (
        await db.execute(
            text(
                "SELECT is_nullable FROM information_schema.columns "
                "WHERE table_name='organizations' AND column_name='tenant_id'"
            )
        )
    ).scalar_one()
    assert nullable == "NO"
    # And no dangling references (FK RESTRICT should make this impossible)
    dangling = (
        await db.execute(
            select(func.count(Organization.id))
            .outerjoin(TenantAccount, TenantAccount.id == Organization.tenant_id)
            .where(TenantAccount.id.is_(None))
        )
    ).scalar_one()
    assert dangling == 0


@pytest.mark.asyncio
async def test_tenant_slugs_unique(db):
    dupes = (
        await db.execute(
            select(TenantAccount.slug, func.count(TenantAccount.id))
            .group_by(TenantAccount.slug)
            .having(func.count(TenantAccount.id) > 1)
        )
    ).all()
    assert dupes == []


@pytest.mark.asyncio
async def test_grandfathering_overrides_valid(db):
    rows = (
        (
            await db.execute(
                select(TenantEntitlementOverride).where(
                    TenantEntitlementOverride.reason == "migration grandfathering"
                )
            )
        )
        .scalars()
        .all()
    )
    for override in rows:
        assert override.key in ENTITLEMENT_DEFS, override.key
        assert override.expires_at is None  # non-expiring by design
        assert "v" in override.value


@pytest.mark.asyncio
async def test_seed_plans_present_one_active_version_each(db):
    plans = (await db.execute(select(ProductPlan).order_by(ProductPlan.sort_order))).scalars().all()
    keys = {p.key for p in plans}
    assert {"community", "school", "growth", "enterprise", "oem"} <= keys
    for plan in plans:
        if plan.key not in ("community", "school", "growth", "enterprise", "oem"):
            continue
        active = (
            (
                await db.execute(
                    select(PlanVersion).where(
                        PlanVersion.plan_id == plan.id, PlanVersion.status == "active"
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(active) == 1, plan.key
        # Every entitlement key in the version is registry-known
        for key in active[0].entitlements:
            assert key in ENTITLEMENT_DEFS, f"{plan.key}: {key}"


@pytest.mark.asyncio
async def test_org_auto_creates_trial_tenant(db):
    """The §1.7 path: creating an org with no tenant context auto-creates a
    TRIAL tenant in the same transaction."""
    from ulid import ULID

    from app.core.security import hash_password
    from app.models.user import User, UserRole, UserStatus
    from app.services.organization import OrgService

    user = User(
        email=f"bf-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="BF",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    org = await OrgService(db).create(
        name=f"BF Org {str(ULID()).lower()[-6:]}",
        slug=f"bf-{str(ULID()).lower()}",
        description="d",
        created_by=user.id,
    )
    assert org.tenant_id is not None
    tenant = await db.get(TenantAccount, org.tenant_id)
    assert tenant.status.value == "trial"
    assert tenant.trial_ends_at is not None
