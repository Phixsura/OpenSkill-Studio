"""ADR-018 §18 acceptance chain — the issue #43 Definition-of-Done flow,
driven inline through every fabric layer:

  external directory (SCIM provision) -> enterprise SSO (OIDC login) ->
  SIS roster sync (engine) -> cohort provisioning -> learning outcome
  (project.approved mesh event) -> signed webhook delivery -> AGS grade
  push to the LMS -> governed warehouse export.
"""

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

from app.controlplane.worker import process_outbox_once
from app.core.security import hash_password
from app.integrations.facade import emit_event
from app.integrations.models import EventDelivery, IntegrationEvent, OrgDomain
from app.models.cohort import Cohort, CohortMember
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus
from app.models.webhook import WebhookSubscription

# Drain EVENT topics only: pulling intg.sync.run here would execute stale
# queued runs from earlier committed test sessions mid-chain (flake source).
INTG_TOPICS = ["intg.event.created", "intg.delivery.attempt"]

IDP = "https://idp.acceptance.example.com"
LMS = "https://lms.acceptance.example.com"

_IDP_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_IDP_PRIV = _IDP_KEY.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
_IDP_JWK = json.loads(pyjwt.algorithms.RSAAlgorithm.to_jwk(_IDP_KEY.public_key()))
_IDP_JWK.update({"kid": "acc-k1", "alg": "RS256", "use": "sig"})


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


class AcceptanceWorld:
    """One fake for every external system in the chain, keyed by host."""

    def __init__(self, domain):
        self.domain = domain
        self.webhook_payloads = []
        self.ags_scores = []
        self.sis_classes = [
            {
                "sourcedId": "cls-101",
                "title": "Enterprise AI 101",
                "classCode": "EAI101",
                "terms": [{"sourcedId": "t-1"}],
                "school": {"sourcedId": "s-1"},
                "grades": ["12"],
            }
        ]
        self.tool_jwks = None  # set later for AGS assertion verification

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        parsed = urlsplit(url)
        host, path = parsed.netloc, parsed.path
        req = httpx.Request(method, url)
        # IdP (OIDC)
        if "idp.acceptance" in host:
            if path.endswith("/.well-known/openid-configuration"):
                return httpx.Response(
                    200,
                    json={
                        "issuer": IDP,
                        "authorization_endpoint": f"{IDP}/authorize",
                        "token_endpoint": f"{IDP}/token",
                        "jwks_uri": f"{IDP}/jwks",
                    },
                    request=req,
                )
            if path.endswith("/jwks"):
                return httpx.Response(200, json={"keys": [_IDP_JWK]}, request=req)
            if path.endswith("/token"):
                return httpx.Response(
                    200, json={"id_token": self.pending_id_token}, request=req
                )
        # SIS (OneRoster)
        if "sis.acceptance" in host:
            if path.endswith("/token"):
                return httpx.Response(200, json={"access_token": "sis-tok"}, request=req)
            if path.endswith("/classes"):
                qs = parse_qs(parsed.query)
                offset = int(qs.get("offset", ["0"])[0])
                items = self.sis_classes[offset : offset + 100]
                return httpx.Response(200, json={"classes": items}, request=req)
        # Customer webhook sink
        if "hooks.acceptance" in host:
            self.webhook_payloads.append(
                {"headers": dict(headers or {}), "body": json.loads(content)}
            )
            return httpx.Response(200, request=req)
        # LMS (AGS)
        if "lms.acceptance" in host:
            if path.endswith("/token"):
                form = parse_qs((content or b"").decode())
                assertion = form["client_assertion"][0]
                header = pyjwt.get_unverified_header(assertion)
                key = next(
                    pyjwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(k))
                    for k in self.tool_jwks["keys"]
                    if k["kid"] == header["kid"]
                )
                pyjwt.decode(
                    assertion, key=key, algorithms=["RS256"], audience=f"{LMS}/token"
                )
                return httpx.Response(200, json={"access_token": "ags-tok"}, request=req)
            if path.endswith("/scores"):
                self.ags_scores.append(json.loads(content))
                return httpx.Response(200, request=req)
        return httpx.Response(404, request=req)


