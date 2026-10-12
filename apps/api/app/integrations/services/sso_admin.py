"""SSO connection admin CRUD (ADR-018 §5.2). Uniform-404 on cross-tenant."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    JIT_ALLOWED_ROLES,
    SSO_PROTOCOLS,
    SSO_STATUSES,
    SsoConnection,
)
from app.integrations.security import validate_egress_url
from app.integrations.services.sso_oidc import set_client_secret

MAX_SSO_CONNECTIONS_PER_ORG = 5


class SsoAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        org_id: str,
        *,
        protocol: str,
        oidc_issuer: str | None = None,
        oidc_client_id: str | None = None,
        oidc_client_secret: str | None = None,
        idp_entity_id: str | None = None,
        idp_sso_url: str | None = None,
        idp_metadata_url: str | None = None,
        idp_certificates: list[dict] | None = None,
        attribute_map: dict | None = None,
        allow_jit: bool = False,
        default_role: str = "student",
    ) -> SsoConnection:
        if protocol not in SSO_PROTOCOLS:
            raise AppError("SSO_PROTOCOL_INVALID", "protocol must be oidc|saml", 422)
        if default_role not in JIT_ALLOWED_ROLES:
            raise AppError("SSO_JIT_ROLE_INVALID", "default_role must be student|instructor", 422)
        if protocol == "oidc":
            if not oidc_issuer or not oidc_client_id:
                raise AppError(
                    "SSO_CONFIG_INVALID", "oidc_issuer and oidc_client_id required", 422
                )
            validate_egress_url(oidc_issuer)
        else:  # saml (P3b)
            if not idp_entity_id or not idp_sso_url:
                raise AppError(
                    "SSO_CONFIG_INVALID", "idp_entity_id and idp_sso_url required", 422
                )
            validate_egress_url(idp_sso_url)
            if idp_metadata_url:
                validate_egress_url(idp_metadata_url)
            certs = self._screen_certificates(idp_certificates)
            if not certs:
                raise AppError(
                    "SSO_CONFIG_INVALID", "at least one signing certificate required", 422
                )
        # R261 (R260 class): FOR UPDATE org lock makes the cap race-proof.
        from app.models.organization import Organization as _Org

        await self.db.execute(select(_Org.id).where(_Org.id == org_id).with_for_update())
        count = len(
            (
                await self.db.execute(
                    select(SsoConnection.id).where(SsoConnection.org_id == org_id)
                )
            ).all()
        )
        if count >= MAX_SSO_CONNECTIONS_PER_ORG:
            raise AppError("SSO_LIMIT_REACHED", "Too many SSO connections", 422)
        conn = SsoConnection(
            org_id=org_id,
            protocol=protocol,
            status="testing",
            oidc_issuer=(oidc_issuer or "").rstrip("/") or None,
            oidc_client_id=oidc_client_id,
            idp_entity_id=idp_entity_id,
            idp_sso_url=idp_sso_url,
            idp_metadata_url=idp_metadata_url,
            idp_certificates=(
                self._screen_certificates(idp_certificates) if protocol == "saml" else []
            ),
            attribute_map=attribute_map or {},
            allow_jit=allow_jit,
            default_role=default_role,
        )
        if oidc_client_secret:
            await set_client_secret(conn, oidc_client_secret)
        self.db.add(conn)
        await self.db.flush()
        await self.db.refresh(conn)
        return conn

    @staticmethod
    def _screen_certificates(certs: list[dict] | None) -> list[dict]:
        """Validate + fingerprint pinned certs. PEM must parse as X.509."""
        out: list[dict] = []
        for entry in certs or []:
            pem = (entry or {}).get("pem", "")
            if not isinstance(pem, str) or len(pem) > 10_000:
                raise AppError("SSO_CONFIG_INVALID", "bad certificate entry", 422)
            try:
                import hashlib

                from cryptography import x509

                cert = x509.load_pem_x509_certificate(pem.encode())
                fingerprint = hashlib.sha256(
                    cert.public_bytes_raw
                    if hasattr(cert, "public_bytes_raw")
                    else pem.encode()
                ).hexdigest()
            except Exception as exc:
                raise AppError("SSO_CONFIG_INVALID", "certificate does not parse", 422) from exc
            out.append(
                {
                    "pem": pem,
                    "fingerprint_sha256": fingerprint,
                    "not_after": cert.not_valid_after_utc.isoformat(),
                }
            )
        return out

    async def get(self, org_id: str, conn_id: str) -> SsoConnection:
        conn = await self.db.get(SsoConnection, conn_id)
        if conn is None or conn.org_id != org_id:
            raise AppError("SSO_CONNECTION_NOT_FOUND", "SSO connection not found", 404)
        return conn

    async def list(self, org_id: str) -> list[SsoConnection]:
        return list(
            (
                await self.db.execute(
                    select(SsoConnection)
                    .where(SsoConnection.org_id == org_id)
                    .order_by(SsoConnection.created_at)
                )
            ).scalars()
        )

    async def update(self, org_id: str, conn_id: str, **fields) -> SsoConnection:
        conn = await self.get(org_id, conn_id)
        secret = fields.pop("oidc_client_secret", None)
        status = fields.pop("status", None)
        if status is not None:
            if status not in SSO_STATUSES:
                raise AppError("SSO_CONFIG_INVALID", "invalid status", 422)
            # enforce_sso may only be flipped on an ACTIVE connection with a
            # break-glass member in place — checked below on the flag itself.
            conn.status = status
        if "default_role" in fields and fields["default_role"] is not None:
            if fields["default_role"] not in JIT_ALLOWED_ROLES:
                raise AppError("SSO_JIT_ROLE_INVALID", "default_role not allowed", 422)
            conn.default_role = fields.pop("default_role")
        if "oidc_issuer" in fields and fields["oidc_issuer"]:
            validate_egress_url(fields["oidc_issuer"])
            conn.oidc_issuer = fields.pop("oidc_issuer").rstrip("/")
        for key in ("oidc_client_id", "attribute_map", "allow_jit"):
            if key in fields and fields[key] is not None:
                setattr(conn, key, fields.pop(key))
        enforce = fields.pop("enforce_sso", None)
        if enforce is True and not conn.enforce_sso:
            await self._assert_break_glass_exists(org_id)
            conn.enforce_sso = True
        elif enforce is False:
            conn.enforce_sso = False
        if secret:
            await set_client_secret(conn, secret)
        await self.db.flush()
        return conn

    async def delete(self, org_id: str, conn_id: str) -> None:
        conn = await self.get(org_id, conn_id)
        await self.db.delete(conn)
        await self.db.flush()

    async def _assert_break_glass_exists(self, org_id: str) -> None:
        """Enforced SSO without a tested escape hatch is a lockout (§5.2).
        At minimum one active break-glass member must exist BEFORE the flag
        flips — the 90-day freshness rule applies at cert-rotation time."""
        from app.models.organization import MemberStatus, OrgMember

        row = (
            await self.db.execute(
                select(OrgMember.id).where(
                    OrgMember.org_id == org_id,
                    OrgMember.status == MemberStatus.ACTIVE,
                    OrgMember.is_break_glass.is_(True),
                )
            )
        ).first()
        if row is None:
            raise AppError(
                "BREAK_GLASS_UNVERIFIED",
                "Designate a break-glass member before enforcing SSO",
                409,
            )

    async def refresh_from_metadata(
        self, org_id: str, conn_id: str, *, egress=None
    ) -> dict:
        """R51: drive the never-driven idp_metadata_url column — fetch the
        IdP's SAML metadata and refresh the pinned signing certificates (and
        SSO URL / entity id when present). Rotation overlap comes from the
        metadata itself carrying old+new certs. Hardened parse: no DTD, no
        entity resolution, 1MB cap; every extracted URL is egress-screened.
        """
        from lxml import etree

        from app.integrations.security import (
            MAX_RESPONSE_BYTES,
            EgressClient,
            validate_egress_url,
        )

        conn = await self.get(org_id, conn_id)
        if conn.protocol != "saml" or not conn.idp_metadata_url:
            raise AppError("SSO_CONFIG_INVALID", "No SAML metadata URL configured", 422)
        validate_egress_url(conn.idp_metadata_url)
        egress = egress or EgressClient()
        resp = await egress.request("GET", conn.idp_metadata_url)
        if resp.status_code != 200:
            raise AppError("SSO_METADATA_FETCH_FAILED", f"metadata {resp.status_code}", 502)
        body = resp.content
        if len(body) > MAX_RESPONSE_BYTES:
            raise AppError("SSO_METADATA_FETCH_FAILED", "metadata too large", 502)
        parser = etree.XMLParser(resolve_entities=False, no_network=True, dtd_validation=False)
        try:
            root = etree.fromstring(body, parser=parser)
        except etree.XMLSyntaxError as exc:
            raise AppError("SSO_METADATA_INVALID", "metadata XML invalid", 422) from exc
        if root.getroottree().docinfo.doctype:
            raise AppError("SSO_METADATA_INVALID", "DTD forbidden", 422)
        md_ns = "urn:oasis:names:tc:SAML:2.0:metadata"
        ds_ns = "http://www.w3.org/2000/09/xmldsig#"
        entity_id = root.get("entityID")
        idp = root.find(f"{{{md_ns}}}IDPSSODescriptor")
        if idp is None:
            raise AppError("SSO_METADATA_INVALID", "No IDPSSODescriptor", 422)
        pems: list[dict] = []
        for kd in idp.findall(f"{{{md_ns}}}KeyDescriptor"):
            use = kd.get("use")
            if use not in (None, "signing"):
                continue  # encryption keys never verify assertions
            for cert_el in kd.findall(f".//{{{ds_ns}}}X509Certificate"):
                b64 = "".join((cert_el.text or "").split())
                if not b64:
                    continue
                lines = [b64[i : i + 64] for i in range(0, len(b64), 64)]
                pems.append(
                    {
                        "pem": "-----BEGIN CERTIFICATE-----\n"
                        + "\n".join(lines)
                        + "\n-----END CERTIFICATE-----\n"
                    }
                )
        if not pems:
            raise AppError("SSO_METADATA_INVALID", "No signing certificates", 422)
        screened = self._screen_certificates(pems)  # parses + stamps not_after
        sso_url = None
        for svc in idp.findall(f"{{{md_ns}}}SingleSignOnService"):
            if svc.get("Binding", "").endswith("HTTP-Redirect") and svc.get("Location"):
                sso_url = svc.get("Location")
                break
        slo_url = None
        for svc in idp.findall(f"{{{md_ns}}}SingleLogoutService"):
            if svc.get("Binding", "").endswith("HTTP-Redirect") and svc.get("Location"):
                slo_url = svc.get("Location")
                break
        # R252 (R251 class — SAML metadata mix-up defense): a document whose
        # entityID differs from the CONFIGURED one must be rejected, not
        # adopted — otherwise a wrong document at the metadata URL (multi-
        # tenant host, path confusion) silently re-points this connection at
        # a different IdP: certs, SSO URL and the issuer check would all
        # follow the imposter. entityID is only adopted when previously
        # unset (bootstrap convenience).
        if (
            entity_id
            and conn.idp_entity_id
            and str(entity_id).strip() != conn.idp_entity_id.strip()
        ):
            raise AppError(
                "SSO_METADATA_INVALID",
                "metadata entityID does not match the configured IdP entity",
                422,
            )
        before = {(c.get("pem") or "").strip() for c in (conn.idp_certificates or [])}
        after = {(c.get("pem") or "").strip() for c in screened}
        conn.idp_certificates = screened
        if entity_id:
            conn.idp_entity_id = str(entity_id)[:500]
        if sso_url:
            validate_egress_url(sso_url)
            conn.idp_sso_url = str(sso_url)[:500]
        if slo_url:
            validate_egress_url(slo_url)
            conn.idp_slo_url = str(slo_url)[:500]
        await self.db.flush()
        return {"certificates": len(screened), "rotated": before != after}

    async def sweep_expiring_certificates(self, *, days: int = 30) -> int:
        """Worker cron (ADR §5.2 R19): emit a daily-deduped mesh event for
        every active SAML connection with a pinned cert expiring within
        ``days`` — rotation reminders are observable + webhook-able."""
        from datetime import UTC, datetime, timedelta

        from app.integrations.models import IntegrationEvent

        conns = (
            await self.db.execute(
                select(SsoConnection).where(
                    SsoConnection.protocol == "saml",
                    SsoConnection.status.in_(("testing", "active")),
                )
            )
        ).scalars().all()
        now = datetime.now(UTC)
        emitted = 0
        for conn in conns:
            soonest: datetime | None = None
            for cert in conn.idp_certificates or []:
                raw = cert.get("not_after")
                if not raw:
                    continue
                try:
                    exp = datetime.fromisoformat(str(raw))
                except ValueError:
                    continue
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=UTC)
                if soonest is None or exp < soonest:
                    soonest = exp
            if soonest is None or soonest - now > timedelta(days=days):
                continue
            # Daily dedup: skip when we already alerted in the last 23h.
            recent = (
                await self.db.execute(
                    select(IntegrationEvent.id)
                    .where(
                        IntegrationEvent.org_id == conn.org_id,
                        IntegrationEvent.type
                        == "com.openskill.integration.sso.cert_expiring.v1",
                        IntegrationEvent.subject == conn.id,
                        IntegrationEvent.time > now - timedelta(hours=23),
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
            if recent is not None:
                continue
            try:
                from app.integrations.facade import emit_event

                await emit_event(
                    self.db,
                    conn.org_id,
                    "integration.sso.cert_expiring",
                    subject=conn.id,
                    data={
                        "sso_connection_id": conn.id,
                        "not_after": soonest.isoformat(),
                        "days_left": max(0, (soonest - now).days),
                    },
                )
                emitted += 1
            except Exception:  # fail-safe sweep
                import structlog

                structlog.get_logger().warning(
                    "cert_expiry_emit_failed", sso_connection_id=conn.id
                )
        return emitted

    async def set_break_glass(
        self, org_id: str, member_user_id: str, *, enabled: bool, actor_role
    ) -> None:
        """Owner-only; max 2 per org."""
        from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole

        if actor_role != OrgRole.OWNER:
            raise AppError("FORBIDDEN", "Only the owner can manage break-glass", 403)
        # R260: serialize the count-then-set under a FOR UPDATE org lock —
        # two concurrent enables at cap-1 would otherwise BOTH count 1 < 2
        # and yield three designees (the cap bounds the password-bypass
        # surface under enforced SSO, so it must hold under races too).
        await self.db.execute(
            select(Organization.id).where(Organization.id == org_id).with_for_update()
        )
        member = (
            await self.db.execute(
                select(OrgMember).where(
                    OrgMember.org_id == org_id,
                    OrgMember.user_id == member_user_id,
                    OrgMember.status == MemberStatus.ACTIVE,
                )
            )
        ).scalar_one_or_none()
        if member is None:
            raise AppError("MEMBER_NOT_FOUND", "Member not found", 404)
        if enabled:
            current = (
                await self.db.execute(
                    select(OrgMember.id).where(
                        OrgMember.org_id == org_id,
                        OrgMember.is_break_glass.is_(True),
                        OrgMember.status == MemberStatus.ACTIVE,
                    )
                )
            ).all()
            if len(current) >= 2 and not member.is_break_glass:
                raise AppError("BREAK_GLASS_LIMIT", "At most 2 break-glass members", 422)
        member.is_break_glass = enabled
        await self.db.flush()
