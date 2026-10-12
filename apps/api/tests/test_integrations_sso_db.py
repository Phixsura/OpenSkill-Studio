"""P3 SSO DB tests — org domains, identity resolution takeover matrix, OIDC
callback against a faked IdP (signed id_token), enforce-SSO + break-glass."""

import json
import time
import uuid
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt as pyjwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.models import (
    ExternalIdentityLink,
    IdentityMatchQueue,
    IntegrationEvent,
    OrgDomain,
    SsoConnection,
)
from app.integrations.services.domains import OrgDomainService
from app.integrations.services.identity import IdentityService, VerifiedExternalIdentity
from app.integrations.services.sso_admin import SsoAdminService
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, email=None):
    u = User(
        email=email or f"sso-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Sso",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, user):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await db.flush()
    return org


async def _verified_domain(db, org, domain):
    row = OrgDomain(
        org_id=org.id,
        domain=domain,
        status="verified",
        verification_token="t",
        verified_at=datetime.now(UTC),
    )
    db.add(row)
    await db.flush()
    return row


# ── domains ──


@pytest.mark.asyncio
async def test_domain_freemail_and_normalization_rules(db):
    owner = await _user(db)
    org = await _org(db, owner)
    svc = OrgDomainService(db)
    with pytest.raises(AppError) as e:
        await svc.claim(org.id, "gmail.com")
    assert e.value.code == "DOMAIN_NOT_ELIGIBLE"
    row = await svc.claim(org.id, "HTTPS://Acme-School.EDU./x")
    assert row.domain == "acme-school.edu"
    assert row.verification_token.startswith("osks-verify-")
    # idempotent re-claim
    again = await svc.claim(org.id, "acme-school.edu")
    assert again.id == row.id


@pytest.mark.asyncio
async def test_domain_verified_exclusivity(db):
    owner1 = await _user(db)
    org1 = await _org(db, owner1)
    await _verified_domain(db, org1, "taken.example.edu")
    owner2 = await _user(db)
    org2 = await _org(db, owner2)
    with pytest.raises(AppError) as e:
        await OrgDomainService(db).claim(org2.id, "taken.example.edu")
    assert e.value.code == "DOMAIN_ALREADY_VERIFIED"


@pytest.mark.asyncio
async def test_domain_verify_uses_verifier(db, monkeypatch):
    owner = await _user(db)
    org = await _org(db, owner)
    svc = OrgDomainService(db)
    row = await svc.claim(org.id, "verify-me.example.edu")

    class Nope:
        async def verify(self, h, t):
            return False

    class Yep:
        async def verify(self, h, t):
            return True

    import app.integrations.services.domains as mod

    monkeypatch.setattr(mod, "get_verifier", lambda: Nope())
    with pytest.raises(AppError) as e:
        await svc.verify(org.id, row.id)
    assert e.value.code == "DOMAIN_VERIFY_FAILED"
    monkeypatch.setattr(mod, "get_verifier", lambda: Yep())
    ok = await svc.verify(org.id, row.id)
    assert ok.status == "verified"


# ── identity resolution matrix ──


def _ident(org, conn_ref="01CONN", subject="sub-1", email=None, verified=True, **kw):
    return VerifiedExternalIdentity(
        org_id=org.id,
        source="sso",
        connection_ref=conn_ref,
        subject=subject,
        email=email,
        email_verified=verified,
        **kw,
    )


@pytest.mark.asyncio
async def test_resolution_unverified_email_queues(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "acme.edu")
    svc = IdentityService(db)
    with pytest.raises(AppError) as e:
        await svc.resolve(_ident(org, email="a@acme.edu", verified=False))
    assert e.value.code == "IDENTITY_AMBIGUOUS"
    # Lesson 8/24: never assert on the LAST row of a global, unordered
    # select against the shared dev DB — key on our own org instead.
    q = (
        (await db.execute(select(IdentityMatchQueue).where(IdentityMatchQueue.org_id == org.id)))
        .scalars()
        .all()
    )
    assert q and q[-1].reason == "email_unverified_or_foreign_domain"
    # Retried login does not duplicate the pending row.
    with pytest.raises(AppError):
        await svc.resolve(_ident(org, email="a@acme.edu", verified=False))
    q2 = (
        (await db.execute(select(IdentityMatchQueue).where(IdentityMatchQueue.subject == "sub-1")))
        .scalars()
        .all()
    )
    assert len(q2) == 1


