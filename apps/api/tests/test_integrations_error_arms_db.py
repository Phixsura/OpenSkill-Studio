"""R511: error-arm totality — every AppError code the fabric can raise is
driven by at least one test (the standing guard at the bottom pins it).

The R510 scan generalized to ERROR codes found 16 raised-but-never-asserted
arms; most were junk-id 404s exercised only via status-code IDOR walls.
Each gets a direct driver here so the code STRING itself is pinned (a typo'd
or re-mapped code fails loudly, and the guard keeps future arms honest).
"""

import uuid

import pytest
import pytest_asyncio
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus

JUNK = "0" * 26


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
        email=f"ea-{uuid.uuid4().hex[:12]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Err Arms",
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
        name=f"EA {ULID()}",
        slug=f"ea-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=u.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE))
    await db.flush()
    return org, u


async def _expect(coro, code: str, status: int):
    with pytest.raises(AppError) as e:
        await coro
    assert e.value.code == code, f"{e.value.code} != {code}"
    assert e.value.status_code == status


@pytest.mark.asyncio
async def test_junk_id_arms_raise_their_documented_codes(db):
    org, owner = await _org(db)
    from app.integrations.services.bulk_import import BulkImportService
    from app.integrations.services.events import replay_delivery
    from app.integrations.services.identity import IdentityService
    from app.integrations.services.lti import LtiService
    from app.integrations.services.sso_admin import SsoAdminService
    from app.integrations.services.warehouse import WarehouseExportService

    await _expect(replay_delivery(db, org.id, JUNK), "DELIVERY_NOT_FOUND", 404)
    await _expect(
        WarehouseExportService(db).get_stream(org.id, JUNK), "EXPORT_STREAM_NOT_FOUND", 404
    )
    await _expect(IdentityService(db).unlink(org.id, JUNK), "IDENTITY_LINK_NOT_FOUND", 404)
    await _expect(BulkImportService(db).get(org.id, JUNK), "IMPORT_NOT_FOUND", 404)
    await _expect(LtiService(db).get_registration(org.id, JUNK), "LTI_REGISTRATION_NOT_FOUND", 404)
    from app.integrations.services.lti_nrps import sync_memberships

    await _expect(sync_memberships(db, org.id, JUNK), "LTI_RESOURCE_LINK_NOT_FOUND", 404)
    await _expect(SsoAdminService(db).get(org.id, JUNK), "SSO_CONNECTION_NOT_FOUND", 404)


@pytest.mark.asyncio
async def test_export_writer_missing_is_500_config_fault(db):
    org, owner = await _org(db)
    from app.integrations.services.warehouse import WarehouseExportService

    svc = WarehouseExportService(db, writer=None)
    stream = await svc.create_stream(org.id, name=f"wm-{ULID()}", dataset="events")
    await _expect(svc.run_export(org.id, stream.id), "EXPORT_WRITER_MISSING", 500)


@pytest.mark.asyncio
async def test_delivery_payload_empty_before_first_dispatch(db):
    org, owner = await _org(db)
    from app.integrations.api.events import delivery_payload as get_delivery_payload
    from app.integrations.facade import emit_event
    from app.integrations.models import EventDelivery
    from app.models.webhook import WebhookSubscription

    sub = WebhookSubscription(
        org_id=org.id,
        url="https://hooks.example.com/s",
        events=["com.openskill.project.*"],
        secret="a" * 64,
        active=True,
    )
    db.add(sub)
    ev = await emit_event(db, org.id, "project.approved", subject="pe", data={})
    await db.flush()
    d = EventDelivery(event_id=ev.id, subscription_id=sub.id, status="pending")
    db.add(d)
    await db.flush()
    await _expect(
        get_delivery_payload(org.id, d.id, db=db, user=owner), "DELIVERY_PAYLOAD_EMPTY", 404
    )
    await _expect(get_delivery_payload(org.id, JUNK, db=db, user=owner), "DELIVERY_NOT_FOUND", 404)


