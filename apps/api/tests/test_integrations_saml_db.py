"""P3b tests — SAML SP validation vectors (signxml-signed assertions)."""

import base64
import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from lxml import etree
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.models import OrgDomain, SsoLoginState
from app.integrations.services.sso_admin import SsoAdminService
from app.integrations.services.sso_saml import SamlService, sp_entity_id
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus

SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"
SAMLP_NS = "urn:oasis:names:tc:SAML:2.0:protocol"
IDP_ENTITY = "https://idp.saml.example.com/metadata"
IDP_SSO = "https://idp.saml.example.com/sso"


def _mint_keypair(cn: str):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(days=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    return key_pem, cert_pem


IDP_KEY, IDP_CERT = _mint_keypair("idp.saml.example.com")
ROGUE_KEY, ROGUE_CERT = _mint_keypair("rogue.example.com")


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
        email=f"sm-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Sm",
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
    domain = f"saml-{uuid.uuid4().hex[:8]}.example.edu"
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
    return org, u, domain


async def _saml_conn(db, org, cert_pem=IDP_CERT, allow_jit=True):
    conn = await SsoAdminService(db).create(
        org.id,
        protocol="saml",
        idp_entity_id=IDP_ENTITY,
        idp_sso_url=IDP_SSO,
        idp_certificates=[{"pem": cert_pem}],
        allow_jit=allow_jit,
    )
    conn.status = "active"
    await db.flush()
    return conn


def _assertion_xml(
    *,
    in_response_to: str,
    email: str,
    audience: str | None = None,
    issuer: str = IDP_ENTITY,
    name_id: str | None = None,
    not_on_or_after: datetime | None = None,
):
    now = datetime.now(UTC)
    noa = (not_on_or_after or (now + timedelta(minutes=5))).isoformat()
    nb = (now - timedelta(minutes=1)).isoformat()
    aud = audience if audience is not None else sp_entity_id()
    nid = name_id or f"subj-{uuid.uuid4().hex[:8]}"
    return f"""<saml:Assertion xmlns:saml="{SAML_NS}" ID="_A{uuid.uuid4().hex}" Version="2.0" IssueInstant="{now.isoformat()}">
  <saml:Issuer>{issuer}</saml:Issuer>
  <saml:Subject>
    <saml:NameID>{nid}</saml:NameID>
    <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
      <saml:SubjectConfirmationData InResponseTo="_{in_response_to}" NotOnOrAfter="{noa}"/>
    </saml:SubjectConfirmation>
  </saml:Subject>
  <saml:Conditions NotBefore="{nb}" NotOnOrAfter="{noa}">
    <saml:AudienceRestriction><saml:Audience>{aud}</saml:Audience></saml:AudienceRestriction>
  </saml:Conditions>
  <saml:AttributeStatement>
    <saml:Attribute Name="email"><saml:AttributeValue>{email}</saml:AttributeValue></saml:Attribute>
    <saml:Attribute Name="displayName"><saml:AttributeValue>SAML User</saml:AttributeValue></saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>"""


def _sign_assertion(assertion_xml: str, key_pem=IDP_KEY, cert_pem=IDP_CERT) -> etree._Element:
    from signxml import XMLSigner

    root = etree.fromstring(assertion_xml.encode())
    # SAML mandates EXCLUSIVE c14n — signxml's default (inclusive 1.1) would
    # bake ancestor namespaces into the digest and break once the assertion
    # is wrapped in a samlp:Response.
    return XMLSigner(
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    ).sign(root, key=key_pem, cert=cert_pem)


def _wrap_response(*elements) -> str:
    resp = etree.Element(f"{{{SAMLP_NS}}}Response", nsmap={"samlp": SAMLP_NS})
    resp.set("ID", f"_R{uuid.uuid4().hex}")
    resp.set("Version", "2.0")
    resp.set("IssueInstant", datetime.now(UTC).isoformat())
    for el in elements:
        resp.append(el)
    return base64.b64encode(etree.tostring(resp)).decode()


async def _start(db, conn) -> str:
    """Mint the outstanding AuthnRequest state; return the state id."""
    svc = SamlService(db)
    url = await svc.build_authn_redirect(conn.id)
    assert url.startswith(IDP_SSO)
    from urllib.parse import parse_qs, urlsplit

    return parse_qs(urlsplit(url).query)["RelayState"][0]


@pytest.mark.asyncio
async def test_saml_happy_path_jit(db):
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    state = await _start(db, conn)
    email = f"saml-{uuid.uuid4().hex[:6]}@{domain}"
    signed = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    b64 = _wrap_response(signed)
    conn2, result, _rt = await SamlService(db).handle_acs(
        connection_id=conn.id, saml_response_b64=b64, relay_state=state
    )
    assert conn2.id == conn.id
    assert result.jit_created is True and result.user.email == email
    # Same NameID relaunches as the same user.
    state2 = await _start(db, conn)
    signed2 = _sign_assertion(
        _assertion_xml(in_response_to=state2, email=email, name_id="stable-1")
    )
    # (different subject -> matches by verified email to the same account)
    _, result2, _rt2 = await SamlService(db).handle_acs(
        connection_id=conn.id, saml_response_b64=_wrap_response(signed2), relay_state=state2
    )
    assert result2.user.id == result.user.id


@pytest.mark.asyncio
async def test_saml_rejection_vectors(db):
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    email = f"v-{uuid.uuid4().hex[:6]}@{domain}"
    svc = SamlService(db)

    async def expect_reject(b64, relay=None):
        with pytest.raises(AppError) as e:
            await svc.handle_acs(
                connection_id=conn.id, saml_response_b64=b64, relay_state=relay
            )
        assert e.value.code == "SSO_ASSERTION_INVALID"

    # unsigned assertion
    state = await _start(db, conn)
    raw = etree.fromstring(_assertion_xml(in_response_to=state, email=email).encode())
    await expect_reject(_wrap_response(raw))

    # signed by a ROGUE cert (cross-tenant forgery)
    state = await _start(db, conn)
    rogue = _sign_assertion(
        _assertion_xml(in_response_to=state, email=email),
        key_pem=ROGUE_KEY,
        cert_pem=ROGUE_CERT,
    )
    await expect_reject(_wrap_response(rogue))

    # audience mismatch
    state = await _start(db, conn)
    bad_aud = _sign_assertion(
        _assertion_xml(in_response_to=state, email=email, audience="https://other-sp")
    )
    await expect_reject(_wrap_response(bad_aud))

    # expired
    state = await _start(db, conn)
    expired = _sign_assertion(
        _assertion_xml(
            in_response_to=state,
            email=email,
            not_on_or_after=datetime.now(UTC) - timedelta(minutes=10),
        )
    )
    await expect_reject(_wrap_response(expired))

    # unknown InResponseTo (unsolicited)
    ghost = _sign_assertion(_assertion_xml(in_response_to="0" * 26, email=email))
    await expect_reject(_wrap_response(ghost))

    # wrong issuer
    state = await _start(db, conn)
    bad_iss = _sign_assertion(
        _assertion_xml(in_response_to=state, email=email, issuer="https://rogue-idp")
    )
    await expect_reject(_wrap_response(bad_iss))

    # DTD smuggling forbidden outright
    dtd = base64.b64encode(
        b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e "x">]><x>&e;</x>'
    ).decode()
    await expect_reject(dtd)