@pytest.mark.asyncio
async def test_resolution_foreign_domain_never_matches(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "acme.edu")
    member = await _user(db, email=f"victim-{uuid.uuid4().hex[:8]}@evil.com")
    db.add(
        OrgMember(
            org_id=org.id, user_id=member.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    await db.flush()
    with pytest.raises(AppError) as e:
        await IdentityService(db).resolve(_ident(org, email=member.email, verified=True))
    assert e.value.code == "IDENTITY_AMBIGUOUS"  # evil.com is not org-verified


@pytest.mark.asyncio
async def test_resolution_links_then_sticks_to_subject(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "acme.edu")
    member = await _user(db, email=f"alice-{uuid.uuid4().hex[:6]}@acme.edu")
    db.add(
        OrgMember(
            org_id=org.id, user_id=member.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    await db.flush()
    svc = IdentityService(db)
    r1 = await svc.resolve(_ident(org, email=member.email))
    assert r1.user.id == member.id and not r1.jit_created
    # IdP email change: SAME subject still resolves to the same user
    # (email is never the re-resolution key).
    r2 = await svc.resolve(_ident(org, email="renamed@acme.edu"))
    assert r2.user.id == member.id
    # Same VERIFIED email under a NEW subject links to the same user (ADR §9
    # step 2 — IdP migrations re-issue subjects); both links stay active.
    r3 = await svc.resolve(_ident(org, subject="sub-OTHER", email=member.email))
    assert r3.user.id == member.id
    links = (
        (
            await db.execute(
                select(ExternalIdentityLink).where(
                    ExternalIdentityLink.user_id == member.id,
                    ExternalIdentityLink.revoked_at.is_(None),
                )
            )
        )
        .scalars()
        .all()
    )
    assert {link.subject for link in links} == {"sub-1", "sub-OTHER"}


@pytest.mark.asyncio
async def test_resolution_jit_creates_and_respects_role_ceiling(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "acme.edu")
    svc = IdentityService(db)
    fresh = f"new-{uuid.uuid4().hex[:8]}@acme.edu"
    # no JIT -> refused
    with pytest.raises(AppError) as e:
        await svc.resolve(_ident(org, subject="s-j", email=fresh))
    assert e.value.code == "SSO_NO_ACCOUNT"
    # JIT student OK
    r = await svc.resolve(_ident(org, subject="s-j2", email=fresh), allow_jit=True)
    assert r.jit_created and r.user.email == fresh
    member = (
        await db.execute(
            select(OrgMember).where(OrgMember.org_id == org.id, OrgMember.user_id == r.user.id)
        )
    ).scalar_one()
    assert member.role == OrgRole.STUDENT and member.is_break_glass is False
    # owner role can never be JIT-minted
    with pytest.raises(AppError) as e2:
        await svc.resolve(
            _ident(org, subject="s-j3", email=f"x-{uuid.uuid4().hex[:6]}@acme.edu"),
            allow_jit=True,
            jit_role="owner",
        )
    assert e2.value.code == "SSO_JIT_ROLE_INVALID"


@pytest.mark.asyncio
async def test_same_subject_two_orgs_two_links(db):
    owner1 = await _user(db)
    org1 = await _org(db, owner1)
    await _verified_domain(db, org1, "one.example.edu")
    owner2 = await _user(db)
    org2 = await _org(db, owner2)
    await _verified_domain(db, org2, "two.example.edu")
    svc = IdentityService(db)
    r1 = await svc.resolve(
        _ident(
            org1,
            conn_ref="01CONNA",
            subject="dup",
            email=f"a-{uuid.uuid4().hex[:5]}@one.example.edu",
        ),
        allow_jit=True,
    )
    r2 = await svc.resolve(
        _ident(
            org2,
            conn_ref="01CONNB",
            subject="dup",
            email=f"b-{uuid.uuid4().hex[:5]}@two.example.edu",
        ),
        allow_jit=True,
    )
    assert r1.user.id != r2.user.id
    links = (
        (
            await db.execute(
                select(ExternalIdentityLink).where(ExternalIdentityLink.subject == "dup")
            )
        )
        .scalars()
        .all()
    )
    assert len(links) == 2
    assert {link.org_id for link in links} == {org1.id, org2.id}


# ── OIDC flow against a faked IdP ──

ISSUER = "https://idp.example.com"
_RSA = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIV = _RSA.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
_PUB_JWK = json.loads(pyjwt.algorithms.RSAAlgorithm.to_jwk(_RSA.public_key()))
_PUB_JWK.update({"kid": "k1", "alg": "RS256", "use": "sig"})


def _discovery_doc():
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "jwks_uri": f"{ISSUER}/jwks",
    }


class FakeIdp:
    """Routes EgressClient calls to a scripted IdP."""

    def __init__(self, id_token_factory):
        self.id_token_factory = id_token_factory
        self.calls = []

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        self.calls.append(url)
        path = urlsplit(url).path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery_doc(), request=httpx.Request(method, url))
        if path.endswith("/jwks"):
            return httpx.Response(
                200, json={"keys": [_PUB_JWK]}, request=httpx.Request(method, url)
            )
        if path.endswith("/token"):
            form = parse_qs((content or b"").decode())
            return httpx.Response(
                200,
                json={"id_token": self.id_token_factory(form)},
                request=httpx.Request(method, url),
            )
        return httpx.Response(404, request=httpx.Request(method, url))


def _mint_id_token(*, sub, email, nonce, aud, email_verified=True, **over):
    claims = {
        "iss": ISSUER,
        "aud": aud,
        "sub": sub,
        "email": email,
        "email_verified": email_verified,
        "name": "OIDC User",
        "nonce": nonce,
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
    }
    claims.update(over)
    return pyjwt.encode(claims, _PRIV, algorithm="RS256", headers={"kid": "k1"})


async def _oidc_setup(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "oidc.example.edu")
    conn = await SsoAdminService(db).create(
        org.id,
        protocol="oidc",
        oidc_issuer=ISSUER,
        oidc_client_id="client-1",
        oidc_client_secret="s3cret",
        allow_jit=True,
    )
    conn.status = "active"
    await db.flush()
    return org, conn


@pytest.mark.asyncio
async def test_oidc_full_flow_jit_login(db, monkeypatch):
    import app.integrations.services.sso_oidc as mod

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)
    email = f"oidc-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    def factory(form):
        state_row_nonce = factory.nonce
        return _mint_id_token(sub="oidc-sub-1", email=email, nonce=state_row_nonce, aud="client-1")

    fake = FakeIdp(factory)
    svc.egress = fake

    url = await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.test/cb")
    qs = parse_qs(urlsplit(url).query)
    state_val = qs["state"][0]
    factory.nonce = qs["nonce"][0]
    assert url.startswith(f"{ISSUER}/authorize?")

    conn2, result, _rt = await svc.handle_callback(
        state_value=state_val, code="authcode", redirect_uri="https://app.test/cb"
    )
    assert conn2.id == conn.id
    assert result.jit_created and result.user.email == email
    # State is single-use.
    with pytest.raises(AppError):
        await svc.handle_callback(
            state_value=state_val, code="authcode", redirect_uri="https://app.test/cb"
        )


@pytest.mark.asyncio
async def test_oidc_rejects_bad_nonce_aud_expiry(db, monkeypatch):
    import app.integrations.services.sso_oidc as mod

    org, conn = await _oidc_setup(db)
    email = f"bad-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    async def run_with(mint_kwargs):
        svc = mod.OidcService(db)

        def factory(form):
            return _mint_id_token(
                sub="s",
                email=email,
                aud=mint_kwargs.pop("aud", "client-1"),
                nonce=mint_kwargs.pop("nonce", factory.real_nonce),
                **mint_kwargs,
            )

        svc.egress = FakeIdp(factory)
        url = await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.test/cb")
        qs = parse_qs(urlsplit(url).query)
        factory.real_nonce = qs["nonce"][0]
        with pytest.raises(AppError) as e:
            await svc.handle_callback(
                state_value=qs["state"][0], code="c", redirect_uri="https://app.test/cb"
            )
        assert e.value.code == "SSO_ASSERTION_INVALID"

    await run_with({"nonce": "evil-echoed-nonce"})
    await run_with({"aud": "other-client"})
    await run_with({"exp": int(time.time()) - 3600})
    await run_with({"iss": "https://rogue.example.com"})


# ── enforce-SSO gate + break-glass ──


@pytest.mark.asyncio
async def test_enforce_sso_blocks_password_login_break_glass_passes(db):
    from app.services.auth import AuthService

    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "locked.example.edu")
    email = f"emp-{uuid.uuid4().hex[:8]}@locked.example.edu"
    emp = await _user(db, email=email)
    member = OrgMember(
        org_id=org.id, user_id=emp.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
    )
    db.add(member)
    conn = SsoConnection(
        org_id=org.id,
        protocol="oidc",
        status="active",
        oidc_issuer=ISSUER,
        oidc_client_id="c",
        enforce_sso=True,
    )
    db.add(conn)
    await db.flush()

    auth = AuthService(db)
    with pytest.raises(AppError) as e:
        await auth.login(email, "Test123!")
    assert e.value.code == "SSO_REQUIRED"

    member.is_break_glass = True
    await db.flush()
    result = await auth.login(email, "Test123!")
    assert result.access_token
    audit = (
        (
            await db.execute(
                select(IntegrationEvent).where(
                    IntegrationEvent.org_id == org.id,
                    IntegrationEvent.type == "com.openskill.org.breakglass.login.v1",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(audit) == 1


@pytest.mark.asyncio
async def test_enforce_flag_requires_break_glass_member(db):
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    conn = await svc.create(org.id, protocol="oidc", oidc_issuer=ISSUER, oidc_client_id="c")
    with pytest.raises(AppError) as e:
        await svc.update(org.id, conn.id, enforce_sso=True)
    assert e.value.code == "BREAK_GLASS_UNVERIFIED"
    await svc.set_break_glass(org.id, owner.id, enabled=True, actor_role=OrgRole.OWNER)
    updated = await svc.update(org.id, conn.id, enforce_sso=True)
    assert updated.enforce_sso is True


@pytest.mark.asyncio
async def test_sso_admin_rules(db):
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    with pytest.raises(AppError):
        await svc.create(org.id, protocol="saml")  # P3b
    with pytest.raises(AppError) as e:
        await svc.create(
            org.id,
            protocol="oidc",
            oidc_issuer=ISSUER,
            oidc_client_id="c",
            default_role="owner",
        )
    assert e.value.code == "SSO_JIT_ROLE_INVALID"
    conn = await svc.create(
        org.id,
        protocol="oidc",
        oidc_issuer=ISSUER,
        oidc_client_id="c",
        oidc_client_secret="x",
    )
    # secret is stored as ciphertext only
    assert conn.oidc_client_secret_ct and conn.oidc_client_secret_ct != "x"
    # cross-tenant uniform 404
    other = await _org(db, await _user(db))
    with pytest.raises(AppError) as e2:
        await svc.get(other.id, conn.id)
    assert e2.value.status_code == 404


# ── R7 adversarial-review regression pins ──


@pytest.mark.asyncio
async def test_resolution_tolerates_junk_claim_types(db):
    """A dict/list email or display_name from a hostile IdP must queue, not
    500 at the DB column (review defect #3)."""
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "junk.example.edu")
    svc = IdentityService(db)
    with pytest.raises(AppError) as e:
        await svc.resolve(_ident(org, subject="junk-1", email={"evil": "dict"}, verified=True))
    assert e.value.code in ("IDENTITY_AMBIGUOUS", "SSO_NO_ACCOUNT")
    with pytest.raises(AppError):
        await svc.resolve(
            VerifiedExternalIdentity(
                org_id=org.id,
                source="sso",
                connection_ref="01CONNJ",
                subject=["not", "a", "string"],
                email="a@junk.example.edu",
                email_verified=True,
            )
        )


# ── R11: pending-domain DNS sweep ──


@pytest.mark.asyncio
async def test_domain_sweep_verifies_and_expires(db, monkeypatch):
    from datetime import UTC, datetime, timedelta

    import app.integrations.services.domains as mod
    from app.integrations.models import OrgDomain

    owner = await _user(db)
    org = await _org(db, owner)
    svc = OrgDomainService(db)
    fresh = await svc.claim(org.id, f"sweep-{uuid.uuid4().hex[:6]}.example.edu")
    stale = await svc.claim(org.id, f"old-{uuid.uuid4().hex[:6]}.example.edu")
    # Backdate the stale claim beyond the 7-day window.
    await db.execute(
        OrgDomain.__table__.update()
        .where(OrgDomain.id == stale.id)
        .values(created_at=datetime.now(UTC) - timedelta(days=8))
    )

    db.expire_all()  # the core UPDATE above bypassed the identity map

    class Yep:
        async def verify(self, h, t):
            return True

    monkeypatch.setattr(mod, "get_verifier", lambda: Yep())
    changed = await svc.sweep_pending()
    # >= not ==: the sweep is global and other committed pending rows (e.g.
    # a live-E2E leftover) may legitimately be swept in the same pass.
    assert changed >= 2
    await db.refresh(fresh)
    await db.refresh(stale)
    assert fresh.status == "verified"
    assert stale.status == "failed"  # expired before DNS was consulted


# ── R20: link administration (list + reversible unlink) ──


@pytest.mark.asyncio
async def test_link_list_and_unlink_frees_subject_for_relink(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "corp-r20.io")
    member = await _user(db, email="r20@corp-r20.io")
    db.add(
        OrgMember(
            org_id=org.id, user_id=member.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    await db.flush()
    svc = IdentityService(db)
    res = await svc.resolve(_ident(org, subject="r20-sub", email="r20@corp-r20.io"))
    assert res.user.id == member.id

    links = await svc.list_links(org.id)
    assert [link.id for link in links] == [res.link.id]
    assert await svc.list_links(org.id, user_id=member.id) != []
    assert await svc.list_links(org.id, user_id=owner.id) == []

    # Reversible (ADR §2.5): revoke keeps the row but frees (conn, subject).
    await svc.unlink(org.id, res.link.id)
    assert await svc.list_links(org.id) == []
    import pytest as _pytest

    from app.exceptions import AppError as _AppError

    with _pytest.raises(_AppError) as exc:  # idempotence: second revoke is 404
        await svc.unlink(org.id, res.link.id)
    assert exc.value.status_code == 404

    # Cross-org revoke is a uniform 404 (no existence oracle).
    other = await _org(db, await _user(db))
    res2 = await svc.resolve(_ident(org, subject="r20-sub", email="r20@corp-r20.io"))
    with _pytest.raises(_AppError) as exc2:
        await svc.unlink(other.id, res2.link.id)
    assert exc2.value.status_code == 404

    # Re-link after revoke produced a NEW active link for the same subject.
    assert res2.link.id != res.link.id


# ── R29: identity-resolution mutation-probe killers ──


async def _add_member(db, org, email, status=MemberStatus.ACTIVE):
    u = await _user(db, email=email)
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.STUDENT, status=status))
    await db.flush()
    return u


@pytest.mark.asyncio
async def test_resolution_email_match_is_case_insensitive(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "case-r29.io")
    member = await _add_member(db, org, "alice@case-r29.io")
    svc = IdentityService(db)
    # IdP sends mixed case; member stored lowercase — must still match.
    res = await svc.resolve(_ident(org, subject="case-sub", email="ALICE@CASE-R29.io"))
    assert res.user.id == member.id and not res.jit_created


@pytest.mark.asyncio
async def test_resolution_two_members_same_email_queue_not_takeover(db):
    """Exactly two active members sharing an email: NEVER link to either —
    queue for the admin. (>=1 mutant would hand the account to the first.)"""
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "dup-r29.io")
    shared = "shared@dup-r29.io"
    await _add_member(db, org, shared)
    # Second user with the same email but different row (simulate legacy dupes
    # via distinct casing — stored emails differ, lower() collides).
    await _add_member(db, org, "SHARED@dup-r29.io")
    svc = IdentityService(db)
    with pytest.raises(AppError) as exc:
        await svc.resolve(_ident(org, subject="dup-sub", email=shared))
    assert exc.value.code == "IDENTITY_AMBIGUOUS"
    q = await svc.list_queue(org.id)
    assert any(i.subject == "dup-sub" and i.reason == "multiple_member_matches" for i in q)


@pytest.mark.asyncio
async def test_resolution_archived_member_never_matches(db):
    """An ARCHIVED membership must not resolve: zero active matches -> queue
    (no JIT) rather than silently reactivating access."""
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "arch-r29.io")
    await _add_member(db, org, "gone@arch-r29.io", status=MemberStatus.ARCHIVED)
    svc = IdentityService(db)
    with pytest.raises(AppError) as exc:
        await svc.resolve(_ident(org, subject="arch-sub", email="gone@arch-r29.io"))
    assert exc.value.code == "SSO_NO_ACCOUNT"
    q = await svc.list_queue(org.id)
    assert any(i.subject == "arch-sub" and i.reason == "no_member_match" for i in q)


@pytest.mark.asyncio
async def test_jit_user_properties_and_inactive_platform_account(db):
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "jit-r29.io")
    svc = IdentityService(db)
    # Fresh JIT: account is email_verified (verified domain + verified IdP
    # email) and email normalized to lowercase.
    res = await svc.resolve(
        _ident(org, subject="jit-sub", email="NewPerson@JIT-R29.io"), allow_jit=True
    )
    assert res.jit_created and res.user.email == "newperson@jit-r29.io"
    assert res.user.email_verified is True
    # A SUSPENDED platform account with that email: membership-only JIT must
    # refuse and queue, never attach an org to a disabled account.
    dead = await _user(db, email="dead@jit-r29.io")
    dead.status = UserStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.resolve(_ident(org, subject="dead-sub", email="dead@jit-r29.io"), allow_jit=True)
    assert exc.value.code == "IDENTITY_AMBIGUOUS"
    q = await svc.list_queue(org.id)
    assert any(i.reason == "existing_account_inactive" for i in q)


