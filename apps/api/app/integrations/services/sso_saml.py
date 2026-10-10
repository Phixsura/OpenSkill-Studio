"""SAML 2.0 Service Provider (ADR-018 §5.2, P3b).

XML-DSIG verification via signxml (pure-python XML security; no xmlsec1
native dependency). The §5.2 validation sequence — every step is a test:

  schema-sane parse (no DTD/entities; lxml resolve_entities off) ->
  SIGNATURE verified against THIS CONNECTION's pinned certs only (signxml
  enforces enveloped-signature reference semantics — the XSW "valid
  signature elsewhere, attributes from an unsigned clone" family fails
  because only the SIGNED subtree is returned and consumed) ->
  issuer matches -> audience == SP entity id -> NotBefore/NotOnOrAfter
  (90s skew) -> InResponseTo matches an outstanding single-use request ->
  assertion ID unseen (DB-backed replay cache) -> RelayState allowlist.

Validation failures surface as one public code (SSO_ASSERTION_INVALID);
the precise reason goes to logs only.
"""

from __future__ import annotations

import base64
import secrets
from datetime import UTC, datetime, timedelta

import structlog
from lxml import etree
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppError
from app.integrations.models import SsoConnection, SsoLoginState
from app.integrations.services.identity import (
    IdentityService,
    ResolutionResult,
    VerifiedExternalIdentity,
)

log = structlog.get_logger()

NS = {
    "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
}
CLOCK_SKEW = timedelta(seconds=90)
STATE_TTL = timedelta(minutes=10)
MAX_RESPONSE_BYTES = 262_144  # 256 KB


def _invalid(reason: str) -> AppError:
    log.warning("sso_saml_invalid", reason=reason)
    return AppError("SSO_ASSERTION_INVALID", "SSO response could not be validated", 401)


def sp_entity_id() -> str:
    return f"{settings.public_base_url}/api/v1/sso/saml/metadata"


def acs_url(connection_id: str) -> str:
    return f"{settings.public_base_url}/api/v1/sso/saml/acs/{connection_id}"


