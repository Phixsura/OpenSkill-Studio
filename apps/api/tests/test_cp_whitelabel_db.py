"""P10 DB tests: branding validation, domains, blueprints/provisioning,
export whitelist, suspension surface."""

import pytest
from sqlalchemy import func, select
from ulid import ULID

from app.controlplane.models.branding import TenantBlueprint
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import branding as branding_svc
from app.controlplane.services import domains as domain_svc
from app.controlplane.services import provisioning as provision_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
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


async def _mk_user(db) -> User:
    user = User(
        email=f"cp10-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP10",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"W {ULID()}",
        slug=f"w-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── Hostname normalization (pure) ────────────────────────────


def test_hostname_normalization_matrix():
    n = domain_svc.normalize_hostname
    assert n("AI.Example-School.COM") == "ai.example-school.com"
    assert n("https://academy.partner.com/") == "academy.partner.com"
    assert n("academy.partner.com:8443") == "academy.partner.com"
    assert n("school.example.com.") == "school.example.com"
    assert n("学校.example.com") == "xn--48s290a.example.com"  # IDNA
    for bad in ("", "single-label", "-bad.example.com", "a b.example.com", "a..b.com"):
        with pytest.raises(AppError):
            n(bad)


def test_reserved_domain_rejection():
    c = domain_svc.check_reserved
    for reserved in ("localhost", "app.localhost", "192.168.1.1", "2001:db8::1"):
        with pytest.raises(AppError) as exc:
            c(reserved if "." in reserved or ":" in reserved else reserved)
        assert exc.value.code == "DOMAIN_RESERVED"
    c("ai.example-school.com")  # fine


def test_theme_token_validation():
    v = branding_svc.validate_theme_tokens
    v({"primary": "#1a2b3c", "radius": "md"})
    for bad in (
        {"primary": "red"},
        {"primary": "#12345"},
        {"primary": "url(javascript:alert(1))"},
        {"unknown_key": "#123456"},
        {"radius": "9999px"},
    ):
        with pytest.raises(AppError) as exc:
            v(bad)
        assert exc.value.code == "BRANDING_INVALID"


def test_legal_links_and_urls():
    branding_svc.validate_legal_links([{"label": "Terms", "url": "https://x.com/terms"}])
    for bad in (
        [{"label": "T", "url": "http://insecure.com"}],
        [{"label": "T", "url": "javascript:alert(1)"}],
        [{"label": "T" * 60, "url": "https://x.com"}],
        [{"label": "T", "url": "https://x.com", "extra": 1}],
    ):
        with pytest.raises(AppError):
            branding_svc.validate_legal_links(bad)


def test_blueprint_config_rejects_runtime_data_keys():
    """Issue §8 red line: the schema structurally rejects user/credential keys."""
    from pydantic import ValidationError

    v = provision_svc.validate_blueprint_config
    v({"plan_key": "school", "org": {"name_template": "{tenant_name} Campus"}})
    for bad in (
        {"users": [{"email": "a@b.c"}]},
        {"credentials": {"api_key": "sk-123"}},
        {"submissions": []},
        {"billing_records": []},
        {"org": {"name_template": "x", "members": []}},
    ):
        with pytest.raises(ValidationError):  # extra=forbid
            v(bad)


# ── Domain lifecycle ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_domain_flow_verify_activate(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    domain, raw = await domain_svc.create_domain(
        db, tenant_id=tenant.id, hostname="AI.Example-School.com", actor=_actor(user)
    )
    assert domain.hostname == "ai.example-school.com"
    assert domain.status == "pending_verification"
    assert raw not in domain.verification_token_hash
    # Forged token with the passing prefix → hash mismatch BEFORE the verifier
    # (a valid-looking "ok-" token from another source can't verify)
    with pytest.raises(AppError) as exc:
        await domain_svc.verify_domain(db, domain, "ok-forged", actor=_actor(user))
    assert exc.value.code == "DOMAIN_VERIFY_FAILED"
    # Verifier consultation: rewrite the hash to a NON-passing token → the
    # mock verifier rejects it and counts the attempt
    import hashlib

    non_passing = "openskill-verify-x"
    domain.verification_token_hash = hashlib.sha256(non_passing.encode()).hexdigest()
    await db.flush()
    with pytest.raises(AppError) as exc2:
        await domain_svc.verify_domain(db, domain, non_passing, actor=_actor(user))
    assert exc2.value.code == "DOMAIN_VERIFY_FAILED"
    assert domain.verify_attempts == 1
    # Restore the real token → passes (mock mode issues "ok-" tokens)
    domain.verification_token_hash = hashlib.sha256(raw.encode()).hexdigest()
    await db.flush()
    domain = await domain_svc.verify_domain(db, domain, raw, actor=_actor(user))
    assert domain.status == "verified"
    domain = await domain_svc.activate_domain(db, domain, actor=_actor(user))
    assert domain.status == "active"
    # Activation is guarded: re-activating an active domain → 409
    with pytest.raises(AppError):
        await domain_svc.activate_domain(db, domain, actor=_actor(user))