@pytest.mark.asyncio
async def test_queue_link_refuses_archived_target(db):
    """Admin queue 'link' action must only accept an ACTIVE member target."""
    owner = await _user(db)
    org = await _org(db, owner)
    svc = IdentityService(db)
    ghost = await _add_member(
        db, org, f"ghost-{uuid.uuid4().hex[:6]}@q-r29.io", status=MemberStatus.ARCHIVED
    )
    with pytest.raises(AppError):
        await svc.resolve(_ident(org, subject="q-sub", email=None, verified=False))
    item = next(i for i in await svc.list_queue(org.id) if i.subject == "q-sub")
    with pytest.raises(AppError) as exc:
        await svc.resolve_queue_item(
            org.id, item.id, action="link", user_id=ghost.id, actor_id=owner.id
        )
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_linked_but_suspended_user_refused_on_hot_path(db):
    """R29: an EXISTING link must not grant access once the user is
    suspended — the hot path re-checks account status on every login."""
    owner = await _user(db)
    org = await _org(db, owner)
    await _verified_domain(db, org, "hot-r29.io")
    member = await _add_member(db, org, "hot@hot-r29.io")
    svc = IdentityService(db)
    res = await svc.resolve(_ident(org, subject="hot-sub", email="hot@hot-r29.io"))
    assert res.user.id == member.id
    member.status = UserStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.resolve(_ident(org, subject="hot-sub", email="hot@hot-r29.io"))
    assert exc.value.code == "SSO_NO_ACCOUNT"


