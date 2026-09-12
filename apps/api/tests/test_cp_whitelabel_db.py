"""P10 DB tests: branding validation, domains, blueprints/provisioning,
export whitelist, suspension surface.
R516 mutation sweep of validate_blueprint_config/_step_done/
create_provision_run/build_export: the headline finding was six
`tenant_id ==` -> `!=` survivors on export sections (now killed by
test_export_sections_are_tenant_scoped, together with the L529
cancelled-subscription gate). Remaining classified survivors:
- L505 OrgMember.status == ACTIVE / L510 User.status != DELETED and
  L552 invoice-line outerjoin shape: member-roster filter and join-shape
  contracts inside the organizations/invoices sections — not privacy
  boundaries (rows are still the exporting tenant's own), currently
  unasserted; acceptable residuals.
- L616/L642 truncation flags for payments/credit_notes: the truncation
  MECHANISM is pinned for ledger/licenses/invoices (R138); these two
  flags share the identical code shape.
- L779 error-message truncation 2000 -> 2001: cosmetic bound.
"""

import pytest
from sqlalchemy import func, select
from ulid import ULID

from app.controlplane.models.branding import TenantBlueprint, TenantDomain
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

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
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
        with pytest.raises(AppError) as exc:
            n(bad)
        assert exc.value.status_code == 422

    # R248 boundary pins (mutation-driven): exactly-at-limit accepted,
    # one-past rejected — a >→>= or 253→254 flip breaks real registrations.
    label63 = "a" * 63
    host253 = ".".join([label63, label63, label63, "a" * 57, "com"])
    assert len(host253) == 253
    assert n(host253) == host253                     # 253 chars OK, 63-label OK
    with pytest.raises(AppError):                    # 254 chars (valid labels)
        n(("b." + host253)[:254].rstrip("."))
    with pytest.raises(AppError):                    # 64-char label
        n("a" * 64 + ".com")
    assert n("a.com") == "a.com"                     # exactly two labels OK
    with pytest.raises(AppError) as exc:             # un-IDNA-encodable label
        n("\u00ad.example.com")                      # soft hyphen → empty label
    assert exc.value.status_code == 422


def test_reserved_domain_rejection():
    c = domain_svc.check_reserved
    for reserved in ("localhost", "app.localhost", "192.168.1.1", "2001:db8::1"):
        with pytest.raises(AppError) as exc:
            c(reserved if "." in reserved or ":" in reserved else reserved)
        assert exc.value.code == "DOMAIN_RESERVED" and exc.value.status_code == 422
    c("ai.example-school.com")  # fine

    # R248: the localhost arm must hold WITHOUT the platform-base-domain
    # fallback (an or→and flip silently delegated it to config).
    from unittest.mock import patch

    from app.config import settings as _settings

    with patch.object(_settings, "platform_base_domains", []):
        for host in ("localhost", "dev.localhost"):
            with pytest.raises(AppError) as exc:
                c(host)
            assert exc.value.code == "DOMAIN_RESERVED"
        c("ai.example-school.com")  # still fine with empty base list


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
        # R137: non-str url inside the untyped list[dict] 500'd on .startswith
        [{"label": "T", "url": 123}],
        [{"label": "T", "url": {"nested": "x"}}],
        [{"label": "T", "url": None}],
    ):
        with pytest.raises(AppError):
            branding_svc.validate_legal_links(bad)


def test_blueprint_config_rejects_runtime_data_keys():
    """Issue §8 red line: the schema structurally rejects user/credential keys.
    R99[33]: rejection now surfaces as AppError 422 (pydantic ValidationError
    escaped FastAPI's request-model wrapping and 500'd)."""
    v = provision_svc.validate_blueprint_config
    v({"plan_key": "school", "org": {"name_template": "{tenant_name} Campus"}})
    for bad in (
        {"users": [{"email": "a@b.c"}]},
        {"credentials": {"api_key": "sk-123"}},
        {"submissions": []},
        {"billing_records": []},
        {"org": {"name_template": "x", "members": []}},
    ):
        with pytest.raises(AppError) as exc:  # extra=forbid → clean 422
            v(bad)
        assert exc.value.status_code == 422


# ── Domain lifecycle ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_domain_flow_verify_activate(db, monkeypatch):
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
    assert exc.value.status_code == 422  # R339
    # R339: activation is gated on VERIFIED — a pending domain 409s
    with pytest.raises(AppError) as excg:
        await domain_svc.activate_domain(db, domain, actor=_actor(user))
    assert excg.value.code == "DOMAIN_STATUS_CONFLICT" and excg.value.status_code == 409
    # Verifier consultation: rewrite the hash to a NON-passing token → the
    # mock verifier rejects it and counts the attempt
    import hashlib

    non_passing = "openskill-verify-x"
    domain.verification_token_hash = hashlib.sha256(non_passing.encode()).hexdigest()
    await db.flush()
    with pytest.raises(AppError) as exc2:
        await domain_svc.verify_domain(db, domain, non_passing, actor=_actor(user))
    assert exc2.value.code == "DOMAIN_VERIFY_FAILED"
    assert exc2.value.status_code == 422  # R339
    assert domain.verify_attempts == 1
    # Restore the real token → passes (mock mode issues "ok-" tokens)
    domain.verification_token_hash = hashlib.sha256(raw.encode()).hexdigest()
    await db.flush()
    domain = await domain_svc.verify_domain(db, domain, raw, actor=_actor(user))
    assert domain.status == "verified"
    # R339: a SECOND (unrelated) domain must be untouched by activation —
    # the TLS-values UPDATE targets exactly the activated row
    other = TenantDomain(
        tenant_id=domain.tenant_id, hostname=f"other-{str(ULID()).lower()[:8]}.example.com",
        status="pending_verification", verification_token_hash="y", created_by=user.id)
    db.add(other)
    await db.flush()
    from app.config import settings as _settings

    monkeypatch.setattr(_settings, "tls_provisioner", "mock")
    domain = await domain_svc.activate_domain(db, domain, actor=_actor(user))
    assert domain.status == "active"
    await db.refresh(domain)
    assert domain.tls_ref == f"mock-cert-{domain.hostname}"  # cert landed HERE
    await db.refresh(other)
    # the TLS update targeted exactly the activated row
    assert other.tls_ref is None and other.status == "pending_verification"
    # Activation is guarded: re-activating an active domain → 409
    with pytest.raises(AppError) as exca:
        await domain_svc.activate_domain(db, domain, actor=_actor(user))
    assert exca.value.status_code == 409  # R339
    # R339: re-verifying an ACTIVE domain is also a status conflict (409)
    with pytest.raises(AppError) as excv:
        await domain_svc.verify_domain(db, domain, raw, actor=_actor(user))
    assert excv.value.code == "DOMAIN_STATUS_CONFLICT" and excv.value.status_code == 409


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
    # R518 mutation kill: real branding CONTENT must survive resolution — the
    # `(x if branding else None) or {}` fallbacks flipped to `and` serve {}/[]
    # for every tenant with real tokens/links (only the null-coalesce R330
    # path was asserted before).
    from app.controlplane.services import branding as branding_svc

    await branding_svc.upsert_branding(
        db,
        tenant_a.id,
        {
            "product_display_name": "Acme Academy",
            "theme_tokens": {"primary": "#112233"},
            "legal_links": [{"label": "Terms", "url": "https://a.example/terms"}],
        },
        actor=_actor(user_a),
    )
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] == tenant_a.id
    assert ctx["branding"]["theme_tokens"] == {"primary": "#112233"}
    assert ctx["branding"]["legal_links"] == [
        {"label": "Terms", "url": "https://a.example/terms"}
    ]
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


