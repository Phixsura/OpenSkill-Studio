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
            return httpx.Response(200, json={"keys": [_JWK]}, request=httpx.Request(method, url))
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
    await expect_reject(code="LTI_DEPLOYMENT_UNKNOWN", **{f"{CLAIM}deployment_id": "dep-ROGUE"})
    # alg=none / HS256 forgery with the public key as secret
    state, nonce = await _start(svc, reg)
    forged = pyjwt.encode(
        {
            "iss": ISS,
            "aud": "tool-client-1",
            "sub": "x",
            "nonce": nonce,
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,
        },
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


# ── R37: launch-validation probe killers ──


@pytest.mark.asyncio
async def test_launch_expired_state_inactive_reg_and_missing_exp(db):
    from datetime import UTC, datetime, timedelta

    from app.integrations.models import LtiLaunchState

    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()

    # 1. Expired state: valid token, stale row -> refused.
    state, nonce = await _start(svc, reg)
    row = await db.get(LtiLaunchState, state)
    row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await db.flush()
    with pytest.raises(AppError):
        await svc.handle_launch(state_value=state, id_token=_mint(nonce))

    # 2. Registration disabled AFTER the state was minted -> refused.
    state, nonce = await _start(svc, reg)
    reg.status = "disabled"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await svc.handle_launch(state_value=state, id_token=_mint(nonce))
    assert "registration_inactive" in exc.value.message or exc.value.code == "LTI_LAUNCH_INVALID"
    reg.status = "active"
    await db.flush()

    # 3. Token without exp -> refused (require list).
    state, nonce = await _start(svc, reg)
    # Fully launchable except for the missing exp — so ONLY the require
    # list can reject it (otherwise identity resolution would mask the hole).
    claims = {
        "iss": ISS,
        "aud": "tool-client-1",
        "sub": "lms-user-7",
        "email": f"noexp-{uuid.uuid4().hex[:6]}@{_mint.domain}",
        "name": "No Exp",
        "nonce": nonce,
        "iat": int(time.time()),
        f"{CLAIM}version": "1.3.0",
        f"{CLAIM}message_type": "LtiResourceLinkRequest",
        f"{CLAIM}deployment_id": "dep-1",
        f"{CLAIM}resource_link": {"id": "rl-1"},
        f"{CLAIM}roles": [],
    }
    token = pyjwt.encode(claims, _PRIV, algorithm="RS256", headers={"kid": "lms-k1"})
    with pytest.raises(AppError):
        await svc.handle_launch(state_value=state, id_token=token)


# ── R49: NRPS membership sync ──


@pytest.mark.asyncio
async def test_nrps_sync_provisions_members_with_pagination_and_ceiling(db):
    """Launch captures the NRPS claim; sync pre-provisions members through
    identity resolution with pagination, role mapping and the JIT ceiling."""
    import json as _json

    from app.integrations.models import IdentityMatchQueue
    from app.integrations.services.lti_ags import ensure_tool_key, tool_jwks
    from app.integrations.services.lti_nrps import sync_memberships

    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()
    await ensure_tool_key(db)
    jwks = await tool_jwks(db)

    # Launch with the NRPS claim: link captures the membership URL.
    link = await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="skill",
        target_id="SKILL1",
    )
    state, nonce = await _start(svc, reg)
    nrps_claim = {
        "context_memberships_url": "https://lms.example.com/api/nrps/ctx-1",
        "service_versions": ["2.0"],
    }
    token = _mint(
        nonce,
        **{"https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice": nrps_claim},
    )
    await svc.handle_launch(state_value=state, id_token=token)
    await db.flush()
    assert link.nrps_url == "https://lms.example.com/api/nrps/ctx-1"

    # Fake platform: token endpoint verifies our assertion; two NRPS pages.
    page2_url = "https://lms.example.com/api/nrps/ctx-1?page=2"
    m1 = {
        "user_id": "stu-1",
        "status": "Active",
        "email": f"n1@{_mint.domain}",
        "name": "N One",
        "roles": ["http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"],
    }
    m2 = {
        "user_id": "teach-1",
        "status": "Active",
        "email": f"n2@{_mint.domain}",
        "name": "N Two",
        "roles": ["http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"],
    }
    m3 = {"user_id": "gone-1", "status": "Deleted", "email": f"n3@{_mint.domain}", "roles": []}
    m4 = {"user_id": "noemail-1", "status": "Active", "roles": []}

    class NrpsPlatform:
        def __init__(self):
            self.calls = []

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            self.calls.append(url)
            path = urlsplit(url).path
            if path.endswith("/token"):
                return httpx.Response(
                    200,
                    json={"access_token": "nrps-tok"},
                    request=httpx.Request(method, url),
                )
            assert headers["authorization"] == "Bearer nrps-tok"
            assert "membershipcontainer" in headers["accept"]
            if "page=2" in url:
                return httpx.Response(
                    200,
                    json={"members": [m2, m3, m4]},
                    request=httpx.Request(method, url),
                )
            return httpx.Response(
                200,
                json={"members": [m1]},
                headers={"link": f'<{page2_url}>; rel="next"'},
                request=httpx.Request(method, url),
            )

    platform = NrpsPlatform()
    report = await sync_memberships(db, org.id, link.id, egress=platform)
    assert report["read"] == 4
    assert report["resolved"] == 2 and report["jit_created"] == 2
    assert report["skipped"] == 1  # deleted member
    assert report["queued"] == 1  # no email -> admin queue
    assert _json is not None and jwks is not None

    # Instructor got the instructor role; learner got student.
    from sqlalchemy import func as _f

    from app.models.organization import OrgMember as MemberModel
    from app.models.user import User as UserModel

    teach = (
        await db.execute(
            select(MemberModel.role)
            .join(UserModel, UserModel.id == MemberModel.user_id)
            .where(
                MemberModel.org_id == org.id,
                _f.lower(UserModel.email) == f"n2@{_mint.domain}".lower(),
            )
        )
    ).scalar_one()
    assert teach.value == "instructor"
    # R244 (survivor pin): the NON-instructor member must get the
    # registration's default role — a mutant minting instructor for everyone
    # (privilege escalation) previously survived because only the positive
    # instructor assertion existed.
    stud = (
        await db.execute(
            select(MemberModel.role)
            .join(UserModel, UserModel.id == MemberModel.user_id)
            .where(
                MemberModel.org_id == org.id,
                _f.lower(UserModel.email) == f"n1@{_mint.domain}".lower(),
            )
        )
    ).scalar_one()
    assert stud.value == "student"
    q = (
        (
            await db.execute(
                select(IdentityMatchQueue).where(
                    IdentityMatchQueue.org_id == org.id,
                    IdentityMatchQueue.subject == f"{ISS}|noemail-1",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(q) == 1

    # Second sync: everyone linked -> resolved, nothing new.
    report2 = await sync_memberships(db, org.id, link.id, egress=platform)
    assert report2["jit_created"] == 0 and report2["resolved"] == 2

    # Cross-org: uniform 404.
    org2, _ = await _org(db)
    with pytest.raises(AppError) as exc:
        await sync_memberships(db, org2.id, link.id, egress=platform)
    assert exc.value.status_code == 404

    # Inactive registration refuses sync.
    reg.status = "disabled"
    await db.flush()
    with pytest.raises(AppError) as exc_inactive:
        await sync_memberships(db, org.id, link.id, egress=platform)
    assert exc_inactive.value.code == "LTI_REGISTRATION_INACTIVE"
    reg.status = "active"
    await db.flush()

    # Token refused -> 502, not a silent empty sync.
    class NoTokenPlatform(NrpsPlatform):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/token"):
                return httpx.Response(401, request=httpx.Request(method, url))
            return await super().request(
                method, url, headers=headers, content=content, read_timeout=read_timeout
            )

    with pytest.raises(AppError) as exc_tok:
        await sync_memberships(db, org.id, link.id, egress=NoTokenPlatform())
    assert exc_tok.value.code == "LTI_NRPS_TOKEN_REFUSED"

    # Data endpoint 401 (expired token mid-walk) -> 502 class too.
    class Auth401Platform(NrpsPlatform):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/token"):
                return httpx.Response(
                    200, json={"access_token": "t"}, request=httpx.Request(method, url)
                )
            return httpx.Response(401, request=httpx.Request(method, url))

    with pytest.raises(AppError) as exc_401:
        await sync_memberships(db, org.id, link.id, egress=Auth401Platform())
    assert exc_401.value.code == "LTI_NRPS_TOKEN_REFUSED"

    # Malicious next-link to a private address is refused (platform data is
    # screened); and an endless next-link chain stops at the page cap.
    class EvilNextPlatform(NrpsPlatform):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/token"):
                return httpx.Response(
                    200, json={"access_token": "t"}, request=httpx.Request(method, url)
                )
            return httpx.Response(
                200,
                json={"members": []},
                headers={"link": '<https://169.254.169.254/x>; rel="next"'},
                request=httpx.Request(method, url),
            )

    from app.integrations.security import EgressBlockedError

    with pytest.raises(EgressBlockedError):
        await sync_memberships(db, org.id, link.id, egress=EvilNextPlatform())

    class LoopPlatform(NrpsPlatform):
        def __init__(self):
            super().__init__()
            self.data_calls = 0

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/token"):
                return httpx.Response(
                    200, json={"access_token": "t"}, request=httpx.Request(method, url)
                )
            self.data_calls += 1
            return httpx.Response(
                200,
                json={"members": []},
                headers={"link": '<https://lms.example.com/api/nrps/ctx-1?loop=1>; rel="next"'},
                request=httpx.Request(method, url),
            )

    loop = LoopPlatform()
    await sync_memberships(db, org.id, link.id, egress=loop)
    assert loop.data_calls == 25  # _MAX_PAGES cap, not unbounded

    # No NRPS URL -> explicit 422 with guidance.
    link2 = await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-2",
        kind="skill",
        target_id="SKILL2",
    )
    with pytest.raises(AppError) as exc2:
        await sync_memberships(db, org.id, link2.id, egress=platform)
    assert exc2.value.code == "LTI_NRPS_UNAVAILABLE"


# ── R87: Dynamic Registration ──


@pytest.mark.asyncio
async def test_dynamic_registration_full_flow_and_screens(db):
    import json as _json

    from app.integrations.services.lti_dynreg import (
        PLATFORM_CONFIG_CLAIM,
        TOOL_CONFIG_CLAIM,
        dynamic_register,
    )

    org, owner = await _org(db)
    iss = f"https://lms-{uuid.uuid4().hex[:6]}.example.com"
    config = {
        "issuer": iss,
        "authorization_endpoint": f"{iss}/auth",
        "token_endpoint": f"{iss}/token",
        "jwks_uri": f"{iss}/jwks",
        "registration_endpoint": f"{iss}/register",
        PLATFORM_CONFIG_CLAIM: {"product_family_code": "moodle"},
    }

    class FakePlatform:
        def __init__(self, cfg):
            self.cfg = cfg
            self.registration_body = None
            self.auth_header = None

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            path = urlsplit(url).path
            if path.endswith("/.well-known/openid-configuration"):
                return httpx.Response(200, json=self.cfg, request=httpx.Request(method, url))
            if path.endswith("/register"):
                self.registration_body = _json.loads(content)
                self.auth_header = (headers or {}).get("authorization")
                return httpx.Response(
                    201,
                    json={
                        "client_id": "dyn-client-9",
                        TOOL_CONFIG_CLAIM: {"deployment_ids": ["dep-A", "dep-B"]},
                    },
                    request=httpx.Request(method, url),
                )
            return httpx.Response(404, request=httpx.Request(method, url))

    platform = FakePlatform(config)
    reg = await dynamic_register(
        db,
        org.id,
        openid_configuration_url=f"{iss}/.well-known/openid-configuration",
        registration_token="one-time-tok",
        egress=platform,
    )
    assert reg.client_id == "dyn-client-9" and reg.issuer == iss
    assert platform.auth_header == "Bearer one-time-tok"
    sent = platform.registration_body
    assert sent["token_endpoint_auth_method"] == "private_key_jwt"
    assert sent["jwks_uri"].endswith("/api/v1/lti/jwks")
    msg_types = {m["type"] for m in sent[TOOL_CONFIG_CLAIM]["messages"]}
    assert msg_types == {"LtiResourceLinkRequest", "LtiDeepLinkingRequest"}
    from sqlalchemy import select as _select

    from app.integrations.models import LtiDeployment

    deps = (
        (
            await db.execute(
                _select(LtiDeployment.deployment_id).where(LtiDeployment.registration_id == reg.id)
            )
        )
        .scalars()
        .all()
    )
    assert sorted(deps) == ["dep-A", "dep-B"]

    # Missing required key (token_endpoint) -> CONFIG_INVALID.
    broken = dict(config)
    broken.pop("token_endpoint")
    broken["issuer"] = f"{iss}/t-broken"
    with pytest.raises(AppError) as e_missing:
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{iss}/.well-known/openid-configuration",
            registration_token=None,
            egress=FakePlatform(broken),
        )
    assert e_missing.value.code == "LTI_DYNREG_CONFIG_INVALID"

    # 201 with an empty JSON body (no client_id) -> REFUSED, not a DB error.
    class EmptyBody(FakePlatform):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/register"):
                return httpx.Response(201, json={}, request=httpx.Request(method, url))
            return await super().request(
                method, url, headers=headers, content=content, read_timeout=read_timeout
            )

    eb_cfg = dict(config)
    eb_cfg["issuer"] = f"{iss}/t-eb"
    with pytest.raises(AppError) as e_empty:
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{iss}/.well-known/openid-configuration",
            registration_token=None,
            egress=EmptyBody(eb_cfg),
        )
    assert e_empty.value.code == "LTI_DYNREG_REFUSED"

    # Plain OIDC server (no platform claim) refused.
    bare = dict(config)
    bare.pop(PLATFORM_CONFIG_CLAIM)
    bare["issuer"] = f"{iss}/t-bare"
    with pytest.raises(AppError) as e1:
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{iss}/.well-known/openid-configuration",
            registration_token=None,
            egress=FakePlatform(bare),
        )
    assert e1.value.code == "LTI_DYNREG_CONFIG_INVALID"

    # Private registration_endpoint refused by the egress screen.
    evil = dict(config)
    evil["issuer"] = f"{iss}-evil"
    evil["registration_endpoint"] = "https://169.254.169.254/register"
    from app.integrations.security import EgressBlockedError

    with pytest.raises(EgressBlockedError):
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{iss}/.well-known/openid-configuration",
            registration_token=None,
            egress=FakePlatform(evil),
        )

    # Platform refusal (403) surfaces as 502-class, not a crash.
    class Refusing(FakePlatform):
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/register"):
                return httpx.Response(403, request=httpx.Request(method, url))
            return await super().request(
                method, url, headers=headers, content=content, read_timeout=read_timeout
            )

    ref_cfg = dict(config)
    ref_cfg["issuer"] = f"{iss}/t-ref"
    with pytest.raises(AppError) as e2:
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{iss}/.well-known/openid-configuration",
            registration_token="t",
            egress=Refusing(ref_cfg),
        )
    assert e2.value.code == "LTI_DYNREG_REFUSED"