@pytest.mark.asyncio
async def test_saml_replay_and_state_single_use(db):
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    email = f"rp-{uuid.uuid4().hex[:6]}@{domain}"
    state = await _start(db, conn)
    signed = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    b64 = _wrap_response(signed)
    svc = SamlService(db)
    await svc.handle_acs(connection_id=conn.id, saml_response_b64=b64, relay_state=state)
    # The exact same response replayed: state consumed -> rejected.
    with pytest.raises(AppError):
        await svc.handle_acs(connection_id=conn.id, saml_response_b64=b64, relay_state=state)
    # Same ASSERTION ID under a fresh state: assertion replay cache rejects.
    state2 = await _start(db, conn)
    tree = etree.fromstring(base64.b64decode(b64))
    assertion = tree.find(f"{{{SAML_NS}}}Assertion")
    scd = assertion.find(
        f"{{{SAML_NS}}}Subject/{{{SAML_NS}}}SubjectConfirmation/"
        f"{{{SAML_NS}}}SubjectConfirmationData"
    )
    scd.set("InResponseTo", f"_{state2}")
    # (signature now broken by the edit — re-sign a FRESH assertion with the
    # SAME ID instead to isolate the replay check)
    reused_id = assertion.get("ID")
    fresh = _assertion_xml(in_response_to=state2, email=email)
    fresh_root = etree.fromstring(fresh.encode())
    fresh_root.set("ID", reused_id)
    resigned = _sign_assertion(etree.tostring(fresh_root).decode())
    with pytest.raises(AppError):
        await svc.handle_acs(
            connection_id=conn.id,
            saml_response_b64=_wrap_response(resigned),
            relay_state=state2,
        )