@pytest.mark.asyncio
async def test_provision_pack_savepoint_rolls_back_partial_copy(db, monkeypatch):
    """R321 (pins R46[28]): each pack install runs in a SAVEPOINT so a
    mid-copy failure rolls back THAT pack's partially-flushed content
    (categories/skills) instead of leaving it committed — otherwise a retry
    duplicates the committed half. Simulate an install that flushes a
    category then dies; the marker row must be GONE after the failed run."""
    from app.models.skill import SkillCategory
    from app.services import installation as install_mod

    user = await _mk_user(db)
    blueprint = TenantBlueprint(
        name=f"BPS {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {"skill_packs": [{"pack_id": "01JPACKCCCCCCCCCCCCCCCCCCC"}]}
        ),
        created_by=user.id,
    )
    db.add(blueprint)
    await db.flush()
    run = await provision_svc.create_provision_run(
        db,
        blueprint_id=blueprint.id,
        name="Partial Copy",
        slug=f"pc-{str(ULID()).lower()[:10]}",
        idempotency_key=f"pc-{ULID()}",
        partner_id=None,
        actor=_actor(user),
    )

    marker_slug = f"r321-partial-{str(ULID()).lower()[:8]}"

    async def dying_install_pack(self, org_id, pack_id, version, installed_by):
        # flush half the pack's content, then fail mid-copy
        self.db.add(
            SkillCategory(org_id=org_id, name="R321 partial", slug=marker_slug)
        )
        await self.db.flush()
        raise AppError("PACK_CORRUPT", "manifest checksum mismatch", 422)

    monkeypatch.setattr(
        install_mod.InstallationService, "install_pack", dying_install_pack
    )
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "failed"
    failed = [s["step"] for s in run.steps if s.get("status") == "failed"]
    assert failed == ["install_skill_packs"]
    assert "not installable" in (run.error or "")

    # the SAVEPOINT must have rolled the partial copy back
    leftover = (
        await db.execute(
            select(SkillCategory).where(SkillCategory.slug == marker_slug)
        )
    ).scalars().all()
    assert leftover == [], "partial pack content survived the failed install"

    # and the failure handler's own writes survived (session not aborted)
    assert run.error is not None


# ── Export ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_whitelist_excludes_sensitive_data(db, monkeypatch):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    captured: dict = {}

    async def fake_s3():
        class FakeClient:
            async def head_bucket(self, **kw):  # R65[23] private export bucket
                return {}

            async def create_bucket(self, **kw):
                return {}

            async def put_object(self, **kw):
                captured["body"] = kw["Body"].decode()
                captured["key"] = kw["Key"]
                captured["bucket"] = kw["Bucket"]

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


# ── R46: provisioning hardening ───────────────────────────────


@pytest.mark.asyncio
async def test_partner_blueprint_rejects_entitlement_overrides(db):
    """R46[25]: entitlement overrides are a platform power — a partner admin
    authoring them into a blueprint escalated arbitrary hard overrides."""
    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.partner import Partner, PartnerMember
    from app.core.security import create_access_token
    from app.main import app

    user = await _mk_user(db)
    partner = Partner(
        name=f"BP {ULID()}",
        slug=f"bp-{str(ULID()).lower()}",
        partner_type="reseller",
        currency="USD",
        created_by=user.id,
    )
    db.add(partner)
    await db.flush()
    db.add(PartnerMember(partner_id=partner.id, user_id=user.id, role="admin", created_by=user.id))
    await db.commit()
    token = create_access_token(user.id, user.email, user.role.value)
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                f"/api/v1/partners/{partner.id}/blueprints",
                json={
                    "name": "Escalate",
                    "config": {"entitlement_overrides": {"max_organizations": 999999}},
                },
                headers={"Authorization": f"Bearer {token}"},
            )
        assert r.status_code == 422, r.text
        assert r.json()["error"]["code"] == "BLUEPRINT_INVALID"
    finally:
        app.router.lifespan_context = orig


@pytest.mark.asyncio
async def test_provision_org_slug_collision_suffixes(db):
    """R46[26]: the create_org step must fall back to a suffixed slug when the
    requested slug collides with any existing org (globally unique)."""
    from app.controlplane.models.branding import TenantBlueprint, TenantProvisionRun
    from app.controlplane.services import provisioning as prov_svc
    from app.models.organization import Organization
    from app.services.organization import OrgService

    user = await _mk_user(db)
    taken_slug = f"prov-{str(ULID()).lower()}"
    await OrgService(db).create(name="Taken", slug=taken_slug, description=None, created_by=user.id)
    bp = TenantBlueprint(
        name=f"B {ULID()}",
        config={"org": {"name_template": "{tenant_name} Campus"}},
        created_by=user.id,
    )
    db.add(bp)
    await db.flush()
    run = TenantProvisionRun(
        blueprint_id=bp.id,
        requested_name=f"Prov {ULID()}",
        requested_slug=taken_slug,  # collides
        idempotency_key=f"prov-{ULID()}",
        created_by=user.id,
    )
    db.add(run)
    await db.flush()
    await prov_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed", run.steps
    org_step = next(s for s in run.steps if s["step"] == "create_org")
    org = await db.get(Organization, org_step["org_id"])
    assert org.slug != taken_slug
    assert org.slug.startswith(taken_slug[:20]) or "-" in org.slug


def test_reserved_domain_whitespace_in_config(monkeypatch):
    """R79[1]: platform_base_domains entries with surrounding whitespace
    (' openskill.app' from a hand-edited JSON env) never matched — the
    platform apex and every subdomain became registrable by any tenant."""
    from app.config import settings as app_settings

    monkeypatch.setattr(
        app_settings, "platform_base_domains", [" openskill.app ", "", "  .Padded.IO"]
    )
    for host in ("openskill.app", "evil.openskill.app", "x.padded.io"):
        with pytest.raises(AppError) as exc:
            domain_svc.check_reserved(host)
        assert exc.value.code == "DOMAIN_RESERVED", host
        assert exc.value.status_code == 422
    domain_svc.check_reserved("unrelated-school.com")  # still fine