@pytest.mark.asyncio
async def test_deep_link_data_round_trips_verbatim(db):
    """R248 (survivor pin): the platform's opaque `data` from the deep-link
    request MUST round-trip into the response JWT verbatim (LTI-DL 2.0);
    omitted when the request carried none."""
    import jwt as _pyjwt

    from app.integrations.services.lti_ags import DL_CLAIM, sign_deep_linking_response

    org, owner = await _org(db)
    _svc, reg = await _registration(db, org)
    token = await sign_deep_linking_response(
        db, reg, deployment_id="dep-1", content_items=[], data="opaque-state-123"
    )
    claims = _pyjwt.decode(token, options={"verify_signature": False})
    assert claims[f"{DL_CLAIM}data"] == "opaque-state-123"
    token2 = await sign_deep_linking_response(
        db, reg, deployment_id="dep-1", content_items=[], data=None
    )
    claims2 = _pyjwt.decode(token2, options={"verify_signature": False})
    assert f"{DL_CLAIM}data" not in claims2


@pytest.mark.asyncio
async def test_dynreg_rejects_cross_origin_issuer(db):
    """R253 (R251/R252 class): a configuration document whose issuer lives on
    a DIFFERENT origin than the admin-pasted configuration URL is registering
    us against another platform — refuse before posting the registration."""
    from app.integrations.services.lti_dynreg import PLATFORM_CONFIG_CLAIM, dynamic_register

    org, owner = await _org(db)
    lms = f"https://lms-{uuid.uuid4().hex[:6]}.example.com"
    evil = "https://other-platform.example.net"
    config = {
        "issuer": evil,
        "authorization_endpoint": f"{evil}/auth",
        "token_endpoint": f"{evil}/token",
        "jwks_uri": f"{evil}/jwks",
        "registration_endpoint": f"{evil}/register",
        PLATFORM_CONFIG_CLAIM: {"product_family_code": "x"},
    }

    class Fake:
        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            return httpx.Response(200, json=config, request=httpx.Request(method, url))

    with pytest.raises(AppError) as e:
        await dynamic_register(
            db,
            org.id,
            openid_configuration_url=f"{lms}/.well-known/openid-configuration",
            registration_token=None,
            egress=Fake(),
        )
    assert e.value.code == "LTI_DYNREG_CONFIG_INVALID"


