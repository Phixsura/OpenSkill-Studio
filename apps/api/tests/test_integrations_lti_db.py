"""P7a tests — LTI 1.3 launch validation vectors against a faked platform."""

import json
import time
import uuid
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
from app.integrations.models import LtiResourceLink, OrgDomain
from app.integrations.services.lti import LtiService
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus

ISS = "https://lms.example.edu"
CLAIM = "https://purl.imsglobal.org/spec/lti/claim/"

_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIV = _KEY.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
_JWK = json.loads(pyjwt.algorithms.RSAAlgorithm.to_jwk(_KEY.public_key()))
_JWK.update({"kid": "lms-k1", "alg": "RS256", "use": "sig"})


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    from datetime import UTC, datetime

    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    u = User(
        email=f"lt-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Lt",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=u.id, type="platform"),
        owner_user_id=u.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=u.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE))
    domain = f"lms-{uuid.uuid4().hex[:8]}.example.edu"
    db.add(
        OrgDomain(
            org_id=org.id,
            domain=domain,
            status="verified",
            verification_token="t",
            verified_at=datetime.now(UTC),
        )
    )
    await db.flush()
    _mint.domain = domain  # launch emails ride THIS org's verified domain
    return org, u


class FakePlatform:
    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        if urlsplit(url).path.endswith("/jwks"):
            return httpx.Response(
                200, json={"keys": [_JWK]}, request=httpx.Request(method, url)
            )
        return httpx.Response(404, request=httpx.Request(method, url))


async def _registration(db, org):
    svc = LtiService(db)
    reg = await svc.create_registration(
        org.id,
        issuer=ISS,
        client_id="tool-client-1",
        auth_login_url=f"{ISS}/auth",
        auth_token_url=f"{ISS}/token",
        jwks_url=f"{ISS}/jwks",
        deployment_ids=["dep-1"],
    )
    return svc, reg


def _mint(nonce, **over):
    claims = {
        "iss": ISS,
        "aud": "tool-client-1",
        "sub": "lms-user-7",
        "email": f"kid-{uuid.uuid4().hex[:6]}@{_mint.domain}",
        "name": "LMS Kid",
        "nonce": nonce,
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        f"{CLAIM}version": "1.3.0",
        f"{CLAIM}message_type": "LtiResourceLinkRequest",
        f"{CLAIM}deployment_id": "dep-1",
        f"{CLAIM}resource_link": {"id": "rl-1"},
        f"{CLAIM}roles": [],
    }
    claims.update(over)
    return pyjwt.encode(claims, _PRIV, algorithm="RS256", headers={"kid": "lms-k1"})


async def _start(svc, reg):
    url = await svc.login_initiation(
        iss=ISS,
        login_hint="u7",
        client_id="tool-client-1",
        lti_message_hint=None,
        target_link_uri="https://tool.example.com/launch",
        redirect_uri="https://tool.example.com/api/v1/lti/launch",
    )
    qs = parse_qs(urlsplit(url).query)
    assert qs["response_mode"] == ["form_post"] and qs["prompt"] == ["none"]
    return qs["state"][0], qs["nonce"][0]


@pytest.mark.asyncio
async def test_launch_happy_path_jit_and_resource_mapping(db):
    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()
    await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="skill",
        target_id="01SKILLXXXXXXXXXXXXXXXXXXX",
        grade_sync_enabled=True,
    )
    state, nonce = await _start(svc, reg)
    ags = {
        f"{CLAIM.replace('lti/claim/', 'lti-ags/claim/')}endpoint": {
            "lineitem": "https://lms.example.edu/ags/line/1"
        }
    }
    reg2, link, result, claims = await svc.handle_launch(
        state_value=state, id_token=_mint(nonce, **ags)
    )
    assert reg2.id == reg.id
    assert result.jit_created is True
    assert link is not None and link.kind == "skill"
    await db.flush()
    stored = (
        await db.execute(select(LtiResourceLink).where(LtiResourceLink.id == link.id))
    ).scalar_one()
    assert stored.ags_lineitem_url == "https://lms.example.edu/ags/line/1"
    # Same subject relaunches as the same user (no second JIT).
    state2, nonce2 = await _start(svc, reg)
    _, _, result2, _ = await svc.handle_launch(state_value=state2, id_token=_mint(nonce2))
    assert result2.user.id == result.user.id and result2.jit_created is False
    # State single-use.
    with pytest.raises(AppError):
        await svc.handle_launch(state_value=state, id_token=_mint(nonce))