@pytest.mark.asyncio
async def test_webhook_delivery_gated_by_entitlement(db):
    """R77[2]: 'webhooks' was enforced only at subscription CREATE —
    suspended tenants (SUSPENSION_MASKED_KEYS masks webhooks) kept
    delivering through pre-existing subscriptions. The delivery path itself
    now checks the effective entitlement."""
    from app.controlplane.services.entitlements import invalidate_cache
    from app.models.webhook import WebhookSubscription
    from app.services.organization import OrgService
    from app.services.webhook import WebhookService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"WH {ULID()}",
        slug=f"wh-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await invalidate_cache(tenant.id)
    sub = WebhookSubscription(
        org_id=org.id,
        url="https://example.com/hook",
        secret="s" * 32,
        events=["pack.installed"],
        active=True,
    )
    db.add(sub)
    await db.flush()

    svc = WebhookService(db)
    scheduled: list = []

    async def counting_deliver(url, secret, webhook_id, event_type, payload):
        scheduled.append(webhook_id)

    from unittest.mock import patch as _patch

    from app.services.webhook import WebhookService as WhSvc

    with _patch.object(WhSvc, "_deliver_background", staticmethod(counting_deliver)):
        # Active tenant → delivery scheduled
        await svc.trigger_event(org.id, "pack.installed", {"x": 1})
        import asyncio as _asyncio

        await _asyncio.sleep(0.05)  # let the fire-and-forget task run
        assert scheduled == [sub.id]
        # Suspended tenant (webhooks masked) → NOTHING scheduled
        tenant.status = TenantStatus.SUSPENDED
        await db.flush()
        await invalidate_cache(tenant.id)
        await svc.trigger_event(org.id, "pack.installed", {"x": 1})
        await _asyncio.sleep(0.05)
        assert scheduled == [sub.id], "suspended tenant must not deliver"
    # The subscription row is untouched (still active) — only delivery gated
    await db.refresh(sub)
    assert sub.active is True


# ── R83: domain verifier boot guard + terminal-tenant darkening ──


def test_domain_verifier_production_boot_guard():
    """R83[4]: 'mock' always verifies — production boot must refuse it, the
    same way it refuses the default jwt_secret."""
    import pydantic
    import pytest as _pytest

    from app.config import Settings

    with _pytest.raises(pydantic.ValidationError, match="DOMAIN_VERIFIER"):
        Settings(
            app_env="production",
            jwt_secret="x" * 40,
            s3_secret_key="not-default",
            database_url="postgresql+asyncpg://u:p@h/db",
            credential_encryption_key="",
            domain_verifier="mock",
        )
    # dns passes the guard (other validators may still object to other fields)
    s = Settings(
        app_env="development",
        domain_verifier="mock",
    )
    assert s.domain_verifier == "mock"  # dev keeps the convenient default


@pytest.mark.asyncio
async def test_site_context_dark_for_terminal_tenants(db):
    """R83[5]: CANCELLED/ARCHIVED tenants kept resolving white-label branding
    forever. Terminal states go dark; SUSPENDED keeps resolving (ADR §10.7)."""
    from app.controlplane.models.branding import TenantDomain

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    tenant.status = TenantStatus.ACTIVE
    host = f"school-{str(ULID()).lower()[:8]}.example-live.com"
    db.add(
        TenantDomain(
            tenant_id=tenant.id,
            hostname=host,
            status="active",
            verification_token_hash="x" * 64,
            created_by=user.id,
        )
    )
    await db.flush()
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] == tenant.id
    # SUSPENDED keeps resolving
    tenant.status = TenantStatus.SUSPENDED
    await db.flush()
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] == tenant.id
    # CANCELLED goes dark
    tenant.status = TenantStatus.CANCELLED
    await db.flush()
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] is None
    # ARCHIVED stays dark
    tenant.status = TenantStatus.ARCHIVED
    await db.flush()
    ctx = await domain_svc.resolve_site_context(db, host)
    assert ctx["tenant_id"] is None


@pytest.mark.asyncio
async def test_stale_pending_domain_claim_evicted(db):
    """R83[M2]: never-verified pending rows held the global hostname unique
    forever — squat any tenant's future domain by registering first. A stale
    (>7d) pending claim is evicted for a new registrant; verified/active
    claims keep anti-sniping semantics."""

    from app.controlplane.models.branding import TenantDomain

    user = await _mk_user(db)
    squatter = await _mk_tenant(db, user)
    victim = await _mk_tenant(db, user)
    host = f"squatted-{str(ULID()).lower()[:8]}.example-live.com"
    # Squatter registered 8 days ago, never verified
    stale = TenantDomain(
        tenant_id=squatter.id,
        hostname=host,
        status="pending_verification",
        verification_token_hash="x" * 64,
        created_by=user.id,
    )
    db.add(stale)
    await db.flush()
    from sqlalchemy import text as _text

    await db.execute(
        _text("UPDATE cp_tenant_domains SET created_at = now() - interval '8 days' WHERE id = :i"),
        {"i": stale.id},
    )
    db.expire(stale)  # the service re-reads the row; drop the stale identity-map copy
    # Victim can now claim it
    domain, raw = await domain_svc.create_domain(
        db, tenant_id=victim.id, hostname=host, actor=_actor(user)
    )
    assert domain.tenant_id == victim.id
    # A FRESH pending claim is NOT evicted
    host2 = f"fresh-{str(ULID()).lower()[:8]}.example-live.com"
    await domain_svc.create_domain(db, tenant_id=squatter.id, hostname=host2, actor=_actor(user))
    with pytest.raises(AppError) as exc:
        await domain_svc.create_domain(db, tenant_id=victim.id, hostname=host2, actor=_actor(user))
    assert exc.value.code == "DOMAIN_TAKEN"
    # An ACTIVE claim is never evicted regardless of age
    host3 = f"act-{str(ULID()).lower()[:8]}.example-live.com"
    active = TenantDomain(
        tenant_id=squatter.id,
        hostname=host3,
        status="active",
        verification_token_hash="y" * 64,
        created_by=user.id,
    )
    db.add(active)
    await db.flush()
    await db.execute(
        _text("UPDATE cp_tenant_domains SET created_at = now() - interval '90 days' WHERE id = :i"),
        {"i": active.id},
    )
    with pytest.raises(AppError):
        await domain_svc.create_domain(db, tenant_id=victim.id, hostname=host3, actor=_actor(user))


@pytest.mark.asyncio
async def test_export_truncation_never_ships_partial_invoice(db, monkeypatch):
    """R138: build_export LEFT-JOINs invoices×lines and caps by EXPORT_MAX_ROWS
    on the JOINED rows — the boundary invoice was cut mid-lines, shipping a
    header with a partial line set whose sum diverged from total_minor. Every
    EMITTED invoice must be complete; the truncated flag signals the drop."""
    import json

    from app.controlplane.models.billing import Invoice, InvoiceLine
    from app.controlplane.services import provisioning as prov

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # Two invoices, two lines each. Cap at 3 joined rows: the window holds
    # inv1(line,line) + inv2(line) — inv2 is cut mid-lines.
    for _n in range(2):
        inv = Invoice(
            tenant_id=tenant.id,
            number=f"INV-{ULID()}",
            status="open",
            currency="USD",
            total_minor=300,
            amount_due_minor=300,
        )
        db.add(inv)
        await db.flush()
        for so in range(2):
            db.add(
                InvoiceLine(
                    invoice_id=inv.id,
                    line_type="usage",
                    description=f"l{so}",
                    amount_minor=150,
                    sort_order=so,
                )
            )
    await db.flush()
    monkeypatch.setattr(prov, "EXPORT_MAX_ROWS", 3)

    captured: dict = {}

    async def fake_s3():
        class FakeClient:
            async def head_bucket(self, **kw):
                return {}

            async def create_bucket(self, **kw):
                return {}

            async def put_object(self, **kw):
                captured["body"] = kw["Body"].decode()

        yield FakeClient()

    monkeypatch.setattr("app.core.storage.get_s3_client", fake_s3)
    export = await prov.build_export(db, tenant.id, actor=_actor(user))
    assert export.status == "completed"
    bundle = json.loads(captured["body"])
    assert "invoices" in bundle["truncated_collections"]
    # Every emitted invoice's lines must reconcile to its total — no partial.
    for inv in bundle["invoices"]:
        assert sum(line["amount_minor"] for line in inv["lines"]) == inv["total_minor"], (
            "a partial (boundary-cut) invoice was shipped"
        )