@pytest.mark.asyncio
async def test_lti_registration_caps(db):
    """R263 (R262 class): per-org registration cap + per-request
    deployment_ids bound, both with stable error codes."""
    from app.integrations.services.lti import (
        MAX_DEPLOYMENTS_PER_REGISTRATION,
        MAX_LTI_REGISTRATIONS_PER_ORG,
    )

    org, owner = await _org(db)
    svc = LtiService(db)
    for i in range(MAX_LTI_REGISTRATIONS_PER_ORG):
        await svc.create_registration(
            org.id,
            issuer=f"https://lms{i}.example.com",
            client_id="c1",
            auth_login_url=f"https://lms{i}.example.com/auth",
            auth_token_url=f"https://lms{i}.example.com/token",
            jwks_url=f"https://lms{i}.example.com/jwks",
            deployment_ids=["d1"],
        )
    with pytest.raises(AppError) as e:
        await svc.create_registration(
            org.id,
            issuer="https://lms-over.example.com",
            client_id="c1",
            auth_login_url="https://lms-over.example.com/auth",
            auth_token_url="https://lms-over.example.com/token",
            jwks_url="https://lms-over.example.com/jwks",
            deployment_ids=["d1"],
        )
    assert e.value.code == "LTI_REGISTRATION_LIMIT_REACHED"

    org2, _owner2 = await _org(db)
    with pytest.raises(AppError) as e:
        await LtiService(db).create_registration(
            org2.id,
            issuer="https://lms-dep.example.com",
            client_id="c1",
            auth_login_url="https://lms-dep.example.com/auth",
            auth_token_url="https://lms-dep.example.com/token",
            jwks_url="https://lms-dep.example.com/jwks",
            deployment_ids=[f"d{i}" for i in range(MAX_DEPLOYMENTS_PER_REGISTRATION + 1)],
        )
    assert e.value.code == "LTI_REGISTRATION_INVALID"