@pytest.mark.asyncio
async def test_saml_xsw_unsigned_sibling_ignored(db):
    """XML Signature Wrapping: an UNSIGNED evil assertion alongside the
    signed one must never be consumed — the verifier returns only the signed
    subtree, so the evil email never reaches identity resolution."""
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    good_email = f"good-{uuid.uuid4().hex[:6]}@{domain}"
    evil_email = f"evil-{uuid.uuid4().hex[:6]}@{domain}"
    state = await _start(db, conn)
    signed = _sign_assertion(_assertion_xml(in_response_to=state, email=good_email))
    evil = etree.fromstring(
        _assertion_xml(in_response_to=state, email=evil_email).encode()
    )
    # Evil assertion FIRST (the classic naive-parser pick).
    b64 = _wrap_response(evil, signed)
    svc = SamlService(db)
    try:
        _, result, _rt3 = await svc.handle_acs(
            connection_id=conn.id, saml_response_b64=b64, relay_state=state
        )
        # If accepted at all, it MUST be the signed identity.
        assert result.user.email == good_email
    except AppError:
        pass  # outright rejection is equally safe
    evil_user = (
        await db.execute(select(User).where(User.email == evil_email))
    ).scalar_one_or_none()
    assert evil_user is None  # the unsigned identity never materialized


@pytest.mark.asyncio
async def test_saml_admin_config_rules(db):
    org, owner, domain = await _org(db)
    svc = SsoAdminService(db)
    with pytest.raises(AppError) as e:
        await svc.create(org.id, protocol="saml", idp_entity_id=IDP_ENTITY, idp_sso_url=IDP_SSO)
    assert e.value.code == "SSO_CONFIG_INVALID"  # no certificates
    with pytest.raises(AppError):
        await svc.create(
            org.id,
            protocol="saml",
            idp_entity_id=IDP_ENTITY,
            idp_sso_url=IDP_SSO,
            idp_certificates=[{"pem": "not-a-cert"}],
        )
    conn = await _saml_conn(db, org)
    assert conn.idp_certificates[0]["fingerprint_sha256"]
    assert conn.idp_certificates[0]["not_after"]
    # pending request rows purge path intact (shared SsoLoginState table)
    states = (
        await db.execute(
            select(SsoLoginState).where(SsoLoginState.sso_connection_id == conn.id)
        )
    ).scalars().all()
    assert isinstance(states, list)


# ── R19: SAML cert-expiry sweep ──


@pytest.mark.asyncio
async def test_cert_expiry_sweep_alerts_once_per_day(db):
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select as _select

    from app.integrations.models import IntegrationEvent

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    # Pin an expiry 10 days out (inside the 30-day window).
    certs = list(conn.idp_certificates)
    certs[0] = dict(certs[0], not_after=(datetime.now(UTC) + timedelta(days=10)).isoformat())
    conn.idp_certificates = certs
    await db.flush()
    svc = SsoAdminService(db)
    assert await svc.sweep_expiring_certificates() == 1
    events = (
        await db.execute(
            _select(IntegrationEvent).where(
                IntegrationEvent.subject == conn.id,
                IntegrationEvent.type
                == "com.openskill.integration.sso.cert_expiring.v1",
            )
        )
    ).scalars().all()
    assert len(events) == 1 and 9 <= events[0].data["days_left"] <= 10
    # Daily dedup: a second sweep within 23h stays quiet.
    assert await svc.sweep_expiring_certificates() == 0
    # A healthy (365-day) cert never alerts.
    certs[0] = dict(certs[0], not_after=(datetime.now(UTC) + timedelta(days=300)).isoformat())
    conn.idp_certificates = list(certs)
    await db.flush()
    # (still deduped this day for THIS conn; a fresh conn proves the window)
    await _saml_conn(db, (await _org(db))[0])  # healthy cert, no alert
    assert await svc.sweep_expiring_certificates() == 0


# ── R30: verifier mutation-probe killers (signed-but-malicious variants) ──


@pytest.mark.asyncio
async def test_saml_condition_and_subject_vectors(db):
    """Each variant is SIGNED by the pinned cert — only the semantic check
    under test can reject it."""
    import re as _re

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    email = f"k-{uuid.uuid4().hex[:6]}@{domain}"
    svc = SamlService(db)

    async def expect_reject(xml: str, relay=None):
        signed = _sign_assertion(xml)
        with pytest.raises(AppError) as e:
            await svc.handle_acs(
                connection_id=conn.id,
                saml_response_b64=_wrap_response(signed),
                relay_state=relay,
            )
        assert e.value.code == "SSO_ASSERTION_INVALID"

    # Missing <Conditions> entirely.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email)
    await expect_reject(_re.sub(r"<saml:Conditions.*?</saml:Conditions>", "", xml, flags=_re.S))

    # NotBefore in the future (beyond skew).
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email)
    future = (datetime.now(UTC) + timedelta(minutes=30)).isoformat()
    await expect_reject(_re.sub(r'NotBefore="[^"]*"', f'NotBefore="{future}"', xml))

    # R177: a non-compliant IdP sending a NAIVE timestamp (no Z/offset) must
    # yield a clean 403, not a 500 from comparing naive vs aware datetimes.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email)
    naive = "2099-01-01T00:00:00"  # no tz — would be naive, but still future-expiry
    await expect_reject(
        _re.sub(r'NotBefore="[^"]*"', 'NotBefore="2099-01-01T00:00:00"', xml)
    )
    assert naive  # referenced

    # Conditions without NotOnOrAfter.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email)
    xml = _re.sub(r'(<saml:Conditions[^>]*?) NotOnOrAfter="[^"]*"', r"\1", xml, count=1)
    await expect_reject(xml)

    # Unsolicited: InResponseTo without the AuthnRequest prefix.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email).replace(
        f'InResponseTo="_{state}"', f'InResponseTo="{state}"'
    )
    await expect_reject(xml)

    # RelayState mismatch on an otherwise-valid assertion.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email)
    await expect_reject(xml, relay="not-the-state")

    # Whitespace NameID strips to empty.
    state = await _start(db, conn)
    xml = _assertion_xml(in_response_to=state, email=email, name_id="  ")
    await expect_reject(xml)


