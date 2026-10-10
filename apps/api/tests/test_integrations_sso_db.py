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
    q = (await db.execute(select(IdentityMatchQueue))).scalars().all()
    assert q and q[-1].reason == "email_unverified_or_foreign_domain"
    # Retried login does not duplicate the pending row.
    with pytest.raises(AppError):
        await svc.resolve(_ident(org, email="a@acme.edu", verified=False))
    q2 = (
        await db.execute(
            select(IdentityMatchQueue).where(IdentityMatchQueue.subject == "sub-1")
        )
    ).scalars().all()
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
        await db.execute(
            select(ExternalIdentityLink).where(
                ExternalIdentityLink.user_id == member.id,
                ExternalIdentityLink.revoked_at.is_(None),
            )
        )
    ).scalars().all()
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
            select(OrgMember).where(
                OrgMember.org_id == org.id, OrgMember.user_id == r.user.id
            )
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
        _ident(org1, conn_ref="01CONNA", subject="dup", email=f"a-{uuid.uuid4().hex[:5]}@one.example.edu"),
        allow_jit=True,
    )
    r2 = await svc.resolve(
        _ident(org2, conn_ref="01CONNB", subject="dup", email=f"b-{uuid.uuid4().hex[:5]}@two.example.edu"),
        allow_jit=True,
    )
    assert r1.user.id != r2.user.id
    links = (
        await db.execute(
            select(ExternalIdentityLink).where(ExternalIdentityLink.subject == "dup")
        )
    ).scalars().all()
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

    conn2, result = await svc.handle_callback(
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
                sub="s", email=email, aud=mint_kwargs.pop("aud", "client-1"),
                nonce=mint_kwargs.pop("nonce", factory.real_nonce), **mint_kwargs
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
        await db.execute(
            select(IntegrationEvent).where(
                IntegrationEvent.org_id == org.id,
                IntegrationEvent.type == "com.openskill.org.breakglass.login.v1",
            )
        )
    ).scalars().all()
    assert len(audit) == 1


@pytest.mark.asyncio
async def test_enforce_flag_requires_break_glass_member(db):
    owner = await _user(db)
    org = await _org(db, owner)
    svc = SsoAdminService(db)
    conn = await svc.create(
        org.id, protocol="oidc", oidc_issuer=ISSUER, oidc_client_id="c"
    )
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
        org.id, protocol="oidc", oidc_issuer=ISSUER, oidc_client_id="c",
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
        await svc.resolve(
            _ident(org, subject="junk-1", email={"evil": "dict"}, verified=True)
        )
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
    assert changed == 2
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