# ── R31: OIDC mutation-probe killers ──


@pytest.mark.asyncio
async def test_oidc_expired_state_missing_exp_and_unverified_email(db):
    """Kills: expired-state acceptance, optional-exp acceptance, and
    trusting an email_verified=false claim."""
    from datetime import timedelta as _td

    import app.integrations.services.sso_oidc as mod
    from app.integrations.models import SsoLoginState

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)
    email = f"r31-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    def factory(form):
        return _mint_id_token(
            sub="r31-sub", email=email, nonce=factory.nonce, aud="client-1", **factory.over
        )

    factory.over = {}
    svc.egress = FakeIdp(factory)

    async def start():
        url = await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.test/cb")
        qs = parse_qs(urlsplit(url).query)
        factory.nonce = qs["nonce"][0]
        return qs["state"][0]

    # 1. Expired state row refused even though the token itself is valid.
    state_val = await start()
    row = await db.get(SsoLoginState, state_val)
    row.expires_at = datetime.now(UTC) - _td(minutes=1)
    await db.flush()
    with pytest.raises(AppError):
        await svc.handle_callback(
            state_value=state_val, code="c", redirect_uri="https://app.test/cb"
        )

    # 2. Token WITHOUT exp refused (require list, not just validity-if-present).
    state_val = await start()

    def no_exp_factory(form):
        claims = {
            "iss": ISSUER,
            "aud": "client-1",
            "sub": "r31-sub",
            "email": email,
            "email_verified": True,
            "nonce": no_exp_factory.nonce,
            "iat": int(time.time()),
        }
        return pyjwt.encode(claims, _PRIV, algorithm="RS256", headers={"kid": "k1"})

    no_exp_factory.nonce = factory.nonce
    svc.egress = FakeIdp(no_exp_factory)
    with pytest.raises(AppError):
        await svc.handle_callback(
            state_value=state_val, code="c", redirect_uri="https://app.test/cb"
        )
    svc.egress = FakeIdp(factory)

    # 3. email_verified=false claim: must QUEUE, never match/JIT.
    factory.over = {"email_verified": False}
    state_val = await start()
    with pytest.raises(AppError) as exc2:
        await svc.handle_callback(
            state_value=state_val, code="c", redirect_uri="https://app.test/cb"
        )
    assert exc2.value.code in ("IDENTITY_AMBIGUOUS", "SSO_NO_ACCOUNT")