@pytest.mark.asyncio
async def test_saml_dtd_forbidden(db):
    """A DOCTYPE anywhere in the response is refused outright (XXE surface),
    even when the assertion inside is validly signed."""
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    svc = SamlService(db)
    state = await _start(db, conn)
    signed = _sign_assertion(
        _assertion_xml(in_response_to=state, email=f"d@{domain}")
    )
    resp = etree.Element(f"{{{SAMLP_NS}}}Response", nsmap={"samlp": SAMLP_NS})
    resp.set("ID", f"_R{uuid.uuid4().hex}")
    resp.append(signed)
    raw = b'<!DOCTYPE Response [<!ENTITY x "y">]>' + etree.tostring(resp)
    with pytest.raises(AppError) as e:
        await svc.handle_acs(
            connection_id=conn.id,
            saml_response_b64=base64.b64encode(raw).decode(),
            relay_state=None,
        )
    assert e.value.code == "SSO_ASSERTION_INVALID"


# ── R51: SAML metadata auto-refresh ──


def _metadata_xml(cert_pem: str, *, entity="https://idp.example.com/meta",
                  sso="https://idp.example.com/sso2", use="signing") -> bytes:
    b64 = "".join(
        line for line in cert_pem.strip().splitlines() if "CERTIFICATE" not in line
    )
    return f"""<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
  xmlns:ds="http://www.w3.org/2000/09/xmldsig#" entityID="{entity}">
  <md:IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:KeyDescriptor use="{use}">
      <ds:KeyInfo><ds:X509Data><ds:X509Certificate>{b64}</ds:X509Certificate></ds:X509Data></ds:KeyInfo>
    </md:KeyDescriptor>
    <md:SingleSignOnService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
      Location="{sso}"/>
  </md:IDPSSODescriptor>
</md:EntityDescriptor>""".encode()


class _MetaEgress:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
        import httpx

        return httpx.Response(
            self.status, content=self.body, request=httpx.Request(method, url)
        )


@pytest.mark.asyncio
async def test_metadata_refresh_rotates_certs_and_rejects_dtd(db):
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    conn.idp_metadata_url = "https://idp.example.com/metadata.xml"
    await db.flush()
    svc = SsoAdminService(db)

    # Fresh cert from the ROGUE pair = a rotation (different from pinned).
    # R252: the metadata's entityID must MATCH the configured one — the old
    # behavior (silently adopting a different entityID) was the SAML
    # mix-up vector this test now pins shut below.
    out = await svc.refresh_from_metadata(
        org.id, conn.id, egress=_MetaEgress(_metadata_xml(ROGUE_CERT, entity=IDP_ENTITY))
    )
    assert out == {"certificates": 1, "rotated": True}
    await db.refresh(conn)
    assert conn.idp_entity_id == IDP_ENTITY

    # R252 mismatch direction: a document for a DIFFERENT entity is refused
    # and nothing (certs/entity/sso) is adopted from it.
    pinned_before = conn.idp_certificates
    with pytest.raises(AppError) as mm:
        await svc.refresh_from_metadata(
            org.id, conn.id,
            egress=_MetaEgress(_metadata_xml(ROGUE_CERT, entity="https://imposter.example.com")),
        )
    assert mm.value.code == "SSO_METADATA_INVALID"
    await db.refresh(conn)
    assert conn.idp_entity_id == IDP_ENTITY
    assert conn.idp_certificates == pinned_before
    assert conn.idp_sso_url == "https://idp.example.com/sso2"
    assert len(conn.idp_certificates) == 1 and conn.idp_certificates[0]["not_after"]

    # Same metadata again: no rotation.
    out2 = await svc.refresh_from_metadata(
        org.id, conn.id, egress=_MetaEgress(_metadata_xml(ROGUE_CERT, entity=IDP_ENTITY))
    )
    assert out2["rotated"] is False

    # Encryption-only keys are ignored -> no signing certs -> 422.
    with pytest.raises(AppError):
        await svc.refresh_from_metadata(
            org.id, conn.id, egress=_MetaEgress(_metadata_xml(ROGUE_CERT, entity=IDP_ENTITY, use="encryption"))
        )
    # DTD refused outright.
    dtd = b'<!DOCTYPE md [<!ENTITY x "y">]>' + _metadata_xml(ROGUE_CERT)
    with pytest.raises(AppError):
        await svc.refresh_from_metadata(org.id, conn.id, egress=_MetaEgress(dtd))
    # Upstream failure is a 502-class error, not a crash.
    with pytest.raises(AppError) as exc:
        await svc.refresh_from_metadata(
            org.id, conn.id, egress=_MetaEgress(b"", status=500)
        )
    assert exc.value.status_code == 502
    # Wrong protocol (oidc) with a metadata URL set anyway -> 422 as well.
    from app.integrations.services.sso_admin import SsoAdminService as _Svc

    oidc_conn = await _Svc(db).create(
        org.id, protocol="oidc", oidc_issuer="https://idp9.example.com",
        oidc_client_id="c9", oidc_client_secret="s",
    )
    oidc_conn.idp_metadata_url = "https://idp9.example.com/metadata.xml"
    await db.flush()
    with pytest.raises(AppError) as exc_proto:
        await svc.refresh_from_metadata(org.id, oidc_conn.id)
    assert exc_proto.value.status_code == 422

    # No metadata URL configured -> 422.
    conn2 = await _saml_conn(db, (await _org(db))[0])
    with pytest.raises(AppError) as exc2:
        await svc.refresh_from_metadata(conn2.org_id, conn2.id)
    assert exc2.value.status_code == 422