# ── R272: verifier/TLS adapter arcs + verify exhaustion ──


@pytest.mark.asyncio
async def test_verify_attempts_exhaustion_fails_domain(db):
    """R272: MAX_VERIFY_ATTEMPTS consecutive failures flip the domain to
    'failed' with a reason — and a failed domain may retry verification
    (status gate admits 'failed')."""
    import hashlib as _hl

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    domain, raw = await domain_svc.create_domain(
        db, tenant_id=tenant.id, hostname=f"x{str(ULID()).lower()[:8]}.example.com",
        actor=_actor(user))
    non_passing = "openskill-verify-nope"
    domain.verification_token_hash = _hl.sha256(non_passing.encode()).hexdigest()
    await db.flush()
    for _ in range(domain_svc.MAX_VERIFY_ATTEMPTS):
        with pytest.raises(AppError):
            await domain_svc.verify_domain(db, domain, non_passing, actor=_actor(user))
    assert domain.status == "failed"
    assert domain.verify_attempts == domain_svc.MAX_VERIFY_ATTEMPTS
    assert domain.failure_reason
    # 'failed' is still awaiting verification — the gate admits a retry
    with pytest.raises(AppError) as e:
        await domain_svc.verify_domain(db, domain, non_passing, actor=_actor(user))
    assert e.value.code == "DOMAIN_VERIFY_FAILED"          # not STATUS_CONFLICT


@pytest.mark.asyncio
async def test_dns_txt_verifier_lookup_logic(monkeypatch):
    """R272: DnsTxtVerifier's record-match logic, DNS patched out — multi-
    string TXT records join before compare, a matching record among noise
    verifies, NXDOMAIN/timeout and wrong records do not."""
    import dns.resolver

    from app.controlplane.services.domains import VERIFY_RECORD_PREFIX, DnsTxtVerifier

    class FakeAnswer:
        def __init__(self, *parts: bytes):
            self.strings = parts

    calls: list[str] = []

    def fake_resolve(name, rtype, lifetime=None):
        calls.append(name)
        assert rtype == "TXT"
        return [FakeAnswer(b"unrelated"), FakeAnswer(b"tok-", b"abc123")]

    monkeypatch.setattr(dns.resolver, "resolve", fake_resolve)
    v = DnsTxtVerifier()
    assert await v.verify("shop.example.com", "tok-abc123") is True   # joined match
    assert calls[0] == f"{VERIFY_RECORD_PREFIX}.shop.example.com"
    assert await v.verify("shop.example.com", "tok-other") is False   # no match

    def nxdomain(name, rtype, lifetime=None):
        raise dns.resolver.NXDOMAIN()

    monkeypatch.setattr(dns.resolver, "resolve", nxdomain)
    assert await v.verify("shop.example.com", "tok-abc123") is False  # fail closed


def test_tls_provisioner_switch_and_punycode_warn():
    """R272: the TLS provisioner switch and both adapters' contracts, plus
    check_reserved's punycode arc (warn, never reject — legit IDNs exist)."""
    import asyncio

    from app.config import settings as _settings
    from app.controlplane.services.domains import (
        MockTlsProvisioner,
        NullTlsProvisioner,
        check_reserved,
        get_tls_provisioner,
    )

    async def run():
        mock = MockTlsProvisioner()
        got = await mock.provision("a.example.com")
        assert got["tls_status"] == "active" and "a.example.com" in got["tls_ref"]
        assert await mock.status("a.example.com", got["tls_ref"]) == "active"
        null = NullTlsProvisioner()
        got2 = await null.provision("a.example.com")
        assert got2 == {"tls_status": "unmanaged", "tls_ref": None}
        assert await null.status("a.example.com", None) == "unmanaged"

    asyncio.run(run())

    from unittest.mock import patch

    with patch.object(_settings, "tls_provisioner", "mock"):
        assert isinstance(get_tls_provisioner(), MockTlsProvisioner)
    with patch.object(_settings, "tls_provisioner", "null"):
        assert isinstance(get_tls_provisioner(), NullTlsProvisioner)

    check_reserved("xn--48s290a.example.com")              # warns, must not raise