# ── R42: OIDC back-channel logout ──


def _mint_logout_token(*, sub, aud="client-1", jti=None, **over):
    claims = {
        "iss": ISSUER,
        "aud": aud,
        "sub": sub,
        "jti": jti or uuid.uuid4().hex,
        "iat": int(time.time()),
        "exp": int(time.time()) + 120,
        "events": {"http://schemas.openid.net/event/backchannel-logout": {}},
    }
    claims.update(over)
    claims = {k: v for k, v in claims.items() if v is not None}
    return pyjwt.encode(claims, _PRIV, algorithm="RS256", headers={"kid": "k1"})


@pytest.mark.asyncio
async def test_backchannel_logout_revokes_sessions_and_rejects_bad_tokens(db):
    import app.integrations.services.sso_oidc as mod
    from app.integrations.services.sso_oidc import handle_backchannel_logout
    from app.models.user import RefreshToken

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)
    email = f"bcl-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    def factory(form):
        return _mint_id_token(sub="bcl-sub", email=email, nonce=factory.nonce, aud="client-1")

    svc.egress = FakeIdp(factory)
    url = await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.test/cb")
    qs = parse_qs(urlsplit(url).query)
    factory.nonce = qs["nonce"][0]
    _, result, _rt = await svc.handle_callback(
        state_value=qs["state"][0], code="c", redirect_uri="https://app.test/cb"
    )
    user_id = result.user.id
    # Give the user a live refresh token to sweep.
    from datetime import timedelta as _td

    from app.services.auth import AuthService

    db.add(
        RefreshToken(
            user_id=user_id, token_hash="h" * 64, expires_at=datetime.now(UTC) + _td(days=7)
        )
    )
    await db.flush()

    tok = _mint_logout_token(sub="bcl-sub")
    swept = await handle_backchannel_logout(db, conn.id, tok, service=svc)
    assert swept == 1
    live = (
        (
            await db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
                )
            )
        )
        .scalars()
        .all()
    )
    assert live == []

    # jti replay refused.
    with pytest.raises(AppError):
        await handle_backchannel_logout(db, conn.id, tok, service=svc)
    # nonce prohibited (id_token must not pass as logout_token).
    with pytest.raises(AppError):
        await handle_backchannel_logout(
            db, conn.id, _mint_logout_token(sub="bcl-sub", nonce="n"), service=svc
        )
    # events member required.
    with pytest.raises(AppError):
        await handle_backchannel_logout(
            db, conn.id, _mint_logout_token(sub="bcl-sub", events={"other": {}}), service=svc
        )
    # missing sub refused.
    with pytest.raises(AppError):
        await handle_backchannel_logout(db, conn.id, _mint_logout_token(sub=None), service=svc)
    # stale iat refused.
    with pytest.raises(AppError):
        await handle_backchannel_logout(
            db,
            conn.id,
            _mint_logout_token(
                sub="bcl-sub", iat=int(time.time()) - 3600, exp=int(time.time()) + 3600
            ),
            service=svc,
        )
    # A REVOKED link is not authoritative: logout for its subject sweeps 0.
    from app.integrations.models import ExternalIdentityLink as _Link

    link_row = (
        await db.execute(
            select(_Link).where(_Link.connection_ref == conn.id, _Link.subject == "bcl-sub")
        )
    ).scalar_one()
    link_row.revoked_at = datetime.now(UTC)
    await db.flush()
    assert (
        await handle_backchannel_logout(db, conn.id, _mint_logout_token(sub="bcl-sub"), service=svc)
        == 0
    )
    link_row.revoked_at = None
    await db.flush()

    # unknown subject: clean 200-equivalent (0 swept), no error oracle.
    assert (
        await handle_backchannel_logout(
            db, conn.id, _mint_logout_token(sub="never-seen"), service=svc
        )
        == 0
    )
    assert AuthService is not None


@pytest.mark.asyncio
async def test_sso_admin_input_screens(db):
    """R43: protocol whitelist, issuer/SSO-URL egress screening, connection
    limit, and oversized/non-string cert entries."""
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)

    with pytest.raises(AppError) as e1:
        await svc.create(org.id, protocol="ldap")
    assert e1.value.code == "SSO_PROTOCOL_INVALID"

    from app.integrations.security import EgressBlockedError

    with pytest.raises(EgressBlockedError):
        await svc.create(
            org.id,
            protocol="oidc",
            oidc_issuer="https://169.254.169.254/",
            oidc_client_id="c",
            oidc_client_secret="s",
        )
    with pytest.raises(EgressBlockedError):
        await svc.create(
            org.id,
            protocol="saml",
            idp_entity_id="e",
            idp_sso_url="ftp://idp.example.com/sso",
        )

    with pytest.raises(AppError) as e2:
        await svc.create(
            org.id,
            protocol="saml",
            idp_entity_id="e",
            idp_sso_url="https://idp.example.com/sso",
            idp_certificates=[{"pem": "x" * 10_001}],
        )
    assert e2.value.code == "SSO_CONFIG_INVALID"
    with pytest.raises(AppError):
        await svc.create(
            org.id,
            protocol="saml",
            idp_entity_id="e",
            idp_sso_url="https://idp.example.com/sso",
            idp_certificates=[{"pem": 123}],
        )

    # Connection limit enforced.
    made = 0
    with pytest.raises(AppError) as e3:
        for i in range(25):
            await svc.create(
                org.id,
                protocol="oidc",
                oidc_issuer=f"https://idp{i}.example.com",
                oidc_client_id=f"c{i}",
                oidc_client_secret="s",
            )
            made += 1
    assert e3.value.code == "SSO_LIMIT_REACHED" and made >= 1


@pytest.mark.asyncio
async def test_oidc_deep_link_round_trip_and_screen(db):
    """R70: return_to survives authorize -> state row -> callback; absolute
    URLs and protocol-relative paths are dropped at the API screen."""
    import app.integrations.services.sso_oidc as mod

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)
    email = f"dl-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    def factory(form):
        return _mint_id_token(sub="dl-sub", email=email, nonce=factory.nonce, aud="client-1")

    svc.egress = FakeIdp(factory)
    url = await svc.build_authorize_redirect(
        conn.id, redirect_uri="https://app.test/cb", return_to="/dashboard/orgs/X/projects"
    )
    qs = parse_qs(urlsplit(url).query)
    factory.nonce = qs["nonce"][0]
    _, result, return_to = await svc.handle_callback(
        state_value=qs["state"][0], code="c", redirect_uri="https://app.test/cb"
    )
    assert return_to == "/dashboard/orgs/X/projects"

    # API screen drops non-relative targets before they reach the state row.
    from app.integrations.api import sso as sso_api

    src = __import__("inspect").getsource(sso_api.oidc_authorize)
    assert 'startswith("/")' in src and 'startswith("//")' in src