@pytest.mark.asyncio
async def test_login_discovery_routes_by_protocol(db):
    """R67: /sso/login discovery must route a SAML org to the SAML authorize
    endpoint — a SAML-only org was handed the OIDC URL (dead login)."""
    import inspect

    import app.integrations.api.sso as sso_api

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    conn.status = "active"
    await db.flush()
    # find the discovery endpoint (protocol /sso/login)
    fn = None
    for obj in vars(sso_api).values():
        if inspect.iscoroutinefunction(obj) and "org_for_email_domain" in inspect.getsource(obj):
            fn = obj
            break
    assert fn is not None, "discovery endpoint not found"
    out = await fn(email=f"who@{domain}", db=db)
    assert out["data"]["sso"] is True
    assert out["data"]["authorize_url"].startswith("/api/v1/sso/saml/authorize?")


@pytest.mark.asyncio
async def test_saml_deep_link_round_trip(db):
    """R75: return_to survives authn-request state -> ACS (SAML symmetry
    with the OIDC deep link)."""
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    svc = SamlService(db)
    url = await svc.build_authn_redirect(conn.id, return_to="/dashboard/orgs/Z/skills")
    from urllib.parse import parse_qs, urlsplit

    state = parse_qs(urlsplit(url).query)["RelayState"][0]
    signed = _sign_assertion(
        _assertion_xml(in_response_to=state, email=f"dl-{uuid.uuid4().hex[:6]}@{domain}")
    )
    _, result, return_to = await svc.handle_acs(
        connection_id=conn.id, saml_response_b64=_wrap_response(signed), relay_state=state
    )
    assert return_to == "/dashboard/orgs/Z/skills"
    assert result.user is not None


# ── R88: Single Logout ──


def _signed_slo_query(subject: str, *, key_pem=IDP_KEY, issuer=IDP_ENTITY,
                      relay: str | None = None, sign: bool = True) -> str:
    import zlib
    from urllib.parse import quote

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    req = (
        f'<samlp:LogoutRequest xmlns:samlp="{SAMLP_NS}" xmlns:saml="{SAML_NS}" '
        f'ID="_LO{uuid.uuid4().hex}" Version="2.0" '
        f'IssueInstant="{datetime.now(UTC).isoformat()}">'
        f"<saml:Issuer>{issuer}</saml:Issuer>"
        f"<saml:NameID>{subject}</saml:NameID>"
        "</samlp:LogoutRequest>"
    )
    deflated = zlib.compress(req.encode())[2:-4]
    parts = [f"SAMLRequest={quote(base64.b64encode(deflated).decode(), safe='')}"]
    if relay is not None:
        parts.append(f"RelayState={quote(relay, safe='')}")
    parts.append(
        "SigAlg=" + quote("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256", safe="")
    )
    query = "&".join(parts)
    if not sign:
        return query
    key = serialization.load_pem_private_key(
        key_pem if isinstance(key_pem, bytes) else key_pem.encode(), password=None
    )
    sig = key.sign(query.encode(), padding.PKCS1v15(), hashes.SHA256())
    return query + "&Signature=" + quote(base64.b64encode(sig).decode(), safe="")