@pytest.mark.asyncio
async def test_launch_rejection_vectors(db):
    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()

    async def expect_reject(code="LTI_LAUNCH_INVALID", **mint_over):
        state, nonce = await _start(svc, reg)
        token = _mint(mint_over.pop("nonce", nonce), **mint_over)
        with pytest.raises(AppError) as e:
            await svc.handle_launch(state_value=state, id_token=token)
        assert e.value.code == code

    await expect_reject(nonce="echoed-from-captured-token")  # nonce mismatch
    await expect_reject(aud="other-tool")  # audience
    await expect_reject(iss="https://rogue.example.com")  # issuer
    await expect_reject(exp=int(time.time()) - 3600)  # expired
    await expect_reject(**{f"{CLAIM}version": "1.1"})  # version
    await expect_reject(**{f"{CLAIM}message_type": "EvilMessage"})  # type
    await expect_reject(azp="other-client")  # azp
    await expect_reject(
        code="LTI_DEPLOYMENT_UNKNOWN", **{f"{CLAIM}deployment_id": "dep-ROGUE"}
    )
    # alg=none / HS256 forgery with the public key as secret
    state, nonce = await _start(svc, reg)
    forged = pyjwt.encode(
        {"iss": ISS, "aud": "tool-client-1", "sub": "x", "nonce": nonce,
         "iat": int(time.time()), "exp": int(time.time()) + 600},
        "not-a-key",
        algorithm="HS256",
        headers={"kid": "lms-k1"},
    )
    with pytest.raises(AppError):
        await svc.handle_launch(state_value=state, id_token=forged)


@pytest.mark.asyncio
async def test_ssrf_blocked_ags_lineitem_is_ignored(db):
    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()
    await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="skill",
        target_id="01SKILLXXXXXXXXXXXXXXXXXXX",
    )
    state, nonce = await _start(svc, reg)
    evil = {
        f"{CLAIM.replace('lti/claim/', 'lti-ags/claim/')}endpoint": {
            "lineitem": "https://169.254.169.254/latest/meta-data"
        }
    }
    _, link, _, _ = await svc.handle_launch(state_value=state, id_token=_mint(nonce, **evil))
    assert link is not None and link.ags_lineitem_url is None  # blocked, not stored


@pytest.mark.asyncio
async def test_registration_admin_rules(db):
    org, _ = await _org(db)
    svc = LtiService(db)
    with pytest.raises(AppError):  # private issuer blocked by egress screen
        await svc.create_registration(
            org.id,
            issuer="https://10.0.0.5",
            client_id="c",
            auth_login_url=f"{ISS}/auth",
            auth_token_url=f"{ISS}/token",
            jwks_url=f"{ISS}/jwks",
            deployment_ids=[],
        )
    with pytest.raises(AppError) as e:  # JIT ceiling
        await svc.create_registration(
            org.id,
            issuer=ISS,
            client_id="c2",
            auth_login_url=f"{ISS}/auth",
            auth_token_url=f"{ISS}/token",
            jwks_url=f"{ISS}/jwks",
            deployment_ids=[],
            default_role="owner",
        )
    assert e.value.code == "SSO_JIT_ROLE_INVALID"
    reg = await svc.create_registration(
        org.id,
        issuer=ISS,
        client_id="c3",
        auth_login_url=f"{ISS}/auth",
        auth_token_url=f"{ISS}/token",
        jwks_url=f"{ISS}/jwks",
        deployment_ids=["d1"],
    )
    with pytest.raises(AppError) as e2:  # duplicate issuer+client
        await svc.create_registration(
            org.id,
            issuer=ISS,
            client_id="c3",
            auth_login_url=f"{ISS}/auth",
            auth_token_url=f"{ISS}/token",
            jwks_url=f"{ISS}/jwks",
            deployment_ids=[],
        )
    assert e2.value.code == "LTI_REGISTRATION_EXISTS"
    # cross-tenant uniform 404
    other, _ = await _org(db)
    with pytest.raises(AppError) as e3:
        await svc.get_registration(other.id, reg.id)
    assert e3.value.status_code == 404
    # bad resource kind
    with pytest.raises(AppError):
        await svc.map_resource_link(
            org.id, reg.id, deployment_id="d1", resource_link_id="r", kind="exam", target_id="x"
        )