@pytest.mark.asyncio
async def test_provision_run_conflict_spoof_and_failed_retry(db):
    """R285: create_provision_run's guard arcs — R72[3] parameter-divergence
    409 on key reuse (incl. partner_id: reuse by a DIFFERENT partner is a
    cross-partner disclosure), the partner-scoped blueprint spoof (another
    partner's blueprint → uniform 404), an inactive blueprint → 404, and
    R101[H7]: replaying a FAILED run re-enqueues the retry instead of
    toasting a dead run as started."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    bp = TenantBlueprint(
        name=f"BP285 {ULID()}",
        config=provision_svc.validate_blueprint_config({"plan_key": "school"}),
        created_by=user.id)
    db.add(bp)
    await db.flush()

    key = f"r285-{ULID()}"
    run = await provision_svc.create_provision_run(
        db, blueprint_id=bp.id, name="Acme", slug=f"r285-{str(ULID()).lower()[:8]}",
        idempotency_key=key, partner_id=None, actor=_actor(user))

    # same key, different name → 409 (R72[3])
    with pytest.raises(AppError) as e:
        await provision_svc.create_provision_run(
            db, blueprint_id=bp.id, name="Evil", slug=run.requested_slug,
            idempotency_key=key, partner_id=None, actor=_actor(user))
    assert e.value.code == "PROVISION_CONFLICT" and e.value.status_code == 409
    # same key, different partner → 409 (cross-partner disclosure guard)
    with pytest.raises(AppError) as e:
        await provision_svc.create_provision_run(
            db, blueprint_id=bp.id, name="Acme", slug=run.requested_slug,
            idempotency_key=key, partner_id=str(ULID()), actor=_actor(user))
    assert e.value.code == "PROVISION_CONFLICT"

    # partner-scoped blueprint requested by another/no partner → uniform 404
    bp_partner = TenantBlueprint(
        name=f"BPp {ULID()}", partner_id=str(ULID()),
        config=provision_svc.validate_blueprint_config({"plan_key": "school"}),
        created_by=user.id)
    db.add(bp_partner)
    await db.flush()
    for pid in (None, str(ULID())):
        with pytest.raises(AppError) as e:
            await provision_svc.create_provision_run(
                db, blueprint_id=bp_partner.id, name="X",
                slug=f"x-{str(ULID()).lower()[:8]}",
                idempotency_key=f"r285b-{ULID()}", partner_id=pid,
                actor=_actor(user))
        assert e.value.code == "BLUEPRINT_INVALID" and e.value.status_code == 404

    # inactive blueprint → 404
    bp.is_active = False
    await db.flush()
    with pytest.raises(AppError) as e:
        await provision_svc.create_provision_run(
            db, blueprint_id=bp.id, name="Y", slug=f"y-{str(ULID()).lower()[:8]}",
            idempotency_key=f"r285c-{ULID()}", partner_id=None, actor=_actor(user))
    assert e.value.code == "BLUEPRINT_INVALID"
    bp.is_active = True
    await db.flush()

    # R101[H7]: replay of a FAILED run re-enqueues provision.run
    run.status = "failed"
    await db.flush()
    replay = await provision_svc.create_provision_run(
        db, blueprint_id=bp.id, name="Acme", slug=run.requested_slug,
        idempotency_key=key, partner_id=None, actor=_actor(user))
    assert replay.id == run.id
    retries = (
        (await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "provision.run",
                OutboxMessage.payload["run_id"].astext == run.id)))
        .scalars().all()
    )
    assert len(retries) >= 1                               # retry enqueued


@pytest.mark.asyncio
async def test_export_marks_ledger_and_license_truncation(db, monkeypatch):
    """R286: the remaining truncation markers — a capped credit_ledger and
    licenses section must SAY it was truncated (a silently-partial offboarding
    export is a legal exposure), and an unknown tenant is a 404."""
    import json

    from app.controlplane.models.marketplace import LicenseGrant
    from app.controlplane.services import credits as credit_svc
    from app.controlplane.services import provisioning as prov

    with pytest.raises(AppError) as e:
        await prov.build_export(db, str(ULID()), actor=_actor(await _mk_user(db)))
    assert e.value.code == "TENANT_NOT_FOUND" and e.value.status_code == 404

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    actor = _actor(user)
    for i in range(3):                                     # 3 ledger entries
        await credit_svc.top_up(
            db, tenant.id, "USD", 100 + i, actor=actor,
            idempotency_key=f"r286-{i}-{ULID()}")
    for _ in range(3):                                     # 3 license grants
        db.add(LicenseGrant(
            product_type="skill_pack", product_id=str(ULID()),
            tenant_id=tenant.id, org_id=None, scope="tenant",
            status="active", source="manual"))
    await db.flush()

    monkeypatch.setattr(prov, "EXPORT_MAX_ROWS", 2)
    captured: dict = {}

    async def fake_s3():
        class FakeClient:
            async def head_bucket(self, **kw):
                return {}

            async def create_bucket(self, **kw):
                return {}

            async def put_object(self, **kw):
                captured["body"] = kw["Body"].decode()

        yield FakeClient()

    monkeypatch.setattr("app.core.storage.get_s3_client", fake_s3)
    export = await prov.build_export(db, tenant.id, actor=actor)
    assert export.status == "completed"
    bundle = json.loads(captured["body"])
    assert "credit_ledger" in bundle["truncated_collections"]
    assert "licenses" in bundle["truncated_collections"]
    assert len(bundle["credit_ledger"]) == 2               # capped, marked
    assert len(bundle["licenses"]) == 2


@pytest.mark.asyncio
async def test_provision_run_resume_is_step_idempotent(db, monkeypatch):
    """R320: a provision run that fails MID-machine (here at
    apply_entitlement_overrides, after create_tenant + create_org) records
    status=failed with the completed steps' done-marks intact. Re-running
    RESUMES: it skips create_tenant/create_org (via _step_done) — it must NOT
    create a SECOND tenant or org — and completes. Guard-proven by forcing
    _step_done False (a second tenant then appears)."""
    from sqlalchemy import func as _f

    from app.controlplane.models.tenant import TenantAccount
    from app.controlplane.services import plans as _plans
    from app.controlplane.services import provisioning as prov

    user = await _mk_user(db)
    bp = TenantBlueprint(
        name=f"R320 {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {"plan_key": "school", "entitlement_overrides": {"max_organizations": 5}}),
        created_by=user.id)
    db.add(bp)
    await db.flush()
    slug = f"r320-{str(ULID()).lower()[:10]}"
    run = await provision_svc.create_provision_run(
        db, blueprint_id=bp.id, name="Resume Co", slug=slug,
        idempotency_key=f"r320-{ULID()}", partner_id=None, actor=_actor(user))

    # fail once at apply_entitlement_overrides
    real_set_override = _plans.set_override
    calls = {"n": 0}

    async def flaky(*a, **kw):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("transient override failure")
        return await real_set_override(*a, **kw)

    monkeypatch.setattr(prov, "set_override", flaky, raising=False)
    # prov imports set_override locally inside the step; patch the source module
    monkeypatch.setattr(_plans, "set_override", flaky)

    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "failed"
    assert provision_svc._step_done(run, "create_tenant")
    assert run.tenant_id is not None
    first_tenant_id = run.tenant_id

    # resume → completes, no second tenant/org for this slug
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed"
    assert run.tenant_id == first_tenant_id          # SAME tenant, not re-created
    n_tenants = (
        await db.execute(
            select(_f.count(TenantAccount.id)).where(TenantAccount.slug == slug))
    ).scalar_one()
    assert n_tenants == 1                             # resume did not double-create
    from app.models.organization import Organization as _Org355

    n_orgs = (
        await db.execute(
            select(_f.count(_Org355.id)).where(_Org355.tenant_id == first_tenant_id))
    ).scalar_one()
    assert n_orgs == 1                                # …nor a second org (R355)


@pytest.mark.asyncio
async def test_concurrent_first_branding_upserts_both_succeed():
    """R324: two concurrent FIRST-EVER branding upserts both pass the
    existence SELECT (neither committed) — the loser's flush hit the
    tenant_id unique index as an unhandled IntegrityError 500 (the R68[4]/
    R113[L10] check-then-insert class). The SAVEPOINT-isolated insert must
    adopt the winner's row: both PUTs succeed, exactly ONE row exists."""
    import asyncio

    from app.controlplane.models.branding import TenantBranding

    async with AsyncSessionLocal() as setup:
        user = await _mk_user(setup)
        tenant = await _mk_tenant(setup, user)
        await setup.commit()
        tid, actor = tenant.id, _actor(user)

    async def winner():
        async with AsyncSessionLocal() as s:
            b = await branding_svc.upsert_branding(
                s, tid, {"login_tagline": "winner"}, actor=actor)
            await asyncio.sleep(0.4)  # hold the uncommitted insert
            await s.commit()
            return b.id

    async def loser():
        await asyncio.sleep(0.15)  # start while winner's insert is uncommitted
        async with AsyncSessionLocal() as s:
            b = await branding_svc.upsert_branding(
                s, tid, {"login_tagline": "loser"}, actor=actor)
            await s.commit()
            return b.id

    id_a, id_b = await asyncio.gather(winner(), loser())
    assert id_a == id_b, "loser must adopt the winner's row, not 500"
    async with AsyncSessionLocal() as s:
        rows = (
            await s.execute(
                select(TenantBranding).where(TenantBranding.tenant_id == tid))
        ).scalars().all()
        assert len(rows) == 1
        # cleanup (module uses shared DB across tests)
        await s.delete(rows[0])
        await s.commit()