@pytest.mark.asyncio
async def test_slo_signed_request_revokes_sessions(db):
    from datetime import timedelta as _td

    from app.models.user import RefreshToken

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    conn.idp_slo_url = "https://idp.example.com/slo"
    await db.flush()
    svc = SamlService(db)
    # Establish a linked user via a normal ACS login.
    state = await _start(db, conn)
    email = f"slo-{uuid.uuid4().hex[:6]}@{domain}"
    signed = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    _, result, _rt = await svc.handle_acs(
        connection_id=conn.id, saml_response_b64=_wrap_response(signed), relay_state=state
    )
    subject = result.link.subject
    db.add(RefreshToken(user_id=result.user.id, token_hash="s" * 64,
                        expires_at=datetime.now(UTC) + _td(days=7)))
    await db.flush()

    conn2, swept, relay = await svc.handle_slo_request(
        connection_id=conn.id,
        raw_query=_signed_slo_query(subject, relay="r-1"),
    )
    assert swept == 1 and relay == "r-1"
    live = (
        await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == result.user.id,
                RefreshToken.revoked_at.is_(None),
            )
        )
    ).scalars().all()
    assert live == []
    redirect = svc.build_slo_response_redirect(conn2, in_response_to=None, relay_state=relay)
    assert redirect.startswith("https://idp.example.com/slo?SAMLResponse=")
    assert "RelayState=r-1" in redirect

    # A REVOKED link never sweeps (not authoritative).
    from app.integrations.models import ExternalIdentityLink as LinkModel

    row = (
        await db.execute(
            select(LinkModel).where(LinkModel.connection_ref == conn.id, LinkModel.subject == subject)
        )
    ).scalar_one()
    row.revoked_at = datetime.now(UTC)
    await db.flush()
    _, swept_rev, _ = await svc.handle_slo_request(
        connection_id=conn.id, raw_query=_signed_slo_query(subject)
    )
    assert swept_rev == 0
    row.revoked_at = None
    await db.flush()

    # Without an SLO URL the response redirect is None (plain confirmation).
    conn2.idp_slo_url = None
    await db.flush()
    assert svc.build_slo_response_redirect(conn2, in_response_to=None, relay_state=None) is None
    conn2.idp_slo_url = "https://idp.example.com/slo"
    await db.flush()

    # Unknown subject: clean success, 0 swept (no oracle).
    _, swept0, _ = await svc.handle_slo_request(
        connection_id=conn.id, raw_query=_signed_slo_query("never-seen")
    )
    assert swept0 == 0


@pytest.mark.asyncio
async def test_slo_rejects_unsigned_rogue_and_wrong_issuer(db):
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    svc = SamlService(db)

    async def expect_reject(query):
        with pytest.raises(AppError) as e:
            await svc.handle_slo_request(connection_id=conn.id, raw_query=query)
        assert e.value.code == "SSO_ASSERTION_INVALID"

    await expect_reject(_signed_slo_query("s", sign=False))          # logout-CSRF
    await expect_reject(_signed_slo_query("s", key_pem=ROGUE_KEY))    # rogue key
    await expect_reject(_signed_slo_query("s", issuer="https://rogue.example.com"))
    # BOTH SigAlg and Signature absent -> clean 401 AppError, never a
    # KeyError/500 (kills the skip-presence-check mutant).
    bare = "&".join(
        seg for seg in _signed_slo_query("s").split("&")
        if not seg.startswith(("SigAlg=", "Signature="))
    )
    await expect_reject(bare)

    # Signature present but SigAlg stripped -> refused (both params required).
    q = _signed_slo_query("s")
    no_alg = "&".join(seg for seg in q.split("&") if not seg.startswith("SigAlg="))
    await expect_reject(no_alg)
    # Unsupported SigAlg (rsa-sha1) refused even with a valid-shape signature.
    sha1 = q.replace("xmldsig-more%23rsa-sha256", "xmldsig%23rsa-sha1")
    await expect_reject(sha1)

    # A signed LogoutRESPONSE (wrong root element) is not a LogoutRequest.
    import zlib
    from urllib.parse import quote

    from cryptography.hazmat.primitives import hashes as _h
    from cryptography.hazmat.primitives import serialization as _ser
    from cryptography.hazmat.primitives.asymmetric import padding as _pad

    resp_xml = (
        f'<samlp:LogoutResponse xmlns:samlp="{SAMLP_NS}" xmlns:saml="{SAML_NS}" '
        f'ID="_X{uuid.uuid4().hex}" Version="2.0" '
        f'IssueInstant="{datetime.now(UTC).isoformat()}">'
        f"<saml:Issuer>{IDP_ENTITY}</saml:Issuer></samlp:LogoutResponse>"
    )
    deflated = zlib.compress(resp_xml.encode())[2:-4]
    base_q = (
        f"SAMLRequest={quote(base64.b64encode(deflated).decode(), safe='')}"
        "&SigAlg=" + quote("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256", safe="")
    )
    key = _ser.load_pem_private_key(
        IDP_KEY if isinstance(IDP_KEY, bytes) else IDP_KEY.encode(), password=None
    )
    sig = key.sign(base_q.encode(), _pad.PKCS1v15(), _h.SHA256())
    await expect_reject(base_q + "&Signature=" + quote(base64.b64encode(sig).decode(), safe=""))

    # A signed LogoutResponse CONTAINING a NameID must still be refused by
    # the root-tag check — otherwise it acts as a logout request.
    resp_with_nameid = (
        f'<samlp:LogoutResponse xmlns:samlp="{SAMLP_NS}" xmlns:saml="{SAML_NS}" '
        f'ID="_Y{uuid.uuid4().hex}" Version="2.0" '
        f'IssueInstant="{datetime.now(UTC).isoformat()}">'
        f"<saml:Issuer>{IDP_ENTITY}</saml:Issuer>"
        "<saml:NameID>victim-subject</saml:NameID></samlp:LogoutResponse>"
    )
    deflated2 = zlib.compress(resp_with_nameid.encode())[2:-4]
    base_q2 = (
        f"SAMLRequest={quote(base64.b64encode(deflated2).decode(), safe='')}"
        "&SigAlg=" + quote("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256", safe="")
    )
    sig2 = key.sign(base_q2.encode(), _pad.PKCS1v15(), _h.SHA256())
    await expect_reject(
        base_q2 + "&Signature=" + quote(base64.b64encode(sig2).decode(), safe="")
    )