@pytest.mark.asyncio
async def test_service_token_private_key_jwt_shape(db):
    """R326 (spec-conformance pin): the client_credentials grant sends a
    private_key_jwt whose claims the platform actually validates —
    iss=sub=client_id, aud=token URL, fresh jti, bounded exp, RS256 signed
    by the ACTIVE tool key (kid in header, verifiable against /lti/jwks).
    A drift here fails every AGS/NRPS call at real LMSes with opaque 401s."""
    from urllib.parse import parse_qs

    import jwt as pyjwt

    from app.integrations.services.lti_ags import service_token, tool_jwks

    org, owner = await _org(db)
    _svc, reg = await _registration(db, org)

    seen = {}

    class _Egress:
        async def request(self, method, url, headers=None, content=None, **kw):
            seen["url"] = url
            seen["form"] = parse_qs((content or b"").decode())
            return httpx.Response(
                200,
                json={"access_token": "at-1"},
                request=httpx.Request(method, url),
            )

    token = await service_token(
        db, reg, _Egress(), scope="https://purl.imsglobal.org/spec/lti-ags/scope/score"
    )
    assert token == "at-1"
    assert seen["url"] == reg.auth_token_url
    form = seen["form"]
    assert form["grant_type"] == ["client_credentials"]
    assert form["client_assertion_type"] == [
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]
    assert form["scope"] == ["https://purl.imsglobal.org/spec/lti-ags/scope/score"]

    assertion = form["client_assertion"][0]
    header = pyjwt.get_unverified_header(assertion)
    assert header["alg"] == "RS256" and header.get("kid")
    # verify against OUR advertised jwks (the platform does exactly this)
    jwks = await tool_jwks(db)
    jwk = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
    pub = pyjwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    claims = pyjwt.decode(assertion, key=pub, algorithms=["RS256"], audience=reg.auth_token_url)
    assert claims["iss"] == reg.client_id
    assert claims["sub"] == reg.client_id
    assert claims["jti"] and len(claims["jti"]) >= 16
    assert 0 < claims["exp"] - claims["iat"] <= 300