@pytest.mark.asyncio
async def test_branding_explicit_null_clears_to_empty_not_jsonb_null(db):
    """R330: PUT branding with an explicit null (the schema advertises
    `dict|None`/`list|None`) was validated as empty but stored RAW — JSONB
    none_as_null=False persisted a jsonb null, and site-context served it
    verbatim: the white-label login shell does `branding.legal_links.length`,
    so one "clear my links" PUT crashed the tenant's entire login page. Null
    means CLEAR: stored as {} / [], and the read paths coalesce pre-fix null
    rows."""
    from app.controlplane.models.branding import TenantBranding

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    b = await branding_svc.upsert_branding(
        db, tenant.id,
        {"theme_tokens": {"primary": "#112233"},
         "legal_links": [{"label": "ToS", "url": "https://x.example/tos"}]},
        actor=_actor(user))
    assert b.theme_tokens and b.legal_links
    # explicit null clears BOTH to empty containers, never jsonb null
    b = await branding_svc.upsert_branding(
        db, tenant.id, {"theme_tokens": None, "legal_links": None},
        actor=_actor(user))
    assert b.theme_tokens == {}, "explicit null must clear to {}, not jsonb null"
    assert b.legal_links == [], "explicit null must clear to [], not jsonb null"

    # read-side coalesce: simulate a PRE-FIX row holding jsonb null
    from sqlalchemy import update as sa_update

    from app.controlplane.models.branding import TenantDomain

    await db.execute(
        sa_update(TenantBranding)
        .where(TenantBranding.tenant_id == tenant.id)
        .values(theme_tokens=None, legal_links=None))
    await db.flush()
    domain = TenantDomain(
        tenant_id=tenant.id, hostname=f"r330-{str(ULID()).lower()[:8]}.example.com",
        status="active", verification_token_hash="x", created_by=user.id)
    db.add(domain)
    await db.flush()
    ctx = await domain_svc.resolve_site_context(db, domain.hostname)
    assert ctx["branding"]["theme_tokens"] == {}
    assert ctx["branding"]["legal_links"] == []