@pytest.mark.asyncio
async def test_domain_uniqueness_and_site_context(db):
    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    tenant_a = await _mk_tenant(db, user_a)
    tenant_b = await _mk_tenant(db, user_b)
    host = f"school-{str(ULID()).lower()[:8]}.example.io"
    domain, raw = await domain_svc.create_domain(
        db, tenant_id=tenant_a.id, hostname=host, actor=_actor(user_a)
    )
    # Cross-tenant duplicate → 409 without revealing the owner
    with pytest.raises(AppError) as exc:
        await domain_svc.create_domain(
            db, tenant_id=tenant_b.id, hostname=host.upper(), actor=_actor(user_b)
        )
    assert exc.value.code == "DOMAIN_TAKEN"
    assert tenant_a.id not in exc.value.message and tenant_a.slug not in exc.value.message
    # site-context: pending domain resolves to NOTHING (no half-activation leak)
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] is None
    # Activate → resolves; disabled → dark again
    import hashlib

    passing = "ok-x"
    domain.verification_token_hash = hashlib.sha256(passing.encode()).hexdigest()
    await db.flush()
    await domain_svc.verify_domain(db, domain, passing, actor=_actor(user_a))
    await domain_svc.activate_domain(db, domain, actor=_actor(user_a))
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] == tenant_a.id
    await domain_svc.disable_domain(db, domain, actor=_actor(user_a))
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] is None
    # Garbage host → platform default, never an error
    ctx = await domain_svc.resolve_site_context(db, "///bad host///")
    assert ctx["tenant_id"] is None


# ── Provisioning ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_provision_run_completes_with_zero_runtime_rows(db):
    user = await _mk_user(db)
    blueprint = TenantBlueprint(
        name=f"BP {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {
                "plan_key": "school",
                "entitlement_overrides": {"max_active_learners": 500},
                "branding": {
                    "product_display_name": "Partner Academy",
                    "theme_tokens": {"primary": "#123456"},
                },
                "org": {"name_template": "{tenant_name} Campus"},
            }
        ),
        created_by=user.id,
    )
    db.add(blueprint)
    await db.flush()
    slug = f"prov-{str(ULID()).lower()[:10]}"
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=blueprint.id,
        name="Example Education Group",
        slug=slug,
        idempotency_key=f"prov-{ULID()}",
        partner_id=None,
        actor=_actor(user),
    )
    # Idempotent replay returns the same run
    replay = await provision_svc.create_provision_run(
        db,
        blueprint_id=blueprint.id,
        name="Example Education Group",
        slug=slug,
        idempotency_key=run.idempotency_key,
        partner_id=None,
        actor=_actor(user),
    )
    assert replay.id == run.id
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed", run.error
    assert run.tenant_id is not None
    tenant = await db.get(TenantAccount, run.tenant_id)
    assert tenant.status == TenantStatus.ACTIVE
    # Subscription active on school
    from app.controlplane.services.billing import get_live_subscription

    sub = await get_live_subscription(db, tenant.id)
    assert sub is not None and sub.status == "active"
    # Entitlement override applied
    from app.controlplane.models.plan import TenantEntitlementOverride

    override = (
        await db.execute(
            select(TenantEntitlementOverride).where(
                TenantEntitlementOverride.tenant_id == tenant.id,
                TenantEntitlementOverride.key == "max_active_learners",
            )
        )
    ).scalar_one()
    assert override.value["v"] == 500
    # Branding applied
    from app.controlplane.models.branding import TenantBranding

    branding = (
        await db.execute(select(TenantBranding).where(TenantBranding.tenant_id == tenant.id))
    ).scalar_one()
    assert branding.product_display_name == "Partner Academy"
    # ZERO runtime rows (issue §8 acceptance): no learners/submissions/progress
    from app.models.organization import Organization, OrgMember, OrgRole
    from app.models.project import Submission

    org_ids = select(Organization.id).where(Organization.tenant_id == tenant.id)
    students = (
        await db.execute(
            select(func.count(OrgMember.id)).where(
                OrgMember.org_id.in_(org_ids), OrgMember.role == OrgRole.STUDENT
            )
        )
    ).scalar_one()
    submissions = (
        await db.execute(select(func.count(Submission.id)).where(Submission.org_id.in_(org_ids)))
    ).scalar_one()
    assert students == 0 and submissions == 0
    # Rerun on completed = no-op
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed"