class _FakeAgsEgress:
    """Captures the AGS score POST; returns the configured status."""

    def __init__(self, status=200):
        self.status = status
        self.calls: list[dict] = []

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        import json as _json

        self.calls.append({"method": method, "url": url, "body": _json.loads(content)})

        class _R:
            status_code = self.status

        return _R()


async def test_ags_push_score_cycle(db, monkeypatch):
    """R412: AGS grade-passback (push_score → the LMS /scores endpoint) was
    uncovered — a shipped outbound WRITE path. Launch to JIT a mapped user,
    then exercise push_score: a grade-sync-disabled link returns False
    without a call, a user who never launched returns False, the happy path
    POSTs a well-formed AGS Score to <lineitem>/scores and returns True,
    and an LMS refusal (4xx) returns False."""
    from app.integrations.models import LtiResourceLink
    from app.integrations.services import lti_ags

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
    _, link, result, _ = await svc.handle_launch(state_value=state, id_token=_mint(nonce, **ags))
    await db.flush()
    link = (
        await db.execute(select(LtiResourceLink).where(LtiResourceLink.id == link.id))
    ).scalar_one()
    user_id = result.user.id

    # _ags_token does a real client-credentials exchange — stub it.
    async def _tok(_db, _reg, _egress):
        return "ags-access-token"

    monkeypatch.setattr(lti_ags, "_ags_token", _tok)

    # happy path
    eg = _FakeAgsEgress(status=200)
    ok = await lti_ags.push_score(db, link, user_id=user_id, score_given=87.5, egress=eg)
    assert ok is True
    assert len(eg.calls) == 1
    call = eg.calls[0]
    assert call["url"] == "https://lms.example.edu/ags/line/1/scores"
    assert call["body"]["scoreGiven"] == 87.5
    assert call["body"]["gradingProgress"] == "FullyGraded"

    # LMS refuses
    eg_bad = _FakeAgsEgress(status=403)
    assert (
        await lti_ags.push_score(db, link, user_id=user_id, score_given=50.0, egress=eg_bad)
        is False
    )

    # user who never launched this LMS -> no subject -> False, no POST
    eg_none = _FakeAgsEgress(status=200)
    other = User(
        email=f"never-{uuid.uuid4().hex[:10]}@x.edu",
        password_hash=hash_password("Test123!"),
        display_name="Never",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(other)
    await db.flush()
    assert (
        await lti_ags.push_score(db, link, user_id=other.id, score_given=10.0, egress=eg_none)
        is False
    )
    assert eg_none.calls == []

    # grade-sync disabled -> False, no token/POST
    link.grade_sync_enabled = False
    await db.flush()
    eg_off = _FakeAgsEgress(status=200)
    assert (
        await lti_ags.push_score(db, link, user_id=user_id, score_given=99.0, egress=eg_off)
        is False
    )
    assert eg_off.calls == []


async def test_handle_gradeable_event_fanout_and_score_clamp(db, monkeypatch):
    """R413: the worker hook that turns an internal gradeable event into AGS
    pushes (handle_gradeable_event) was uncovered — it is the automation
    that makes grade-passback actually fire. Cover: unknown event type -> 0,
    missing target/user -> 0, a matched grade-enabled link -> one push with
    the score clamped into [0,100], and a non-numeric score -> 0.0."""
    from types import SimpleNamespace

    from app.integrations.services import lti_ags

    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    svc.egress = FakePlatform()
    skill_target = "01SKILLXXXXXXXXXXXXXXXXXXX"
    await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="skill",
        target_id=skill_target,
        grade_sync_enabled=True,
    )
    state, nonce = await _start(svc, reg)
    ags = {
        f"{CLAIM.replace('lti/claim/', 'lti-ags/claim/')}endpoint": {
            "lineitem": "https://lms.example.edu/ags/line/1"
        }
    }
    _, _link, result, _ = await svc.handle_launch(state_value=state, id_token=_mint(nonce, **ags))
    await db.flush()
    uid = result.user.id

    pushes: list[dict] = []

    async def _fake_push(_db, link, *, user_id, score_given, score_maximum=100.0, egress=None):
        pushes.append({"link": link.id, "user_id": user_id, "score": score_given})
        return True

    monkeypatch.setattr(lti_ags, "push_score", _fake_push)

    def ev(etype, data):
        return SimpleNamespace(type=etype, data=data, org_id=org.id)

    # unknown event type
    assert await lti_ags.handle_gradeable_event(db, ev("com.openskill.unknown.v1", {})) == 0
    # missing user/target
    assert (
        await lti_ags.handle_gradeable_event(
            db, ev("com.openskill.skill.completed.v1", {"skill_id": skill_target})
        )
        == 0
    )
    assert not pushes

    # matched skill.completed (no score_key -> defaults to 100)
    n = await lti_ags.handle_gradeable_event(
        db, ev("com.openskill.skill.completed.v1", {"skill_id": skill_target, "user_id": uid})
    )
    assert n == 1 and pushes[-1]["score"] == 100.0 and pushes[-1]["user_id"] == uid

    # project.approved with an over-range final_score -> clamped to 100
    await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-proj",
        kind="project",
        target_id="proj-9",
        grade_sync_enabled=True,
    )
    # the project link needs an AGS lineitem to be selected — relaunch sets it
    # per resource_link; instead set it directly for this unit.
    from app.integrations.models import LtiResourceLink

    plink = (
        await db.execute(
            select(LtiResourceLink).where(LtiResourceLink.resource_link_id == "rl-proj")
        )
    ).scalar_one()
    plink.ags_lineitem_url = "https://lms.example.edu/ags/line/2"
    await db.flush()
    pushes.clear()
    n = await lti_ags.handle_gradeable_event(
        db,
        ev(
            "com.openskill.project.approved.v1",
            {"project_id": "proj-9", "user_id": uid, "final_score": 150},
        ),
    )
    assert n == 1 and pushes[-1]["score"] == 100.0  # clamped

    # non-numeric score -> 0.0
    pushes.clear()
    n = await lti_ags.handle_gradeable_event(
        db,
        ev(
            "com.openskill.project.approved.v1",
            {"project_id": "proj-9", "user_id": uid, "final_score": "A+"},
        ),
    )
    assert n == 1 and pushes[-1]["score"] == 0.0


