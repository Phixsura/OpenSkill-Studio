"""P7b tests — tool keys, client assertions, AGS score push, event hook."""

import json
import uuid
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt as pyjwt
import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.integrations.models import (
    ExternalIdentityLink,
    IntegrationEvent,
    LtiToolKey,
)
from app.integrations.services.lti import LtiService
from app.integrations.services.lti_ags import (
    ensure_tool_key,
    handle_gradeable_event,
    push_score,
    tool_jwks,
)
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus

ISS = "https://lms.example.edu"


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    u = User(
        email=f"ag-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Ag",
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
    await db.flush()
    return org, u


class FakeAgsPlatform:
    """Verifies the tool's client assertion against the tool's OWN JWKS,
    hands out a token, and records score posts."""

    def __init__(self, jwks):
        self.jwks = jwks
        self.scores = []
        self.assertion_claims = None

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        path = urlsplit(url).path
        if path.endswith("/token"):
            form = parse_qs((content or b"").decode())
            assertion = form["client_assertion"][0]
            header = pyjwt.get_unverified_header(assertion)
            key = next(
                pyjwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(k))
                for k in self.jwks["keys"]
                if k["kid"] == header["kid"]
            )
            self.assertion_claims = pyjwt.decode(
                assertion,
                key=key,
                algorithms=["RS256"],
                audience=f"{ISS}/token",
                options={"require": ["exp", "iat", "jti", "iss", "sub"]},
            )
            return httpx.Response(
                200, json={"access_token": "ags-tok"}, request=httpx.Request(method, url)
            )
        if path.endswith("/scores"):
            assert headers["authorization"] == "Bearer ags-tok"
            self.scores.append(json.loads(content))
            return httpx.Response(200, json={}, request=httpx.Request(method, url))
        return httpx.Response(404, request=httpx.Request(method, url))


async def _setup(db, org, user):
    svc = LtiService(db)
    reg = await svc.create_registration(
        org.id,
        issuer=ISS,
        client_id="tool-1",
        auth_login_url=f"{ISS}/auth",
        auth_token_url=f"{ISS}/token",
        jwks_url=f"{ISS}/jwks",
        deployment_ids=["dep-1"],
    )
    link = await svc.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="project",
        target_id="01PROJXXXXXXXXXXXXXXXXXXXX",
        grade_sync_enabled=True,
    )
    link.ags_lineitem_url = f"{ISS}/ags/lineitems/7"
    # The user launched once: link subject iss|sub exists.
    db.add(
        ExternalIdentityLink(
            org_id=org.id,
            user_id=user.id,
            source="lti",
            connection_ref=reg.id,
            subject=f"{ISS}|lms-user-42",
        )
    )
    await db.flush()
    return reg, link


@pytest.mark.asyncio
async def test_tool_key_singleton_and_jwks(db):
    k1 = await ensure_tool_key(db)
    k2 = await ensure_tool_key(db)
    assert k1.id == k2.id  # singleton per environment
    jwks = await tool_jwks(db)
    assert jwks["keys"][0]["kid"] == k1.kid
    assert jwks["keys"][0]["kty"] == "RSA"
    # private pem never in the public row
    assert "pem" not in json.dumps(jwks)
    stored = (await db.execute(select(LtiToolKey))).scalars().first()
    assert "BEGIN PRIVATE KEY" not in stored.private_pem_ct  # encrypted


@pytest.mark.asyncio
async def test_push_score_full_flow(db):
    org, user = await _org(db)
    reg, link = await _setup(db, org, user)
    jwks = await tool_jwks(db) if (await ensure_tool_key(db)) else None
    jwks = await tool_jwks(db)
    platform = FakeAgsPlatform(jwks)
    ok = await push_score(db, link, user_id=user.id, score_given=92.5, egress=platform)
    assert ok is True
    # Platform verified our assertion (signature + aud + iss/sub = client id).
    assert platform.assertion_claims["iss"] == "tool-1"
    assert platform.assertion_claims["sub"] == "tool-1"
    score = platform.scores[0]
    assert score["userId"] == "lms-user-42"  # LMS sub, not our ULID
    assert score["scoreGiven"] == 92.5 and score["scoreMaximum"] == 100.0
    assert score["gradingProgress"] == "FullyGraded"


@pytest.mark.asyncio
async def test_push_score_guards(db):
    org, user = await _org(db)
    reg, link = await _setup(db, org, user)
    jwks = await tool_jwks(db)
    platform = FakeAgsPlatform(jwks)
    # disabled link -> no push
    link.grade_sync_enabled = False
    assert await push_score(db, link, user_id=user.id, score_given=1, egress=platform) is False
    link.grade_sync_enabled = True
    # user who never launched -> no push (nothing to grade)
    stranger = User(
        email=f"s-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="S",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(stranger)
    await db.flush()
    assert await push_score(db, link, user_id=stranger.id, score_given=1, egress=platform) is False
    assert platform.scores == []


@pytest.mark.asyncio
async def test_gradeable_event_hook_pushes_clamped_score(db, monkeypatch):
    org, user = await _org(db)
    reg, link = await _setup(db, org, user)
    jwks = await tool_jwks(db)
    platform = FakeAgsPlatform(jwks)
    import app.integrations.services.lti_ags as mod

    monkeypatch.setattr(mod, "EgressClient", lambda: platform)

    event = IntegrationEvent(
        org_id=org.id,
        type="com.openskill.project.approved.v1",
        source=f"/orgs/{org.id}",
        subject="sub-1",
        data={
            "submission_id": "s1",
            "project_id": "01PROJXXXXXXXXXXXXXXXXXXXX",
            "user_id": user.id,
            "final_score": 150,  # out-of-range -> clamped
        },
    )
    db.add(event)
    await db.flush()
    pushed = await handle_gradeable_event(db, event)
    assert pushed == 1
    assert platform.scores[0]["scoreGiven"] == 100.0  # clamped
    # Non-gradeable types no-op.
    event2 = IntegrationEvent(
        org_id=org.id,
        type="com.openskill.brief.created.v1",
        source=f"/orgs/{org.id}",
        data={},
    )
    db.add(event2)
    await db.flush()
    assert await handle_gradeable_event(db, event2) == 0


@pytest.mark.asyncio
async def test_jwks_endpoint(client):
    resp = await client.get("/api/v1/lti/jwks")
    assert resp.status_code == 200
    # Without DB (noop lifespan) this may 500 in other suites; here the DB is
    # up, so the shape must be a JWKS document.
    body = resp.json()
    assert "keys" in body and body["keys"][0]["kty"] == "RSA"