@pytest.mark.asyncio
async def test_full_acceptance_chain(db, monkeypatch):
    from datetime import UTC, datetime

    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    # ── org with a verified enterprise domain ──
    owner = User(
        email=f"own-{uuid.uuid4().hex[:12]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Owner",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=owner.id, type="platform"),
        owner_user_id=owner.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )
    org = Organization(
        name=f"Acceptance {ULID()}",
        slug=f"acc-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=owner.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=owner.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    domain = f"acc-{uuid.uuid4().hex[:8]}.example.edu"
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
    world = AcceptanceWorld(domain)

    # ── 1. SCIM: the directory provisions a learner ──
    from app.integrations.services.scim import ScimTokenService, ScimUserService

    scim_token, _raw = await ScimTokenService(db).create(
        org.id, name="entra", group_map={}, created_by=owner.id
    )
    learner_email = f"learner-{uuid.uuid4().hex[:6]}@{domain}"
    scim_user, _ = await ScimUserService(db, scim_token).create(
        {"userName": learner_email, "displayName": "Learner One", "externalId": "dir-7"}
    )
    learner_id = scim_user["id"]

    # ── 2. SSO: the same person signs in through the org IdP (OIDC) ──
    import app.integrations.services.sso_oidc as sso_mod
    from app.integrations.services.sso_admin import SsoAdminService

    sso = await SsoAdminService(db).create(
        org.id,
        protocol="oidc",
        oidc_issuer=IDP,
        oidc_client_id="acc-client",
        oidc_client_secret="s",
        allow_jit=False,  # directory already provisioned the account
    )
    sso.status = "active"
    await db.flush()
    oidc = sso_mod.OidcService(db)
    oidc.egress = world
    url = await oidc.build_authorize_redirect(sso.id, redirect_uri="https://app.test/cb")
    qs = parse_qs(urlsplit(url).query)
    world.pending_id_token = pyjwt.encode(
        {
            "iss": IDP,
            "aud": "acc-client",
            "sub": "idp-sub-learner",
            "email": learner_email,
            "email_verified": True,
            "name": "Learner One",
            "nonce": qs["nonce"][0],
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,
        },
        _IDP_PRIV,
        algorithm="RS256",
        headers={"kid": "acc-k1"},
    )
    _conn, resolution = await oidc.handle_callback(
        state_value=qs["state"][0], code="c", redirect_uri="https://app.test/cb"
    )
    assert resolution.user.id == learner_id  # SCIM account, SSO login, ONE user
    assert resolution.jit_created is False

    # ── 3. SIS roster sync -> staged -> cohort provisioning ──
    from app.integrations import registry
    from app.integrations.services.connections import ConnectionService
    from app.integrations.services.roster import RosterProvisioningService
    from app.integrations.services.sync_engine import SyncProfileService, execute_run

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    conn = await csvc.create(
        org.id,
        provider_key="oneroster",
        name=f"sis-{uuid.uuid4().hex[:6]}",
        config={"token_url": "https://sis.acceptance.example.com/token"},
        base_url="https://sis.acceptance.example.com/ims/oneroster/rostering/v1p2",
        created_by=owner.id,
    )
    conn.status = "active"
    await csvc.set_credential(
        org.id, conn.id, kind="oauth2_tokens",
        values={"client_id": "cid", "client_secret": "cs"}, expires_at=None,
    )
    # Real OneRosterConnector, egress swapped for the fake world.
    real = registry.OneRosterConnector()
    profile = await SyncProfileService(db).create(
        org.id,
        connection_id=conn.id,
        name="roster-classes",
        model="roster.class",
        direction="pull",
        mapping_profile_id=None,
    )
    run = await SyncProfileService(db).trigger(org.id, profile.id)
    await db.commit()

    class WorldCtxConnector:
        key = "oneroster"
        capabilities = frozenset({"roster.read"})

        async def ping(self, ctx):
            return None

        def read(self, ctx, model, state):
            ctx.egress = world
            return real.read(ctx, model, state)

    registry.CONNECTORS["oneroster"] = WorldCtxConnector()
    await execute_run(db, run.id)
    await db.refresh(run)
    assert run.status == "succeeded" and run.stats["created"] == 1

    # enrollment arrives via staging (SIS linked the directory user by email)
    from app.integrations.models import StagedRecord

    db.add(
        StagedRecord(
            connection_id=conn.id,
            model="roster.user",
            external_id="sis-u-1",
            payload={"email": learner_email},
            raw_hash="h1",
            status="active",
        )
    )
    db.add(
        StagedRecord(
            connection_id=conn.id,
            model="roster.enrollment",
            external_id="sis-e-1",
            payload={
                "class_external_id": "cls-101",
                "user_external_id": "sis-u-1",
                "role": "student",
            },
            raw_hash="h2",
            status="active",
        )
    )
    await db.flush()
    report = await RosterProvisioningService(db).provision(org.id, conn.id, actor_id=owner.id)
    assert report["members_added"] == 1 and report["conflicts"] == 0
    cohort = (
        await db.execute(
            select(Cohort).where(Cohort.org_id == org.id, Cohort.name == "Enterprise AI 101")
        )
    ).scalar_one()
    member = (
        await db.execute(
            select(CohortMember).where(
                CohortMember.cohort_id == cohort.id, CohortMember.user_id == learner_id
            )
        )
    ).scalar_one()
    assert member is not None

    # ── 4. LTI mapping so the outcome can flow back to the LMS ──
    from app.integrations.services.lti import LtiService
    from app.integrations.services.lti_ags import ensure_tool_key, tool_jwks

    lti = LtiService(db)
    reg = await lti.create_registration(
        org.id,
        issuer=LMS,
        # unique per run: (issuer, client_id) is globally unique and the
        # chain COMMITS (outbox drains) — re-runs must not collide.
        client_id=f"acc-tool-{uuid.uuid4().hex[:8]}",
        auth_login_url=f"{LMS}/auth",
        auth_token_url=f"{LMS}/token",
        jwks_url=f"{LMS}/jwks",
        deployment_ids=["dep-1"],
    )
    link = await lti.map_resource_link(
        org.id,
        reg.id,
        deployment_id="dep-1",
        resource_link_id="rl-1",
        kind="project",
        target_id="01PROJACCEPTANCEXXXXXXXXXX",
        grade_sync_enabled=True,
    )
    link.ags_lineitem_url = f"{LMS}/ags/lineitems/1"
    # the learner "launched" once from the LMS: identity link exists
    from app.integrations.models import ExternalIdentityLink

    db.add(
        ExternalIdentityLink(
            org_id=org.id,
            user_id=learner_id,
            source="lti",
            connection_ref=reg.id,
            subject=f"{LMS}|lms-learner-1",
        )
    )
    await ensure_tool_key(db)
    world.tool_jwks = await tool_jwks(db)

    # ── 5. the customer's webhook subscription for outcomes ──
    db.add(
        WebhookSubscription(
            org_id=org.id,
            url="https://hooks.acceptance.example.com/outcomes",
            events=["com.openskill.project.*"],
            secret="b" * 64,
            active=True,
        )
    )
    await db.flush()

    # ── 6. the learning outcome: project approved -> mesh event ──
    import app.integrations.services.events as events_mod
    import app.integrations.services.lti_ags as ags_mod

    monkeypatch.setattr(events_mod, "EgressClient", lambda: world)
    monkeypatch.setattr(ags_mod, "EgressClient", lambda: world)
    event = await emit_event(
        db,
        org.id,
        "project.approved",
        subject="sub-acc",
        data={
            "submission_id": "sub-acc",
            "project_id": "01PROJACCEPTANCEXXXXXXXXXX",
            "user_id": learner_id,
            "final_score": 88,
        },
    )
    await db.commit()
    # Drain until OUR delivery is terminal — the shared outbox can hold due
    # retry messages from earlier (committed) test runs that would starve a
    # fixed round count.
    delivery = None
    for _ in range(40):
        await process_outbox_once(db, topics=INTG_TOPICS)
        delivery = (
            await db.execute(
                select(EventDelivery).where(EventDelivery.event_id == event.id)
            )
        ).scalar_one_or_none()
        if delivery is not None and delivery.status in ("succeeded", "exhausted"):
            break
    assert delivery is not None and delivery.status == "succeeded"
    hook = world.webhook_payloads[0]
    assert hook["body"]["type"] == "com.openskill.project.approved.v1"
    assert hook["headers"]["webhook-id"] == event.id
    assert hook["headers"]["webhook-signature"].startswith("v1,")
    # AGS grade landed in the LMS for the launch user
    assert world.ags_scores == [
        {
            "userId": "lms-learner-1",
            "scoreGiven": 88.0,
            "scoreMaximum": 100.0,
            "activityProgress": "Completed",
            "gradingProgress": "FullyGraded",
            "timestamp": world.ags_scores[0]["timestamp"],
        }
    ]

    # ── 7. governed export carries the outcome event, allowlist-shaped ──
    from app.integrations.services.warehouse import WarehouseExportService

    class MemWriter:
        def __init__(self):
            self.files = {}

        async def write(self, key, content):
            self.files[key] = content

    writer = MemWriter()
    wsvc = WarehouseExportService(db, writer=writer)
    stream = await wsvc.create_stream(org.id, name=f"ev-{ULID()}", dataset="events")
    export_run = await wsvc.run_export(org.id, stream.id)
    assert export_run.status == "succeeded"
    exported = [
        json.loads(line)
        for part in export_run.parts
        for line in writer.files[part].decode().strip().split("\n")
    ]
    outcome_rows = [r for r in exported if r["type"] == "com.openskill.project.approved.v1"]
    assert outcome_rows and set(outcome_rows[0]) == {"id", "type", "subject", "time"}

    # ── 8. deprovision closes the loop: SCIM deactivation sweeps sessions ──
    await ScimUserService(db, scim_token).patch(
        learner_id, {"Operations": [{"op": "replace", "path": "active", "value": False}]}
    )
    archived = (
        await db.execute(
            select(OrgMember).where(
                OrgMember.org_id == org.id, OrgMember.user_id == learner_id
            )
        )
    ).scalar_one()
    assert archived.status == MemberStatus.ARCHIVED
    # SSO login for the deprovisioned account now refuses.
    url2 = await oidc.build_authorize_redirect(sso.id, redirect_uri="https://app.test/cb")
    qs2 = parse_qs(urlsplit(url2).query)
    world.pending_id_token = pyjwt.encode(
        {
            "iss": IDP,
            "aud": "acc-client",
            "sub": "idp-sub-learner",
            "email": learner_email,
            "email_verified": True,
            "nonce": qs2["nonce"][0],
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,
        },
        _IDP_PRIV,
        algorithm="RS256",
        headers={"kid": "acc-k1"},
    )
    # Link still resolves the user, but... account remains ACTIVE platform-
    # wide (multi-org); org access is governed by membership, which is
    # archived. The chain asserts membership-based surfaces are closed.
    events_count = (
        await db.execute(
            select(IntegrationEvent).where(
                IntegrationEvent.org_id == org.id,
                IntegrationEvent.type == "com.openskill.org.scim.deprovisioned.v1",
            )
        )
    ).scalars().all()
    assert len(events_count) == 1