@pytest.mark.asyncio
async def test_oidc_pkce_s256(db):
    """R135 (RFC 9700): the authorize redirect carries a S256 code_challenge
    derived from a per-state verifier, and the token exchange replays that
    exact verifier — an intercepted code alone is useless."""
    import base64
    import hashlib

    import app.integrations.services.sso_oidc as mod
    from app.integrations.models.sso import SsoLoginState

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)
    email = f"pkce-{uuid.uuid4().hex[:8]}@oidc.example.edu"

    captured_forms: list[dict] = []

    def factory(form):
        captured_forms.append(form)
        return _mint_id_token(sub="pkce-sub", email=email, nonce=factory.nonce, aud="client-1")

    fake = FakeIdp(factory)
    svc.egress = fake

    url = await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.test/cb")
    q = parse_qs(urlsplit(url).query)
    assert q["code_challenge_method"] == ["S256"]
    challenge = q["code_challenge"][0]
    state_id = q["state"][0]
    row = await db.get(SsoLoginState, state_id)
    assert row.code_verifier and 43 <= len(row.code_verifier) <= 128
    expect = (
        base64.urlsafe_b64encode(hashlib.sha256(row.code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    assert challenge == expect
    factory.nonce = row.nonce

    await svc.handle_callback(code="c0de", state_value=state_id, redirect_uri="https://app.test/cb")
    assert captured_forms, "token endpoint never called"
    assert captured_forms[0]["code_verifier"] == [row.code_verifier]


@pytest.mark.asyncio
async def test_concurrent_domain_claim_same_org_no_500(db):
    """R207: two sessions claiming the same (org, domain) concurrently must
    end with ONE row and no IntegrityError 500 (loser used to hit
    uq_intg_domain_org at a bare flush -> 500 + poisoned session).

    Honest scope (same as the R199 SAML replay test): a single event loop
    does not force the dup-SELECT/INSERT interleave, so this asserts the
    serialized+idempotent OUTCOME; the org FOR UPDATE lock and the
    savepoint-wrapped INSERT are the guards for true parallelism."""
    import asyncio

    from app.core.database import AsyncSessionLocal

    user = await _user(db)
    org = await _org(db, user)
    await db.commit()
    domain = f"race-{uuid.uuid4().hex[:10]}.example.edu"

    async def _claim():
        async with AsyncSessionLocal() as s:
            row = await OrgDomainService(s).claim(org.id, domain)
            rid = row.id
            await s.commit()
            return rid

    r1, r2 = await asyncio.gather(_claim(), _claim())
    assert r1 == r2  # serialized + idempotent: one row, no IntegrityError 500
    rows = (await db.execute(select(OrgDomain).where(OrgDomain.domain == domain))).scalars().all()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_unparseable_certificate_rejected_at_create(db):
    """R244 (survivor pin): a pinned cert that is not valid X.509 PEM must be
    a clean 422 at create — silently accepting garbage leaves a SAML
    connection that can never verify anything (or worse, skips pinning)."""
    user = await _user(db)
    org = await _org(db, user)
    with pytest.raises(AppError) as e:
        await SsoAdminService(db).create(
            org.id,
            protocol="saml",
            idp_entity_id="https://idp.example.com",
            idp_sso_url="https://idp.example.com/sso",
            idp_certificates=[
                {"pem": "-----BEGIN CERTIFICATE-----\nnope\n-----END CERTIFICATE-----"}
            ],
        )
    assert e.value.code == "SSO_CONFIG_INVALID"


@pytest.mark.asyncio
async def test_discovery_issuer_mismatch_rejected(db):
    """R251 (RFC 8414 §3.3 — issuer mix-up defense): the discovery metadata's
    issuer MUST equal the configured issuer. A multi-tenant IdP host (or a
    confused deployment) returning a DIFFERENT issuer would otherwise make us
    accept that other issuer's tokens, since decode validates against
    doc["issuer"]."""
    import app.integrations.services.sso_oidc as mod

    org, conn = await _oidc_setup(db)
    svc = mod.OidcService(db)

    class EvilDiscoveryIdp(FakeIdp):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            path = urlsplit(url).path
            if path.endswith("/.well-known/openid-configuration"):
                doc = _discovery_doc()
                doc["issuer"] = "https://other-tenant.example.com"
                return httpx.Response(200, json=doc, request=httpx.Request(method, url))
            return await super().request(
                method, url, headers=headers, content=content, read_timeout=read_timeout
            )

    svc.egress = EvilDiscoveryIdp(lambda form: "unused")
    with pytest.raises(AppError) as e:
        await svc.build_authorize_redirect(conn.id, redirect_uri="https://app.example.com/cb")
    assert e.value.status_code == 401


@pytest.mark.asyncio
async def test_enforce_sso_gate_requires_verified_domain(db):
    """R255 (survivor pin — over-enforcement direction): the SSO-required
    gate keys on VERIFIED domains only. An org whose domain claim is still
    PENDING must not block its members' password logins."""
    from app.services.auth import AuthService

    owner = await _user(db)
    org = await _org(db, owner)
    pend = f"pend-{uuid.uuid4().hex[:8]}.example.edu"
    db.add(OrgDomain(org_id=org.id, domain=pend, status="pending", verification_token="t"))
    email = f"pp-{uuid.uuid4().hex[:8]}@{pend}"
    emp = await _user(db, email=email)
    db.add(
        OrgMember(org_id=org.id, user_id=emp.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE)
    )
    db.add(
        SsoConnection(
            org_id=org.id,
            protocol="oidc",
            status="active",
            oidc_issuer=ISSUER,
            oidc_client_id="c",
            enforce_sso=True,
        )
    )
    await db.flush()
    result = await AuthService(db).login(email, "Test123!")
    assert result.access_token  # pending domain never enforces


@pytest.mark.asyncio
async def test_break_glass_capped_at_two(db):
    """R255 (survivor pin): at most TWO break-glass designees per org — the
    cap bounds the password-bypass surface under enforced SSO."""
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    from app.models.organization import OrgRole as _Role

    members = [owner]
    for _i in range(2):
        u = await _user(db)
        db.add(OrgMember(org_id=org.id, user_id=u.id, role=_Role.ADMIN, status=MemberStatus.ACTIVE))
        members.append(u)
    await db.flush()
    await svc.set_break_glass(org.id, members[0].id, enabled=True, actor_role=_Role.OWNER)
    await svc.set_break_glass(org.id, members[1].id, enabled=True, actor_role=_Role.OWNER)
    with pytest.raises(AppError) as e:
        await svc.set_break_glass(org.id, members[2].id, enabled=True, actor_role=_Role.OWNER)
    assert e.value.code == "BREAK_GLASS_LIMIT"
    # Re-enabling an EXISTING designee is idempotent, not a third slot.
    await svc.set_break_glass(org.id, members[1].id, enabled=True, actor_role=_Role.OWNER)


@pytest.mark.asyncio
async def test_domain_cross_org_idor_uniform_404(db):
    """R257 (survivor pin): OrgDomainService.get keys on (id, org_id) — org B
    must not read, verify, or DELETE org A's domain claim (deleting a rival's
    verified domain would drop their SSO enforcement). Uniform 404, no
    existence oracle."""
    owner_a = await _user(db)
    org_a = await _org(db, owner_a)
    dom = f"idor-{uuid.uuid4().hex[:8]}.example.edu"
    row = await _verified_domain(db, org_a, dom)
    owner_b = await _user(db)
    org_b = await _org(db, owner_b)
    svc = OrgDomainService(db)
    for op in (svc.get, svc.verify, svc.delete):
        with pytest.raises(AppError) as e:
            await op(org_b.id, row.id)
        assert e.value.code == "DOMAIN_NOT_FOUND"
        assert e.value.status_code == 404
    # the domain is untouched
    assert (await svc.get(org_a.id, row.id)).status == "verified"


@pytest.mark.asyncio
async def test_match_queue_cross_org_wall(db):
    """R276 (survivor pin, IDOR class): org B cannot resolve org A's
    identity match-queue item — uniform 404."""
    from app.integrations.models import IdentityMatchQueue
    from app.integrations.services.identity import IdentityService

    owner_a = await _user(db)
    org_a = await _org(db, owner_a)
    owner_b = await _user(db)
    org_b = await _org(db, owner_b)
    item = IdentityMatchQueue(
        org_id=org_a.id,
        source="scim",
        connection_ref="c",
        subject="s",
        email="q@x.edu",
        reason="ambiguous",
        payload={},
        status="pending",
    )
    db.add(item)
    await db.flush()
    with pytest.raises(AppError) as e:
        await IdentityService(db).resolve_queue_item(
            org_b.id, item.id, action="dismiss", user_id=None, actor_id=owner_b.id
        )
    assert e.value.code == "IDENTITY_QUEUE_NOT_FOUND" and e.value.status_code == 404
    await db.refresh(item)
    assert item.status == "pending"


@pytest.mark.asyncio
async def test_sso_update_validations(db):
    """R294 (survivor pins): the UPDATE path re-validates what create
    validates — bogus status, admin default_role (JIT mint ceiling), and
    an internal oidc_issuer (egress screen) are all refused, and nothing
    on the row changes."""
    from app.integrations.security import EgressBlockedError

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    conn = await svc.create(
        org.id,
        protocol="oidc",
        oidc_issuer="https://idp.example.com",
        oidc_client_id="c",
    )

    with pytest.raises(AppError) as e:
        await svc.update(org.id, conn.id, status="banana")
    assert e.value.code == "SSO_CONFIG_INVALID"

    with pytest.raises(AppError) as e:
        await svc.update(org.id, conn.id, default_role="admin")
    assert e.value.code == "SSO_JIT_ROLE_INVALID"

    with pytest.raises(EgressBlockedError):
        await svc.update(org.id, conn.id, oidc_issuer="http://169.254.169.254/x")

    await db.refresh(conn)
    assert conn.oidc_issuer == "https://idp.example.com"
    assert conn.default_role == "student"


@pytest.mark.asyncio
async def test_queue_resolve_single_winner_under_race(db):
    """R308 (R306 class): two admins adjudicating the SAME pending item
    concurrently yield exactly one winner — the loser gets a clean 409,
    never a link+reject mix."""
    import asyncio

    from app.core.database import AsyncSessionLocal
    from app.integrations.models import IdentityMatchQueue
    from app.integrations.services.identity import IdentityService

    owner = await _user(db)
    org = await _org(db, owner)
    item = IdentityMatchQueue(
        org_id=org.id,
        source="scim",
        connection_ref="c",
        subject=f"rq-{uuid.uuid4().hex[:6]}",
        email="rq@x.edu",
        reason="ambiguous",
        payload={},
        status="pending",
    )
    db.add(item)
    await db.commit()

    async def resolver(n):
        async with AsyncSessionLocal() as own:
            try:
                await IdentityService(own).resolve_queue_item(
                    org.id,
                    item.id,
                    action="reject",
                    user_id=None,
                    actor_id=owner.id,
                )
                await own.commit()
                return "won"
            except AppError as exc:
                return exc.code

    results = sorted(await asyncio.gather(resolver(1), resolver(2)))
    assert results == ["IDENTITY_QUEUE_RESOLVED", "won"]
    await db.refresh(item)
    assert item.status == "rejected"
    # tidy the committed row — global-select assertions elsewhere are
    # sensitive to shared-DB leftovers.
    await db.delete(item)
    await db.commit()


@pytest.mark.asyncio
async def test_break_glass_login_event_carries_ip_and_ua(db):
    """R313 (ADR §5.2): the org.breakglass.login mesh event carries IP + UA
    — a password bypass under enforced SSO must be attributable."""
    from app.integrations.models import IntegrationEvent
    from app.services.auth import AuthService

    owner = await _user(db)
    org = await _org(db, owner)
    dom = f"bgip-{uuid.uuid4().hex[:8]}.example.edu"
    await _verified_domain(db, org, dom)
    email = f"bg-{uuid.uuid4().hex[:8]}@{dom}"
    emp = await _user(db, email=email)
    db.add(
        OrgMember(
            org_id=org.id,
            user_id=emp.id,
            role=OrgRole.ADMIN,
            status=MemberStatus.ACTIVE,
            is_break_glass=True,
        )
    )
    db.add(
        SsoConnection(
            org_id=org.id,
            protocol="oidc",
            status="active",
            oidc_issuer=ISSUER,
            oidc_client_id="c",
            enforce_sso=True,
        )
    )
    await db.flush()
    result = await AuthService(db).login(
        email, "Test123!", ip_address="198.51.100.7", device_info="E2E-UA/1.0"
    )
    assert result.access_token
    ev = (
        (
            await db.execute(
                select(IntegrationEvent).where(
                    IntegrationEvent.type == "com.openskill.org.breakglass.login.v1",
                    IntegrationEvent.subject == emp.id,
                )
            )
        )
        .scalars()
        .first()
    )
    assert ev is not None
    assert ev.data["ip_address"] == "198.51.100.7"
    assert ev.data["user_agent"] == "E2E-UA/1.0"


@pytest.mark.asyncio
async def test_idn_domain_email_matching_consistent(db):
    """R319: claim stores IDN domains as IDNA/UTS46 punycode — every
    email-domain comparison must normalize the SAME way or IDN tenants'
    discovery / enforce gate / JIT matching silently un-match. Walks the
    unicode domain end to end."""
    from app.integrations.services.domains import normalized_email_domain
    from app.services.auth import AuthService

    uni = f"школа-{uuid.uuid4().hex[:6]}.рф"
    owner = await _user(db)
    org = await _org(db, owner)
    svc = OrgDomainService(db)
    row = await svc.claim(org.id, uni)
    assert row.domain.startswith("xn--")  # stored canonical punycode

    # helper folds the unicode email domain to the same form
    assert normalized_email_domain(f"u@{uni}") == row.domain
    assert normalized_email_domain(f"u@{row.domain}") == row.domain
    assert normalized_email_domain("not-an-email") == ""

    row.status = "verified"
    await db.flush()

    # discovery routes the unicode email to the org
    assert await svc.org_for_email_domain(f"user@{uni}") == org.id

    # enforce gate covers the IDN member's password login
    email = f"idn-{uuid.uuid4().hex[:6]}@{uni}"
    emp = await _user(db, email=email)
    db.add(
        OrgMember(org_id=org.id, user_id=emp.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE)
    )
    db.add(
        SsoConnection(
            org_id=org.id,
            protocol="oidc",
            status="active",
            oidc_issuer=ISSUER,
            oidc_client_id="c",
            enforce_sso=True,
        )
    )
    await db.flush()
    with pytest.raises(AppError) as e:
        await AuthService(db).login(email, "Test123!")
    assert e.value.code == "SSO_REQUIRED"

    # identity resolution matches the verified IDN domain by email
    ident = VerifiedExternalIdentity(
        org_id=org.id,
        source="oidc",
        connection_ref="conn-idn",
        subject=f"s-{uuid.uuid4().hex[:6]}",
        email=email,
        email_verified=True,
    )
    res = await IdentityService(db).resolve(ident)
    assert res.user.id == emp.id


@pytest.mark.asyncio
async def test_jwks_kid_miss_refetch_floor(db, monkeypatch):
    """R325: the JWKS cache's kid-miss behavior is a security/availability
    bound — a cache hit never refetches, a kid MISS within the 30s floor
    returns the stale set WITHOUT a network call (an attacker spraying
    random kids cannot stampede our egress at the IdP), and a miss after
    the floor refetches exactly once."""
    import app.integrations.services.sso_oidc as oidc_mod
    from app.integrations.services.sso_oidc import OidcService

    owner = await _user(db)
    org = await _org(db, owner)
    conn = await SsoAdminService(db).create(
        org.id, protocol="oidc",
        oidc_issuer=f"https://jwks-{uuid.uuid4().hex[:6]}.example.com",
        oidc_client_id="c",
    )

    calls = {"n": 0}
    from cryptography.hazmat.primitives.asymmetric import rsa as _rsa

    jwk_key = _rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = jwk_key.public_key().public_numbers()

    def _b64u(i, length):
        import base64 as _b
        return _b.urlsafe_b64encode(i.to_bytes(length, "big")).rstrip(b"=").decode()

    class _Egress:
        async def request(self, method, url, **kw):
            calls["n"] += 1
            return httpx.Response(
                200,
                json={"keys": [{
                    "kty": "RSA", "kid": f"kid-{calls['n']}", "use": "sig",
                    "n": _b64u(pub.n, 256), "e": _b64u(pub.e, 3),
                }]},
                request=httpx.Request(method, url),
            )

    svc = OidcService(db)
    svc.egress = _Egress()
    now = {"t": 1000.0}
    monkeypatch.setattr(oidc_mod.time, "monotonic", lambda: now["t"])
    oidc_mod._jwks_cache.pop(conn.id, None)

    # first call: no cache -> one fetch
    keys = await svc._jwks_keys(conn, "https://idp/jwks", kid="kid-1")
    assert calls["n"] == 1 and "kid-1" in keys

    # cache hit (known kid): zero additional fetches
    await svc._jwks_keys(conn, "https://idp/jwks", kid="kid-1")
    assert calls["n"] == 1

    # kid MISS inside the floor: stale set returned, still no fetch
    now["t"] += 5
    stale = await svc._jwks_keys(conn, "https://idp/jwks", kid="kid-sprayed")
    assert calls["n"] == 1 and "kid-1" in stale

    # kid miss AFTER the floor: exactly one refetch
    now["t"] += 60
    fresh = await svc._jwks_keys(conn, "https://idp/jwks", kid="kid-2")
    assert calls["n"] == 2 and "kid-2" in fresh
    oidc_mod._jwks_cache.pop(conn.id, None)


@pytest.mark.asyncio
async def test_last_break_glass_cannot_be_removed_under_enforced_sso(db):
    """R331 (R330 class): with enforce_sso active, removing the LAST
    designee deletes the escape hatch the flip required — refused 409.
    Allowed again once enforce_sso is off, or when a second designee
    remains."""
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    conn = await svc.create(
        org.id, protocol="oidc", oidc_issuer=ISSUER, oidc_client_id="c",
    )
    conn.status = "active"
    from app.models.organization import OrgRole as _Role

    await svc.set_break_glass(org.id, owner.id, enabled=True, actor_role=_Role.OWNER)
    await svc.update(org.id, conn.id, enforce_sso=True)

    # last designee + enforced -> refused, flag intact
    with pytest.raises(AppError) as e:
        await svc.set_break_glass(org.id, owner.id, enabled=False, actor_role=_Role.OWNER)
    assert e.value.code == "BREAK_GLASS_REQUIRED"
    member = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org.id, OrgMember.user_id == owner.id
            )
        )
    ).scalar_one()
    assert member.is_break_glass is True

    # a second designee makes removal of the first fine
    u2 = await _user(db)
    db.add(OrgMember(org_id=org.id, user_id=u2.id, role=OrgRole.ADMIN,
                     status=MemberStatus.ACTIVE))
    await db.flush()
    await svc.set_break_glass(org.id, u2.id, enabled=True, actor_role=_Role.OWNER)
    await svc.set_break_glass(org.id, owner.id, enabled=False, actor_role=_Role.OWNER)

    # and with enforce off, the last one can retire too
    await svc.update(org.id, conn.id, enforce_sso=False)
    await svc.set_break_glass(org.id, u2.id, enabled=False, actor_role=_Role.OWNER)