def sp_metadata_xml(connection_id: str | None = None) -> str:
    """Minimal SP metadata (we require signed assertions; no SP signing yet)."""
    acs = acs_url(connection_id or "{connection_id}")
    return (
        '<?xml version="1.0"?>'
        f'<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" '
        f'entityID="{sp_entity_id()}">'
        '<md:SPSSODescriptor AuthnRequestsSigned="false" '
        'WantAssertionsSigned="true" '
        'protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">'
        f'<md:AssertionConsumerService '
        'Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" '
        f'Location="{acs}" index="0"/>'
        "</md:SPSSODescriptor></md:EntityDescriptor>"
    )


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SamlService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _connection(self, connection_id: str) -> SsoConnection:
        conn = await self.db.get(SsoConnection, connection_id)
        if conn is None or conn.protocol != "saml" or conn.status not in ("testing", "active"):
            raise AppError("SSO_CONNECTION_NOT_FOUND", "SSO connection not found", 404)
        return conn

    # ── AuthnRequest (SP-initiated; redirect binding) ──

    async def build_authn_redirect(self, connection_id: str) -> str:
        import zlib
        from urllib.parse import urlencode

        conn = await self._connection(connection_id)
        if not conn.idp_sso_url:
            raise AppError("SSO_CONFIG_INVALID", "idp_sso_url not configured", 422)
        state = SsoLoginState(
            sso_connection_id=conn.id,
            nonce=secrets.token_urlsafe(24)[:64],
            expires_at=datetime.now(UTC) + STATE_TTL,
        )
        self.db.add(state)
        await self.db.flush()
        issue_instant = datetime.now(UTC).isoformat()
        authn = (
            f'<samlp:AuthnRequest xmlns:samlp="{NS["samlp"]}" xmlns:saml="{NS["saml"]}" '
            f'ID="_{state.id}" Version="2.0" IssueInstant="{issue_instant}" '
            f'Destination="{conn.idp_sso_url}" '
            f'AssertionConsumerServiceURL="{acs_url(conn.id)}" '
            'ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">'
            f"<saml:Issuer>{sp_entity_id()}</saml:Issuer>"
            "</samlp:AuthnRequest>"
        )
        deflated = zlib.compress(authn.encode())[2:-4]  # raw DEFLATE per binding
        q = urlencode(
            {
                "SAMLRequest": base64.b64encode(deflated).decode(),
                "RelayState": state.id,
            }
        )
        return f"{conn.idp_sso_url}?{q}"

    # ── ACS (the validation core) ──

    async def _consume_request_id(self, state_value: str, conn_id: str) -> None:
        """InResponseTo must be an outstanding request of THIS connection —
        single-use, TTL'd (same discipline as the OIDC state row)."""
        res = await self.db.execute(
            update(SsoLoginState)
            .where(
                SsoLoginState.id == state_value,
                SsoLoginState.sso_connection_id == conn_id,
                SsoLoginState.used_at.is_(None),
                SsoLoginState.expires_at > datetime.now(UTC),
            )
            .values(used_at=datetime.now(UTC))
            .returning(SsoLoginState.id)
        )
        if res.scalar_one_or_none() is None:
            raise _invalid("in_response_to_unknown_used_or_expired")

    async def _assert_id_unseen(
        self, conn_id: str, assertion_id: str, not_on_or_after: datetime
    ) -> None:
        """Replay cache: assertion IDs are single-use until expiry. Reuses the
        login-state table (deterministic 26-char key hashed from the id)."""
        import hashlib

        key = hashlib.sha256(assertion_id.encode()).hexdigest()[:26].upper()
        existing = await self.db.get(SsoLoginState, key)
        if existing is not None:
            raise _invalid("assertion_replayed")
        self.db.add(
            SsoLoginState(
                id=key,
                sso_connection_id=conn_id,
                nonce="assertion-replay-cache",
                expires_at=not_on_or_after,
                used_at=datetime.now(UTC),
            )
        )

    def _verify_signature(self, conn: SsoConnection, xml_bytes: bytes) -> etree._Element:
        """Return the VERIFIED subtree only (signxml XMLVerifier). Certs are
        pinned per connection — never a shared trust store (§5.2 rule 2)."""
        from signxml import XMLVerifier

        certs = [c.get("pem", "") for c in (conn.idp_certificates or []) if c.get("pem")]
        if not certs:
            raise _invalid("no_pinned_certificates")
        parser = etree.XMLParser(resolve_entities=False, no_network=True, dtd_validation=False)
        try:
            root = etree.fromstring(xml_bytes, parser=parser)
        except etree.XMLSyntaxError as exc:
            raise _invalid("xml_parse_failed") from exc
        if root.getroottree().docinfo.doctype:
            raise _invalid("dtd_forbidden")
        last_exc: Exception | None = None
        for pem in certs:
            try:
                verified = XMLVerifier().verify(root, x509_cert=pem)
                return verified.signed_xml  # ONLY the signed subtree is trusted
            except Exception as exc:  # try the next pinned cert (rotation overlap)
                last_exc = exc
        raise _invalid(f"signature_invalid:{type(last_exc).__name__}")

    async def handle_acs(
        self, *, connection_id: str, saml_response_b64: str, relay_state: str | None
    ) -> tuple[SsoConnection, ResolutionResult]:
        conn = await self._connection(connection_id)
        if len(saml_response_b64) > MAX_RESPONSE_BYTES:
            raise _invalid("response_too_large")
        try:
            xml_bytes = base64.b64decode(saml_response_b64, validate=True)
        except Exception as exc:
            raise _invalid("base64_invalid") from exc
        if len(xml_bytes) > MAX_RESPONSE_BYTES:
            raise _invalid("response_too_large")

        signed = self._verify_signature(conn, xml_bytes)
        # The verified subtree may be the Response (enveloped at root) or the
        # Assertion. Locate the assertion WITHIN the signed subtree only.
        if signed.tag == f"{{{NS['saml']}}}Assertion":
            assertion = signed
        else:
            assertion = signed.find(f"{{{NS['saml']}}}Assertion")
        if assertion is None:
            raise _invalid("no_signed_assertion")

        issuer = assertion.findtext(f"{{{NS['saml']}}}Issuer", default="").strip()
        if conn.idp_entity_id and issuer != conn.idp_entity_id:
            raise _invalid("issuer_mismatch")

        conditions = assertion.find(f"{{{NS['saml']}}}Conditions")
        if conditions is None:
            raise _invalid("no_conditions")
        now = datetime.now(UTC)
        nb, noa = conditions.get("NotBefore"), conditions.get("NotOnOrAfter")
        try:
            if nb and now < _parse_time(nb) - CLOCK_SKEW:
                raise _invalid("not_yet_valid")
            if not noa:
                raise _invalid("no_expiry")
            expiry = _parse_time(noa)
            if now >= expiry + CLOCK_SKEW:
                raise _invalid("expired")
        except ValueError as exc:
            raise _invalid("bad_timestamps") from exc
        audience = conditions.findtext(
            f"{{{NS['saml']}}}AudienceRestriction/{{{NS['saml']}}}Audience", default=""
        ).strip()
        if audience != sp_entity_id():
            raise _invalid("audience_mismatch")

        # InResponseTo: strip the AuthnRequest's '_' prefix to the state id.
        subject_conf = assertion.find(
            f"{{{NS['saml']}}}Subject/{{{NS['saml']}}}SubjectConfirmation/"
            f"{{{NS['saml']}}}SubjectConfirmationData"
        )
        in_response_to = (subject_conf.get("InResponseTo") if subject_conf is not None else None) or ""
        if not in_response_to.startswith("_"):
            raise _invalid("unsolicited_response")  # IdP-initiated not supported v1
        await self._consume_request_id(in_response_to[1:], conn.id)

        assertion_id = assertion.get("ID", "")
        if not assertion_id:
            raise _invalid("no_assertion_id")
        await self._assert_id_unseen(conn.id, assertion_id, expiry)

        if relay_state is not None and relay_state != in_response_to[1:]:
            raise _invalid("relay_state_mismatch")

        name_id = assertion.findtext(
            f"{{{NS['saml']}}}Subject/{{{NS['saml']}}}NameID", default=""
        ).strip()
        if not name_id:
            raise _invalid("no_name_id")

        attrs: dict[str, str] = {}
        for attr in assertion.findall(
            f"{{{NS['saml']}}}AttributeStatement/{{{NS['saml']}}}Attribute"
        ):
            name = attr.get("Name", "")
            value = attr.findtext(f"{{{NS['saml']}}}AttributeValue", default="")
            if name:
                attrs[name] = value
        amap = conn.attribute_map or {}
        email = attrs.get(amap.get("email", "email")) or (
            name_id if "@" in name_id else None
        )
        display = attrs.get(amap.get("display_name", "displayName"))

        ident = VerifiedExternalIdentity(
            org_id=conn.org_id,
            source="sso",
            connection_ref=conn.id,
            subject=name_id,
            email=email,
            # The org's IdP signed this assertion with the pinned cert — the
            # same trust root as OIDC email_verified.
            email_verified=bool(email),
            display_name=display,
        )
        result = await IdentityService(self.db).resolve(
            ident, allow_jit=conn.allow_jit, jit_role=conn.default_role
        )
        return conn, result