@pytest.mark.asyncio
async def test_storage_error_when_s3_yields_nothing(db, monkeypatch):
    import app.integrations.api.imports as imports_api

    async def _empty_gen():
        return
        yield  # pragma: no cover

    monkeypatch.setattr("app.core.storage.get_s3_client", lambda: _empty_gen())
    await _expect(imports_api._load_file("k"), "STORAGE_ERROR", 500)


@pytest.mark.asyncio
async def test_lti_resource_kind_invalid(db):
    org, owner = await _org(db)
    from app.integrations.services.lti import LtiService

    svc = LtiService(db)
    reg = await svc.create_registration(
        org.id,
        issuer=f"https://lms-{uuid.uuid4().hex[:8]}.example.com",
        client_id="c",
        auth_login_url="https://lms.example.com/a",
        auth_token_url="https://lms.example.com/t",
        jwks_url="https://lms.example.com/j",
        deployment_ids=["d1"],
    )
    await _expect(
        svc.map_resource_link(
            org.id,
            reg.id,
            deployment_id="d1",
            resource_link_id="rl1",
            kind="bogus-kind",
            target_id="x",
        ),
        "LTI_RESOURCE_KIND_INVALID",
        422,
    )


@pytest.mark.asyncio
async def test_import_row_invalid_surfaces_unresolvable_roster_refs(db):
    org, owner = await _org(db)
    from app.integrations.services.bulk_import import BulkImportService

    svc = BulkImportService(db, file_loader=None)
    await _expect(
        svc._apply_roster_row(
            org.id,
            {
                "row_number": 2,
                "email": "ghost@nowhere.example.edu",
                "cohort_slug": "no-such",
                "role": "student",
            },
        ),
        "IMPORT_ROW_INVALID",
        422,
    )


@pytest.mark.asyncio
async def test_sso_metadata_fetch_failed_on_non_200(db, monkeypatch):
    org, owner = await _org(db)
    import datetime as _dt

    import httpx
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import Encoding
    from cryptography.x509.oid import NameOID

    from app.integrations.services.sso_admin import SsoAdminService

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "idp.example.com")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_dt.datetime.now(_dt.UTC) - _dt.timedelta(days=1))
        .not_valid_after(_dt.datetime.now(_dt.UTC) + _dt.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    pem = cert.public_bytes(Encoding.PEM).decode()

    svc = SsoAdminService(db)
    conn = await svc.create(
        org.id,
        protocol="saml",
        idp_entity_id="https://idp.example.com",
        idp_sso_url="https://idp.example.com/sso",
        idp_metadata_url="https://idp.example.com/metadata",
        idp_certificates=[{"pem": pem}],
    )

    class _Egress:
        async def request(self, method, url, **kw):
            return httpx.Response(503, request=httpx.Request(method, url))

    await _expect(
        svc.refresh_from_metadata(org.id, conn.id, egress=_Egress()),
        "SSO_METADATA_FETCH_FAILED",
        502,
    )


def test_every_raised_fabric_error_code_is_asserted_in_tests():
    """Standing guard (R511): a NEW AppError code raised anywhere in the
    fabric must be asserted by code-string in at least one test — an
    untested error arm is unverified behavior AND an unpinned contract."""
    import pathlib
    import re

    code_re = re.compile(r"""AppError\(\s*["']([A-Z0-9_]+)["']""")
    raised: set[str] = set()
    for f in pathlib.Path("app/integrations").rglob("*.py"):
        raised |= set(code_re.findall(f.read_text()))
    raised |= {"EGRESS_BLOCKED", "UPSTREAM_UNREACHABLE"}

    corpus = ""
    for f in pathlib.Path("tests").rglob("*.py"):
        corpus += f.read_text()
    untested = sorted(c for c in raised if c not in corpus)
    assert not untested, f"error arms no test asserts: {untested}"