@pytest.mark.asyncio
async def test_authn_redirect_purges_expired_replay_cache(db):
    """R165: a SAML-only tenant never hits the OIDC authorize purge, so
    build_authn_redirect sweeps expired login-state/replay-cache rows itself
    — old rows go, fresh rows (incl. the one it just minted) stay."""
    from datetime import UTC, datetime, timedelta

    from app.integrations.models.sso import SsoLoginState

    org, _u, _d = await _org(db)
    conn = await _saml_conn(db, org)

    stale = SsoLoginState(
        id="STALEROWREPLAYCACHE0000001",
        sso_connection_id=conn.id,
        nonce="assertion-replay-cache",
        expires_at=datetime.now(UTC) - timedelta(days=3),
        used_at=datetime.now(UTC) - timedelta(days=3),
    )
    fresh = SsoLoginState(
        id="FRESHROWREPLAYCACHE0000001",
        sso_connection_id=conn.id,
        nonce="assertion-replay-cache",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        used_at=datetime.now(UTC),
    )
    db.add_all([stale, fresh])
    await db.flush()

    await SamlService(db).build_authn_redirect(conn.id)

    assert await db.get(SsoLoginState, "STALEROWREPLAYCACHE0000001") is None
    assert await db.get(SsoLoginState, "FRESHROWREPLAYCACHE0000001") is not None


@pytest.mark.asyncio
async def test_connection_without_pinned_certs_rejects_even_valid_signatures(db):
    """R237 (unreached-branch pin): a connection whose pinned-cert list is
    empty must reject EVERY assertion with no_pinned_certificates — even one
    validly signed by a real IdP key. The danger this pins out: an empty
    x509_cert handed to signxml could fall back to the EMBEDDED KeyInfo cert
    (trust-whoever-signed-it). No prior test exercised the empty-cert branch."""
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    conn.idp_certificates = []  # cert list emptied (e.g. bad admin edit)
    await db.flush()
    email = f"np-{uuid.uuid4().hex[:6]}@{domain}"
    state = await _start(db, conn)
    signed = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    b64 = _wrap_response(signed)
    with pytest.raises(AppError) as e:
        await SamlService(db).handle_acs(
            connection_id=conn.id, saml_response_b64=b64, relay_state=state
        )
    # _invalid() is deliberately generic (401, reason only logged) — the
    # outcome that matters: the login is REJECTED, never resolved.
    assert e.value.status_code == 401


@pytest.mark.asyncio
async def test_unsolicited_assertion_without_inresponseto_rejected(db):
    """R240 (survivor pin): an assertion carrying NO InResponseTo —
    IdP-initiated SSO — must be rejected in v1 even when validly signed and
    a real outstanding request exists (the attacker may know a state id via
    RelayState, but only a response bound to the request is acceptable)."""
    import re as _re

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    email = f"un-{uuid.uuid4().hex[:6]}@{domain}"
    state = await _start(db, conn)  # a real outstanding request exists
    xml = _assertion_xml(in_response_to=state, email=email)
    # Strip the InResponseTo attribute BEFORE signing (it is inside the
    # signed subtree, so post-signature tampering would fail earlier).
    xml = _re.sub(r'InResponseTo="[^"]*" ', "", xml, count=1)
    assert "InResponseTo" not in xml
    b64 = _wrap_response(_sign_assertion(xml))
    with pytest.raises(AppError) as e:
        await SamlService(db).handle_acs(
            connection_id=conn.id, saml_response_b64=b64, relay_state=state
        )
    assert e.value.status_code == 401