@pytest.mark.asyncio
async def test_map_resource_link_update_in_place(db):
    """R431: map_resource_link's update-in-place arm (same reg+deployment+
    resource_link_id re-mapped) had never executed — only the create arm and
    the bad-kind reject. Re-mapping must mutate the existing row (kind,
    target, grade_sync), not insert a duplicate."""
    org, owner = await _org(db)
    svc, reg = await _registration(db, org)

    first = await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-upd",
        kind="skill",
        target_id="SKILL_A",
        grade_sync_enabled=False,
    )
    second = await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-upd",
        kind="project",
        target_id="PROJ_B",
        grade_sync_enabled=True,
    )
    assert second.id == first.id  # same row, updated in place
    assert second.kind == "project" and second.target_id == "PROJ_B"
    assert second.grade_sync_enabled is True


@pytest.mark.asyncio
async def test_nrps_sync_fetch_and_member_shape_arms(db):
    """R434: sync_memberships's data-fetch and member-shape arms. The
    membership GET returning 401 or any non-200 -> 502; a non-JSON body ->
    502; members not being a list -> 502; a member that isn't a dict is
    skipped (continue); and a member whose computed JIT role is invalid is
    counted as skipped, not fatal."""
    from app.integrations.services.lti_ags import ensure_tool_key
    from app.integrations.services.lti_nrps import sync_memberships

    org, owner = await _org(db)
    svc, reg = await _registration(db, org)
    await ensure_tool_key(db)
    link = await svc.map_resource_link(
        org.id, reg.id, deployment_id="dep-1", resource_link_id="rl-n", kind="skill",
        target_id="S1",
    )
    link.nrps_url = "https://lms.example.com/api/nrps/ctx-x"
    await db.flush()

    class TokenOk:
        """Token endpoint always succeeds; the membership GET is overridable."""

        def __init__(self, membership):
            self.membership = membership

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            if urlsplit(url).path.endswith("/token"):
                return httpx.Response(
                    200, json={"access_token": "nrps-tok"}, request=httpx.Request(method, url)
                )
            return self.membership(method, url)

    def r(status, *, json_body=None, text=None):
        def make(method, url):
            req = httpx.Request(method, url)
            if json_body is not None:
                return httpx.Response(status, json=json_body, request=req)
            return httpx.Response(status, text=text or "", request=req)

        return make

    async def expect(code, membership):
        with pytest.raises(AppError) as e:
            await sync_memberships(db, org.id, link.id, egress=TokenOk(membership))
        assert e.value.code == code

    await expect("LTI_NRPS_TOKEN_REFUSED", r(401))
    await expect("LTI_NRPS_FETCH_FAILED", r(503))
    await expect("LTI_NRPS_FETCH_FAILED", r(200, text="<<not json>>"))
    await expect("LTI_NRPS_FETCH_FAILED", r(200, json_body={"members": "nope"}))

    # A non-dict member entry is skipped; the sync still succeeds overall.
    report = await sync_memberships(
        db, org.id, link.id, egress=TokenOk(r(200, json_body={"members": ["not-a-dict", 42]}))
    )
    assert report["read"] == 0 and report["skipped"] == 0  # non-dicts never counted as read

    # An invalid default JIT role makes every learner's mint invalid -> skipped.
    reg.default_role = "superadmin"  # not in JIT_ALLOWED_ROLES
    await db.flush()
    member = {"user_id": "u-1", "status": "Active", "email": f"x@{_mint.domain}", "roles": []}
    report2 = await sync_memberships(
        db, org.id, link.id, egress=TokenOk(r(200, json_body={"members": [member]}))
    )
    assert report2["read"] == 1 and report2["skipped"] == 1 and report2["resolved"] == 0


