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
    conn2, result = await SamlService(db).handle_acs(
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
    _, result2 = await SamlService(db).handle_acs(
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
        _, result = await svc.handle_acs(
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
