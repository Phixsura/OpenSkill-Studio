"""R36 — fabric health summary endpoint (aggregate counts only)."""

import uuid

import pytest
import pytest_asyncio
from ulid import ULID

from app.core.security import hash_password
from app.integrations.api.connections import fabric_health
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(
        email=f"hl-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Health",
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
        name=f"Org {ULID()}", slug=f"o-{str(ULID()).lower()}", status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER,
                     status=MemberStatus.ACTIVE))
    await db.flush()
    return org


@pytest.mark.asyncio
async def test_health_counts_are_org_scoped(db):
    from app.integrations.services.connections import ConnectionService
    from app.models.webhook import WebhookSubscription

    owner = await _user(db)
    org = await _org(db, owner)
    other_owner = await _user(db)
    other = await _org(db, other_owner)

    csvc = ConnectionService(db)
    await csvc.sync_provider_catalog()
    await db.flush()
    await csvc.create(
        org.id, provider_key="generic_webhook", name=f"h-{uuid.uuid4().hex[:6]}",
        config={}, base_url="https://x.example.com", created_by=owner.id,
    )
    # Noise in ANOTHER org must not leak into this org's counts.
    await csvc.create(
        other.id, provider_key="generic_webhook", name=f"h-{uuid.uuid4().hex[:6]}",
        config={}, base_url="https://y.example.com", created_by=other_owner.id,
    )
    db.add(WebhookSubscription(
        org_id=org.id, url="https://sink.example.com/h", events=["project.approved"],
        secret="whsec_x", active=False,
    ))
    await db.flush()

    out = await fabric_health(org.id, db=db, user=owner)
    data = out["data"]
    assert data["connections"]["total"] == 1
    assert data["connections"]["by_status"] == {"pending": 1}
    assert data["subscriptions"] == {"total": 1, "disabled": 1}
    assert data["deliveries"] == {"pending": 0, "exhausted_24h": 0}
    assert data["identity_queue_pending"] == 0
    assert data["sync"] == {"profiles": 0, "failed_runs_24h": 0}
    assert data["sso_connections_active"] == 0

    # Non-admin of the org is refused (uniform wall).
    from fastapi.exceptions import HTTPException

    with pytest.raises(HTTPException):
        await fabric_health(org.id, db=db, user=other_owner)


@pytest.mark.asyncio
async def test_webhook_test_send_reports_status_and_signs(db, monkeypatch):
    """R37: /webhooks/{id}/test dispatches a sample SIGNED CloudEvent
    synchronously, reports delivered/status/latency, 404s cross-org, and
    maps connection failures to a result (never a 500)."""
    import json

    import httpx

    import app.api.v1.endpoints.webhooks as ep
    from app.models.webhook import WebhookSubscription
    from app.services import webhook as legacy

    owner = await _user(db)
    org = await _org(db, owner)
    sub = WebhookSubscription(
        org_id=org.id, url="https://sink.example.com/h",
        events=["project.approved"], secret="b" * 64, active=True,
    )
    db.add(sub)
    await db.flush()

    calls = []

    class _Fake:
        def __init__(self, code):
            self.code = code

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            calls.append({"url": url, "headers": headers, "body": content})
            if self.code == -1:
                raise httpx.ConnectTimeout("boom")
            return httpx.Response(self.code, request=httpx.Request(method, url))

    from app.integrations import security as sec

    monkeypatch.setattr(sec, "EgressClient", lambda: _Fake(200))
    out = await ep.test_webhook(org.id, sub.id, user=owner, db=db)
    data = out.data
    assert data["delivered"] is True and data["status_code"] == 200
    body = json.loads(calls[0]["body"])
    assert body["type"] == "com.openskill.integration.subscription.test.v1"
    assert body["data"]["test"] is True
    assert "webhook-signature" in calls[0]["headers"]

    # Receiver down -> structured failure, not a 500.
    monkeypatch.setattr(sec, "EgressClient", lambda: _Fake(-1))
    out2 = await ep.test_webhook(org.id, sub.id, user=owner, db=db)
    assert out2.data["delivered"] is False and out2.data["error"] == "ConnectTimeout"

    # Cross-org: uniform 404.
    from app.exceptions import AppError

    mallory = await _user(db)
    other = await _org(db, mallory)
    with pytest.raises(AppError) as exc:
        await ep.test_webhook(other.id, sub.id, user=mallory, db=db)
    assert exc.value.status_code == 404
    assert legacy is not None  # module import sanity


@pytest.mark.asyncio
async def test_connection_health_sweep_pings_and_alerts_on_transition(db):
    """R41: the sweep pings active/degraded connections, feeds the health
    state machine, and emits integration.connection.unhealthy exactly on
    the transition INTO an unhealthy status."""
    from sqlalchemy import select as _select

    from app.exceptions import AppError
    from app.integrations import registry
    from app.integrations.models import IntegrationEvent
    from app.integrations.services.connections import ConnectionService

    user = await _user(db)
    org = await _org(db, user)
    svc = ConnectionService(db)
    await svc.sync_provider_catalog()
    await db.flush()
    conn = await svc.create(
        org.id, provider_key="oneroster", name=f"hs-{uuid.uuid4().hex[:6]}",
        config={"token_url": "https://idp.example.com/token"},
        base_url="https://sis.example.com/ims/oneroster", created_by=user.id,
    )
    conn.status = "active"
    await db.flush()

    class _DeadConnector:
        key = "oneroster"
        capabilities = frozenset({"roster.read"})

        async def ping(self, ctx):
            raise AppError("CONNECTION_AUTH_REJECTED", "401 from source", 502)

    old = registry.CONNECTORS.get("oneroster")
    registry.CONNECTORS["oneroster"] = _DeadConnector()
    try:
        swept = await svc.sweep_connection_health()
        assert swept >= 1
        await db.refresh(conn)
        assert conn.status == "active"  # first rejection only records
        await svc.sweep_connection_health()  # second consecutive -> parks
        await db.refresh(conn)
        assert conn.status == "error"
        events = (
            await db.execute(
                _select(IntegrationEvent).where(
                    IntegrationEvent.subject == conn.id,
                    IntegrationEvent.type
                    == "com.openskill.integration.connection.unhealthy.v1",
                )
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].data["error_class"] == "CONNECTION_AUTH_REJECTED"
        # Error connections are NOT pinged again (load guard) — count calls.
        calls = {"n": 0}

        class _CountingDead(_DeadConnector):
            async def ping(self, ctx):
                calls["n"] += 1
                raise AppError("CONNECTION_AUTH_REJECTED", "401", 502)

        registry.CONNECTORS["oneroster"] = _CountingDead()
        await svc.sweep_connection_health()
        assert calls["n"] == 0  # the parked connection stays untouched

        # A connector CRASH (non-AppError) still records failure health.
        conn.status = "active"
        conn.health = {}
        await db.flush()

        class _Crashing:
            key = "oneroster"
            capabilities = frozenset({"roster.read"})

            async def ping(self, ctx):
                raise RuntimeError("segfault-ish")

        registry.CONNECTORS["oneroster"] = _Crashing()
        await svc.sweep_connection_health()
        await db.refresh(conn)
        assert conn.health.get("last_error_class") == "CONNECTOR_CRASH"

        # Error connections are NOT re-swept (not in active/degraded).
        await svc.sweep_connection_health()
        events2 = (
            await db.execute(
                _select(IntegrationEvent).where(IntegrationEvent.subject == conn.id)
            )
        ).scalars().all()
        assert len(events2) == 1
    finally:
        if old is not None:
            registry.CONNECTORS["oneroster"] = old