@pytest.mark.asyncio
async def test_saml_request_id_single_use_and_connection_scoped(db):
    """R256 (survivor pins): the AuthnRequest state (InResponseTo target) is
    single-use AND bound to the connection that minted it.
    (1) A SECOND distinct assertion reusing an already-consumed InResponseTo
        is rejected even though its assertion ID is fresh (so the
        assertion-replay cache is NOT what catches it).
    (2) A request minted for connection A cannot satisfy an assertion
        presented to connection B."""
    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    email = f"ru-{uuid.uuid4().hex[:6]}@{domain}"

    state = await _start(db, conn)
    a1 = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    await SamlService(db).handle_acs(
        connection_id=conn.id, saml_response_b64=_wrap_response(a1), relay_state=state
    )
    # Fresh assertion ID, SAME consumed InResponseTo -> request already used.
    a2 = _sign_assertion(_assertion_xml(in_response_to=state, email=email))
    with pytest.raises(AppError) as reuse:
        await SamlService(db).handle_acs(
            connection_id=conn.id, saml_response_b64=_wrap_response(a2), relay_state=state
        )
    assert reuse.value.status_code == 401

    # Connection-scoped: state minted on conn, assertion presented to conn_b.
    conn_b = await _saml_conn(db, org)
    state_b_victim = await _start(db, conn)  # minted for conn, NOT conn_b
    ab = _sign_assertion(_assertion_xml(in_response_to=state_b_victim, email=email))
    with pytest.raises(AppError) as xconn:
        await SamlService(db).handle_acs(
            connection_id=conn_b.id, saml_response_b64=_wrap_response(ab),
            relay_state=state_b_victim,
        )
    assert xconn.value.status_code == 401


@pytest.mark.asyncio
async def test_slo_dtd_forbidden_even_when_signed(db):
    """R265 (survivor pin): a DTD-carrying LogoutRequest is refused even
    with a VALID IdP signature over the query — the doctype screen is not
    allowed to rot behind the signature layer."""
    import zlib
    from urllib.parse import quote

    from cryptography.hazmat.primitives import hashes as _h
    from cryptography.hazmat.primitives import serialization as _ser
    from cryptography.hazmat.primitives.asymmetric import padding as _pad

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)
    svc = SamlService(db)
    req = (
        "<!DOCTYPE foo [<!ENTITY bar \"x\">]>"
        f'<samlp:LogoutRequest xmlns:samlp="{SAMLP_NS}" xmlns:saml="{SAML_NS}" '
        f'ID="_LO{uuid.uuid4().hex}" Version="2.0" '
        f'IssueInstant="{datetime.now(UTC).isoformat()}">'
        f"<saml:Issuer>{IDP_ENTITY}</saml:Issuer>"
        "<saml:NameID>dtd-sub</saml:NameID>"
        "</samlp:LogoutRequest>"
    )
    deflated = zlib.compress(req.encode())[2:-4]
    base_q = (
        f"SAMLRequest={quote(base64.b64encode(deflated).decode(), safe='')}"
        "&SigAlg=" + quote("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256", safe="")
    )
    key = _ser.load_pem_private_key(
        IDP_KEY if isinstance(IDP_KEY, bytes) else IDP_KEY.encode(), password=None
    )
    sig = key.sign(base_q.encode(), _pad.PKCS1v15(), _h.SHA256())
    with pytest.raises(AppError) as e:
        await svc.handle_slo_request(
            connection_id=conn.id,
            raw_query=base_q + "&Signature=" + quote(base64.b64encode(sig).decode(), safe=""),
        )
    assert e.value.code == "SSO_ASSERTION_INVALID"


@pytest.mark.asyncio
async def test_saml_authorize_route_screens_open_redirect(db):
    """R272 (survivor pin): the /saml/authorize ROUTE drops absolute and
    scheme-relative return_to values before minting state (the OIDC twin was
    pinned; this one was not) — a crafted login link must not become an
    open redirect after the IdP round-trip."""
    from urllib.parse import parse_qs, urlsplit

    from app.integrations.api.sso import saml_authorize
    from app.integrations.models import SsoLoginState

    org, owner, domain = await _org(db)
    conn = await _saml_conn(db, org)

    async def minted_redirect(return_to):
        resp = await saml_authorize(connection=conn.id, return_to=return_to, db=db)
        q = parse_qs(urlsplit(resp.headers["location"]).query)
        state_id = q["RelayState"][0]
        row = await db.get(SsoLoginState, state_id)
        return row.redirect_to

    assert await minted_redirect("https://evil.example.com/phish") is None
    assert await minted_redirect("//evil.example.com/phish") is None
    assert await minted_redirect("/dashboard/orgs/X") == "/dashboard/orgs/X"