@pytest.mark.asyncio
async def test_provision_gates_versions_and_resume_org_reuse(db, monkeypatch):
    """R355 (mutation survivors): (1) replaying a COMPLETED run never
    re-enqueues (only FAILED does — R101[H7]'s other side); (2) a partner may
    use a GLOBAL blueprint (the Or-mutant 404s every global blueprint for
    partner callers); (3) executing a nonexistent run id is a silent no-op,
    never a crash; (4) pack version "latest" installs as None while a pinned
    version passes through VERBATIM — for BOTH the skill and workflow loops;
    (5) the workflow loop tolerates ALREADY_INSTALLED on resume like the
    skill loop; (6) a column-max (100-char) requested slug lands within the 100-char org
    slug column; (7) resume reuses the already-created ORG (exactly one).
    Documented-equivalent mutants: the [:100]/[:101] slug truncations
    (identity — the API caps slugs at 100), the collision-retry internals
    (unique index + ULID randomness), the entitlement-overrides depth limit
    (shadowed by per-key validation into the same BLUEPRINT_INVALID),
    error-list/audit truncation cosmetics, and the pack-unavailable 422
    statuses (contained by the run's failure handler — never cross the API)."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.models.organization import Organization
    from app.services import installation as install_mod
    from app.services import workflow_installation as winstall_mod

    user = await _mk_user(db)
    partner_user = await _mk_user(db)
    from app.controlplane.models.partner import Partner

    partner = Partner(name=f"P {ULID()}", slug=f"p-{str(ULID()).lower()[:10]}",
                      currency="USD", status="active", partner_type="reseller",
                      created_by=partner_user.id)
    db.add(partner)
    await db.flush()

    installed: list = []

    async def fake_skill_install(self, org_id, pack_id, version, installed_by):
        if pack_id.endswith("AAA"):
            raise AppError("ALREADY_INSTALLED", "dup", 409)
        installed.append(("skill", pack_id, version, org_id))

    async def fake_wf_install(self, org_id, pack_id, version, installed_by):
        if pack_id.endswith("AAA"):
            raise AppError("ALREADY_INSTALLED", "dup", 409)
        installed.append(("workflow", pack_id, version))

    monkeypatch.setattr(install_mod.InstallationService, "install_pack", fake_skill_install)
    monkeypatch.setattr(winstall_mod.WorkflowInstallationService, "install", fake_wf_install)

    # (2)+(4)+(5): GLOBAL blueprint used BY A PARTNER, latest + pinned +
    # already-installed refs in both loops
    bp = TenantBlueprint(
        name=f"R355 {ULID()}",
        config=provision_svc.validate_blueprint_config({
            "skill_packs": [
                {"pack_id": "01JPACKAAAAAAAAAAAAAAAAAAA"},                    # dup-tolerated
                {"pack_id": "01JPACKBBBBBBBBBBBBBBBBBBB", "version": "1.2.3"},
                {"pack_id": "01JPACKCCCCCCCCCCCCCCCCCCC", "version": "latest"},
            ],
            "workflow_packs": [
                {"pack_id": "01JWPACKAAAAAAAAAAAAAAAAAA"[:26].ljust(26, "A")},  # dup-tolerated
                {"pack_id": "01JWPACKBBBBBBBBBBBBBBBBBB"[:26].ljust(26, "B"), "version": "2.0.0"},
            ],
        }),
        created_by=user.id)
    db.add(bp)
    await db.flush()

    long_slug = ("r355-" + "x" * 100)[:100]              # (6) column-max slug
    run = await provision_svc.create_provision_run(
        db, blueprint_id=bp.id, name="R355 Co", slug=long_slug,
        idempotency_key=f"r355-{ULID()}",
        partner_id=partner.id,                            # partner ON a global bp
        actor=_actor(partner_user))
    await provision_svc.execute_provision_run(db, run.id)
    await db.refresh(run)
    assert run.status == "completed", run.steps

    # (4): version pass-through semantics
    by_pack = {e[1]: e[2] for e in installed if e[0] == "skill"}
    assert by_pack["01JPACKBBBBBBBBBBBBBBBBBBB"] == "1.2.3"
    assert by_pack["01JPACKCCCCCCCCCCCCCCCCCCC"] is None            # latest → None
    assert ("workflow", "01JWPACKBBBBBBBBBBBBBBBBBB"[:26].ljust(26, "B"), "2.0.0") in installed

    # (6)+(7): org slug bounded; exactly one org for this run
    orgs = (
        await db.execute(select(Organization).where(
            Organization.tenant_id == run.tenant_id))
    ).scalars().all()
    assert len(orgs) == 1 and len(orgs[0].slug) <= 100

    # (1): replaying the COMPLETED run returns it WITHOUT re-enqueueing
    pending_before = (
        await db.execute(select(OutboxMessage).where(
            OutboxMessage.topic == "provision.run",
            OutboxMessage.status == "pending"))
    ).scalars().all()
    replay = await provision_svc.create_provision_run(
        db, blueprint_id=bp.id, name="R355 Co", slug=long_slug,
        idempotency_key=run.idempotency_key, partner_id=partner.id,
        actor=_actor(partner_user))
    assert replay.id == run.id
    pending_after = (
        await db.execute(select(OutboxMessage).where(
            OutboxMessage.topic == "provision.run",
            OutboxMessage.status == "pending"))
    ).scalars().all()
    assert len(pending_after) == len(pending_before)     # completed: no enqueue

    # (3): nonexistent run id → silent no-op
    await provision_svc.execute_provision_run(db, str(ULID()))

    # the NON-collision path uses the requested slug VERBATIM
    assert orgs[0].slug == long_slug

    # config-validation boundaries: feature_settings nests to depth 4, one
    # deeper is a 422; a malformed config is a 422; a partner-blueprint spoof
    # is a uniform 404 (statuses pinned)
    deep_ok = {"a": {"b": {"c": "d"}}}                    # 4 levels incl. root
    provision_svc.validate_blueprint_config({"feature_settings": deep_ok})
    with pytest.raises(AppError) as e_deep:
        provision_svc.validate_blueprint_config(
            {"feature_settings": {"a": {"b": {"c": {"d": "e"}}}}})
    assert e_deep.value.status_code == 422
    with pytest.raises(AppError) as e_bad:
        provision_svc.validate_blueprint_config({"skill_packs": [{"nope": 1}]})
    assert e_bad.value.status_code == 422
    other_partner = Partner(name=f"P2 {ULID()}", slug=f"p2-{str(ULID()).lower()[:10]}",
                            currency="USD", status="active", partner_type="reseller",
                            created_by=partner_user.id)
    db.add(other_partner)
    await db.flush()
    scoped_bp = TenantBlueprint(
        name=f"R355s {ULID()}", partner_id=partner.id,
        config=provision_svc.validate_blueprint_config({}), created_by=user.id)
    db.add(scoped_bp)
    await db.flush()
    with pytest.raises(AppError) as e_404:
        await provision_svc.create_provision_run(
            db, blueprint_id=scoped_bp.id, name="Spoof", slug=f"sp-{str(ULID()).lower()[:8]}",
            idempotency_key=f"sp-{ULID()}", partner_id=other_partner.id,
            actor=_actor(partner_user))
    assert e_404.value.status_code == 404

    # a pack that raises a non-dup AppError fails the run with a 422-coded
    # BLUEPRINT_PACK_UNAVAILABLE detail (status pinned via the raise class)
    async def corrupt_install(self, org_id, pack_id, version, installed_by):
        raise AppError("PACK_CORRUPT", "checksum", 422)

    monkeypatch.setattr(install_mod.InstallationService, "install_pack", corrupt_install)
    bp2 = TenantBlueprint(
        name=f"R355c {ULID()}",
        config=provision_svc.validate_blueprint_config(
            {"skill_packs": [{"pack_id": "01JPACKDDDDDDDDDDDDDDDDDDD"}]}),
        created_by=user.id)
    db.add(bp2)
    await db.flush()
    run2 = await provision_svc.create_provision_run(
        db, blueprint_id=bp2.id, name="Corrupt", slug=f"co-{str(ULID()).lower()[:8]}",
        idempotency_key=f"co-{ULID()}", partner_id=None, actor=_actor(user))
    await provision_svc.execute_provision_run(db, run2.id)
    await db.refresh(run2)
    assert run2.status == "failed" and "not installable" in (run2.error or "")

    # heal the pack step and RESUME with the real step ledger intact: the
    # install must run against the RECOVERED org id (create_org step payload),
    # never a None from a flipped step matcher
    monkeypatch.setattr(install_mod.InstallationService, "install_pack",
                        fake_skill_install)
    installed.clear()
    await provision_svc.execute_provision_run(db, run2.id)
    await db.refresh(run2)
    assert run2.status == "completed"
    run2_org = next(st.get("org_id") for st in run2.steps
                    if st.get("step") == "create_org" and st.get("status") == "done")
    assert installed and installed[0][3] == run2_org and run2_org is not None

    # R84[M5]: a FAILED snapshot_config residue (no 'config' key) plus a done
    # one — resume must match ONLY the done+config entry, never KeyError-wedge
    run3 = await provision_svc.create_provision_run(
        db, blueprint_id=bp2.id, name="Craft", slug=f"cr-{str(ULID()).lower()[:8]}",
        idempotency_key=f"cr-{ULID()}", partner_id=None, actor=_actor(user))
    run3.status = "failed"
    run3.steps = [
        {"step": "snapshot_config", "status": "failed"},
        {"step": "snapshot_config", "status": "done",
         "config": provision_svc.validate_blueprint_config({})},
    ]
    await db.flush()
    await provision_svc.execute_provision_run(db, run3.id)   # no KeyError wedge
    await db.refresh(run3)
    assert run3.status == "completed"

    # inactive blueprint → 404 with status
    bp2.is_active = False
    await db.flush()
    with pytest.raises(AppError) as e_inact:
        await provision_svc.create_provision_run(
            db, blueprint_id=bp2.id, name="Inact", slug=f"in-{str(ULID()).lower()[:8]}",
            idempotency_key=f"in-{ULID()}", partner_id=None, actor=_actor(user))
    assert e_inact.value.status_code == 404


@pytest.mark.asyncio
async def test_fresh_pending_domain_claim_not_evictable(db):
    """R369 (the security-review-flagged eviction boundary): a FRESH pending
    claim (inside the 7-day grace) is NOT evictable by another tenant — the
    flipped/widened mutants let any tenant squat-evict a competitor's claim
    minutes after it was made. Both takeover raises carry 409."""
    from datetime import UTC, datetime, timedelta

    user = await _mk_user(db)
    t1 = await _mk_tenant(db, user)
    t2 = await _mk_tenant(db, user)
    host = f"fresh-{str(ULID()).lower()[:8]}.example.com"
    d1, _ = await domain_svc.create_domain(db, tenant_id=t1.id, hostname=host, actor=_actor(user))
    assert d1.status == "pending_verification"

    # 6 days old: still inside the grace — the second tenant gets a 409
    d1.created_at = datetime.now(UTC) - timedelta(days=6)
    await db.flush()
    with pytest.raises(AppError) as e_taken:
        await domain_svc.create_domain(db, tenant_id=t2.id, hostname=host, actor=_actor(user))
    assert e_taken.value.code == "DOMAIN_TAKEN" and e_taken.value.status_code == 409

    # 7.5 days old: past the SEVEN-day window — evictable (7.5 sits between
    # the real 7d cutoff and the 8d-mutant's, so the widened window 409s it)
    d1.created_at = datetime.now(UTC) - timedelta(days=7, hours=12)
    await db.flush()
    d2, _ = await domain_svc.create_domain(db, tenant_id=t2.id, hostname=host, actor=_actor(user))
    assert d2.tenant_id == t2.id


class _Req383:
    class _State:
        request_id = "r383"
    state = _State()


@pytest.mark.asyncio
async def test_whitelabel_api_handlers_cross_tenant_404(db):
    """R383: the whitelabel handler layer — the _tenant_domain ownership gate
    404s a FOREIGN tenant's domain id uniformly on verify/activate/disable/
    delete (no existence oracle), and update_branding round-trips through the
    handler with the tenant actor."""
    from app.controlplane.api.whitelabel import (
        BrandingRequest,
        delete_domain,
        disable_domain,
        update_branding,
    )
    from app.controlplane.api.whitelabel import (
        activate_domain as activate_ep,
    )
    from app.controlplane.api.whitelabel import (
        verify_domain as verify_ep,
    )
    from app.controlplane.services.plans import set_override

    user = await _mk_user(db)
    t1 = await _mk_tenant(db, user)
    t2 = await _mk_tenant(db, user)
    req = _Req383()
    await set_override(db, t1.id, "custom_domain", value=True,
                       enforcement="hard", expires_at=None,
                       reason="r383", actor=_actor(user))
    await set_override(db, t1.id, "white_label", value=True,
                       enforcement="hard", expires_at=None,
                       reason="r383", actor=_actor(user))
    from app.controlplane.services.entitlements import invalidate_cache
    await invalidate_cache(t1.id)

    # a domain owned by TENANT 2
    foreign, _ = await domain_svc.create_domain(
        db, tenant_id=t2.id, hostname=f"f383-{str(ULID()).lower()[:8]}.example.com",
        actor=_actor(user))

    from app.controlplane.api.whitelabel import VerifyDomainRequest

    with pytest.raises(AppError) as e_v:
        await verify_ep(t1.id, foreign.id,
                        VerifyDomainRequest(token="tok-r383-aaaa"), req,
                        user=user, db=db)
    assert e_v.value.status_code == 404 and e_v.value.code == "DOMAIN_INVALID"
    for ep in (activate_ep, disable_domain, delete_domain):
        with pytest.raises(AppError) as e404:
            await ep(t1.id, foreign.id, req, user=user, db=db)
        assert e404.value.status_code == 404, ep.__name__
        assert e404.value.code == "DOMAIN_INVALID"

    # branding handler round-trip (tenant actor threading + response shape)
    resp = await update_branding(
        t1.id, BrandingRequest(login_tagline="Hello R383"), req,
        user=user, db=db)
    assert resp.data["login_tagline"] == "Hello R383"
    assert resp.data["theme_tokens"] == {}


async def test_export_sections_are_tenant_scoped(db, monkeypatch):
    """R516 mutation kills: the provisioning sweep left `tenant_id ==` -> `!=`
    ALIVE on six export sections (payments, credit notes, credit ledger,
    licenses, usage, domains) — i.e. nothing asserted that another tenant's
    rows are EXCLUDED, nor even that the exporting tenant's own rows appear.
    Seed two tenants with distinguishable rows in every section and assert
    both directions; also pin the cancelled-subscription exclusion (L529).
    """
    import json as _json
    from datetime import UTC, datetime, timedelta
    from decimal import Decimal as _Dec

    from app.controlplane.models.billing import Invoice, PaymentRecord, Subscription
    from app.controlplane.models.branding import TenantDomain
    from app.controlplane.models.credit import CreditLedgerEntry
    from app.controlplane.models.marketplace import LicenseGrant
    from app.controlplane.models.usage import UsageEvent

    user = await _mk_user(db)
    ten_a = await _mk_tenant(db, user)
    ten_b = await _mk_tenant(db, user)

    async def seed(tenant_id: str, tag: str) -> dict:
        inv_total = 111001 if tag == "alpha" else 112002  # unique invoice markers
        inv = Invoice(tenant_id=tenant_id, currency="USD", status="open",
                      subtotal_minor=inv_total, total_minor=inv_total,
                      amount_due_minor=inv_total, finalized_at=datetime.now(UTC))
        db.add(inv)
        await db.flush()
        pay = PaymentRecord(tenant_id=tenant_id, invoice_id=inv.id, amount_minor=1000, currency="USD",
                            method="manual", status="succeeded",
                            received_at=datetime.now(UTC))
        amount = 771001 if tag == "alpha" else 772002  # unique ledger markers
        ledger = CreditLedgerEntry(tenant_id=tenant_id, currency="USD",
                                   entry_type="manual_adjustment", amount_minor=amount,
                                   balance_after_minor=amount, reason=f"seed-{tag}")
        grant = LicenseGrant(tenant_id=tenant_id, product_type="skill_pack",
                             product_id=str(ULID()), scope="tenant", status="active",
                             source="manual_grant")
        # content_license is rare in the shared dev DB; the EXACT per-tenant
        # quantity is the marker — a tenant_id != mutant aggregates everyone
        # else's rows and can no longer produce exactly this sum.
        qty = 31 if tag == "alpha" else 37
        usage = UsageEvent(tenant_id=tenant_id, org_id=str(ULID()),
                           usage_type="content_license", quantity=_Dec(qty),
                           unit="licenses", occurred_at=datetime.now(UTC),
                           source="manual", metadata_={})
        dom = TenantDomain(tenant_id=tenant_id, verification_token_hash="x" * 64,
                           hostname=f"exp-{tag}-{str(ULID()).lower()[:8]}.example.com")
        db.add_all([pay, ledger, grant, usage, dom])
        await db.flush()
        return {"invoice": inv.id, "payment": pay.id, "grant": grant.product_id,
                "domain": dom.hostname, "ledger": str(amount), "inv_total": inv_total}
    a = await seed(ten_a.id, "alpha")
    b = await seed(ten_b.id, "bravo")
    # a CANCELLED subscription for tenant A must be excluded (L529)
    from app.controlplane.models.plan import PlanVersion as _Pv

    pv_id = (
        await db.execute(select(_Pv.id).limit(1))
    ).scalar_one_or_none()
    assert pv_id is not None, "dev DB has no plan versions seeded"
    db.add(Subscription(tenant_id=ten_a.id, plan_version_id=pv_id,
                        status="cancelled", currency="USD", interval="month",
                        current_period_start=datetime.now(UTC),
                        current_period_end=datetime.now(UTC) + timedelta(days=30)))
    await db.flush()

    captured: dict = {}

    async def fake_s3():
        class FakeClient:
            async def head_bucket(self, **kw):
                return {}

            async def create_bucket(self, **kw):
                return {}

            async def put_object(self, **kw):
                captured["body"] = kw["Body"].decode()

        yield FakeClient()

    monkeypatch.setattr("app.core.storage.get_s3_client", fake_s3)
    export = await provision_svc.build_export(db, ten_a.id, actor=_actor(user))
    assert export.status == "completed"
    body = captured["body"]
    bundle = _json.loads(body)

    # own rows present in every section
    assert a["payment"] in body
    assert a["ledger"] in body  # ledger amount marker
    assert a["grant"] in body  # license
    assert a["domain"] in body
    lic_rows = [u for u in bundle["usage_monthly"] if u["usage_type"] == "content_license"]
    assert lic_rows and all(float(u["quantity"]) == 31.0 for u in lic_rows), lic_rows
    assert any(i["total_minor"] == a["inv_total"] for i in bundle["invoices"])
    # the OTHER tenant's rows are excluded from every section (§35 red line)
    for marker in (b["payment"], b["ledger"], b["grant"], b["domain"], str(b["inv_total"])):
        assert marker not in body, marker
    # cancelled subscription excluded
    assert bundle["subscription"] is None