@pytest.mark.asyncio
async def test_dynamic_register_fetch_and_response_shape_arms(db):
    """R439: dynamic_register's remaining fetch/shape arms. Config GET non-200
    -> 502; config body not JSON -> 502; registration response not JSON ->
    502; and a registration response with no client_id -> 502. None crash."""
    from app.integrations.services.lti_dynreg import (
        PLATFORM_CONFIG_CLAIM,
        dynamic_register,
    )

    org, owner = await _org(db)
    iss = f"https://lms-{uuid.uuid4().hex[:6]}.example.com"
    cfg = {
        "issuer": iss,
        "authorization_endpoint": f"{iss}/auth",
        "token_endpoint": f"{iss}/token",
        "jwks_uri": f"{iss}/jwks",
        "registration_endpoint": f"{iss}/register",
        PLATFORM_CONFIG_CLAIM: {"product_family_code": "moodle"},
    }
    cfg_url = f"{iss}/.well-known/openid-configuration"

    class Platform:
        def __init__(self, *, config_resp, register_resp=None):
            self.config_resp = config_resp
            self.register_resp = register_resp

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            req = httpx.Request(method, url)
            if urlsplit(url).path.endswith("/.well-known/openid-configuration"):
                return self.config_resp(req)
            if urlsplit(url).path.endswith("/register"):
                return self.register_resp(req)
            return httpx.Response(404, request=req)

    async def expect(code, platform):
        with pytest.raises(AppError) as e:
            await dynamic_register(
                db, org.id, openid_configuration_url=cfg_url,
                registration_token=None, egress=platform,
            )
        assert e.value.code == code

    # Config GET non-200.
    await expect("LTI_DYNREG_CONFIG_FAILED", Platform(config_resp=lambda r: httpx.Response(503, request=r)))
    # Config not JSON.
    await expect(
        "LTI_DYNREG_CONFIG_FAILED",
        Platform(config_resp=lambda r: httpx.Response(200, text="<<not json>>", request=r)),
    )
    # Registration response not JSON.
    await expect(
        "LTI_DYNREG_REFUSED",
        Platform(
            config_resp=lambda r: httpx.Response(200, json=cfg, request=r),
            register_resp=lambda r: httpx.Response(201, text="nope", request=r),
        ),
    )
    # Registration response with no client_id.
    await expect(
        "LTI_DYNREG_REFUSED",
        Platform(
            config_resp=lambda r: httpx.Response(200, json=cfg, request=r),
            register_resp=lambda r: httpx.Response(201, json={"not_client_id": "x"}, request=r),
        ),
    )


@pytest.mark.asyncio
async def test_login_initiation_unknown_issuer_and_message_hint(db):
    """R440: login_initiation's unknown-issuer reject and the optional
    lti_message_hint passthrough branch."""
    from urllib.parse import parse_qs, urlsplit

    org, owner = await _org(db)
    svc, reg = await _registration(db, org)

    # Unknown issuer -> invalid (no registration).
    with pytest.raises(AppError) as e:
        await svc.login_initiation(
            iss="https://not-registered.example.com",
            login_hint="u",
            client_id=None,
            lti_message_hint=None,
            target_link_uri="https://tool.example.com/launch",
            redirect_uri="https://tool.example.com/api/v1/lti/launch",
        )
    assert e.value.code == "LTI_LAUNCH_INVALID"

    # lti_message_hint present -> echoed into the authorize params.
    url = await svc.login_initiation(
        iss=ISS,
        login_hint="u7",
        client_id="tool-client-1",
        lti_message_hint="deep-link-123",
        target_link_uri="https://tool.example.com/launch",
        redirect_uri="https://tool.example.com/api/v1/lti/launch",
    )
    qs = parse_qs(urlsplit(url).query)
    assert qs["lti_message_hint"] == ["deep-link-123"]