@pytest.mark.asyncio
async def test_provision_resume_after_failure(db):
    """A run failing mid-way (bad pack ref) resumes from the failed step."""
    user = await _mk_user(db)
    blueprint = TenantBlueprint(
        name=f"BPF {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {
                "skill_packs": [{"pack_id": "01JNOPENOPACKAAAAAAAAAAAAA"}],  # nonexistent
            }
        ),
        created_by=user.id,
    )
    db.add(blueprint)
    await db.flush()
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=blueprint.id,
        name="Fail Then Resume",
        slug=f"ftr-{str(ULID()).lower()[:10]}",
        idempotency_key=f"ftr-{ULID()}",
        partner_id=None,
        actor=_actor(user),
    )
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "failed"
    assert run.tenant_id is not None  # earlier steps persisted
    done_steps = [s["step"] for s in run.steps if s.get("status") == "done"]
    assert "create_tenant" in done_steps and "create_org" in done_steps
    # Fix the blueprint's snapshotted config? No — snapshot is frozen. Instead
    # verify resume skips completed steps and fails at the same point again.
    tenant_id_before = run.tenant_id
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.tenant_id == tenant_id_before  # no duplicate tenant created
    tenants_with_name = (
        await db.execute(
            select(func.count(TenantAccount.id)).where(TenantAccount.name == "Fail Then Resume")
        )
    ).scalar_one()
    assert tenants_with_name == 1


@pytest.mark.asyncio
async def test_provision_resume_tolerates_already_installed_packs(db, monkeypatch):
    """R38/C33: install_skill_packs has no per-pack progress marker, so a
    resume re-runs the whole loop. Packs installed before an earlier failure
    are committed → their ALREADY_INSTALLED must be treated as success, or the
    run can never complete. Simulate pack A already-installed + pack B fresh."""
    from app.services import installation as install_mod

    user = await _mk_user(db)
    blueprint = TenantBlueprint(
        name=f"BPR {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {
                "skill_packs": [
                    {"pack_id": "01JPACKAAAAAAAAAAAAAAAAAAA"},
                    {"pack_id": "01JPACKBBBBBBBBBBBBBBBBBBB"},
                ]
            }
        ),
        created_by=user.id,
    )
    db.add(blueprint)
    await db.flush()
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=blueprint.id,
        name="Resume Already",
        slug=f"ra-{str(ULID()).lower()[:10]}",
        idempotency_key=f"ra-{ULID()}",
        partner_id=None,
        actor=_actor(user),
    )

    installed: list[str] = []

    async def fake_install_pack(self, org_id, pack_id, version, installed_by):
        # Pack A is "already installed" (committed by a prior attempt);
        # pack B installs fine. The step must complete despite A's 409.
        if pack_id.endswith("AAA"):
            raise AppError("ALREADY_INSTALLED", "Pack already installed", 409)
        installed.append(pack_id)

    monkeypatch.setattr(install_mod.InstallationService, "install_pack", fake_install_pack)
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed", run.error
    assert installed == ["01JPACKBBBBBBBBBBBBBBBBBBB"]  # only the fresh one installed
    done = [s["step"] for s in run.steps if s.get("status") == "done"]
    assert "install_skill_packs" in done


# ── Export ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_whitelist_excludes_sensitive_data(db, monkeypatch):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    captured: dict = {}

    async def fake_s3():
        class FakeClient:
            async def put_object(self, **kw):
                captured["body"] = kw["Body"].decode()
                captured["key"] = kw["Key"]

        yield FakeClient()

    monkeypatch.setattr("app.core.storage.get_s3_client", fake_s3)
    export = await provision_svc.build_export(db, tenant.id, actor=_actor(user))
    assert export.status == "completed"
    body = captured["body"]
    import json

    bundle = json.loads(body)
    assert bundle["export_schema"] == 1
    assert bundle["tenant"]["id"] == tenant.id
    # Excluded classes never appear (issue §35)
    for forbidden in (
        "token_hash",
        "encrypted_data",
        "internal_cost",
        "unit_cost",
        "password",
        "api_key",
    ):
        assert forbidden not in body, forbidden


# ── Suspension surface ───────────────────────────────────────


@pytest.mark.asyncio
async def test_suspension_blocks_costed_surfaces(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await tenant_svc.transition_status(
        db, tenant, TenantStatus.SUSPENDED, actor=_actor(user), reason="t"
    )
    with pytest.raises(AppError) as exc:
        tenant_svc.require_tenant_active(tenant)
    assert exc.value.code == "TENANT_SUSPENDED"
    # Reactivate restores with no rebuild
    await tenant_svc.transition_status(db, tenant, TenantStatus.ACTIVE, actor=_actor(user))
    tenant_svc.require_tenant_active(tenant)  # no raise
