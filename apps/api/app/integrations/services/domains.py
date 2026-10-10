"""Org domain claims + DNS TXT verification (ADR-018 §5.1).

Reuses the controlplane verifier adapters (mock/dns switch via
settings.domain_verifier) and hostname normalization — the SSO domain layer
adds the freemail denylist, the global one-verified-holder rule, and mesh
audit events.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.services.domains import check_reserved, get_verifier, normalize_hostname
from app.exceptions import AppError
from app.integrations.models import PUBLIC_EMAIL_DOMAINS, OrgDomain

log = structlog.get_logger()

MAX_DOMAINS_PER_ORG = 20


class OrgDomainService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def claim(self, org_id: str, raw_domain: str) -> OrgDomain:
        domain = normalize_hostname(raw_domain)
        check_reserved(domain)
        if domain in PUBLIC_EMAIL_DOMAINS:
            raise AppError(
                "DOMAIN_NOT_ELIGIBLE",
                "Public mailbox domains cannot anchor an organization",
                422,
            )
        count = len(
            (
                await self.db.execute(select(OrgDomain.id).where(OrgDomain.org_id == org_id))
            ).all()
        )
        if count >= MAX_DOMAINS_PER_ORG:
            raise AppError("DOMAIN_LIMIT_REACHED", "Too many domains for this org", 422)
        # Another org VERIFIED it -> explicit conflict (not an oracle: domain
        # ownership is public information by definition).
        other = (
            await self.db.execute(
                select(OrgDomain.id).where(
                    OrgDomain.domain == domain,
                    OrgDomain.status == "verified",
                    OrgDomain.org_id != org_id,
                )
            )
        ).scalar_one_or_none()
        if other is not None:
            raise AppError(
                "DOMAIN_ALREADY_VERIFIED", "Domain is verified by another organization", 409
            )
        dup = (
            await self.db.execute(
                select(OrgDomain).where(
                    OrgDomain.org_id == org_id, OrgDomain.domain == domain
                )
            )
        ).scalar_one_or_none()
        if dup is not None:
            return dup  # idempotent re-claim returns the existing row
        row = OrgDomain(
            org_id=org_id,
            domain=domain,
            status="pending",
            verification_token=f"osks-verify-{secrets.token_hex(16)}",
        )
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def get(self, org_id: str, domain_id: str) -> OrgDomain:
        row = await self.db.get(OrgDomain, domain_id)
        if row is None or row.org_id != org_id:
            raise AppError("DOMAIN_NOT_FOUND", "Domain not found", 404)
        return row

    async def list(self, org_id: str) -> list[OrgDomain]:
        return list(
            (
                await self.db.execute(
                    select(OrgDomain)
                    .where(OrgDomain.org_id == org_id)
                    .order_by(OrgDomain.created_at)
                )
            ).scalars()
        )

    async def delete(self, org_id: str, domain_id: str) -> None:
        row = await self.get(org_id, domain_id)
        await self.db.delete(row)
        await self.db.flush()

    async def verify(self, org_id: str, domain_id: str) -> OrgDomain:
        row = await self.get(org_id, domain_id)
        row.last_checked_at = datetime.now(UTC)
        if row.status == "verified":
            return row
        ok = await get_verifier().verify(row.domain, row.verification_token)
        if not ok:
            raise AppError(
                "DOMAIN_VERIFY_FAILED",
                "TXT record not found or does not match the verification token",
                422,
            )
        # Partial unique index is the authoritative race guard.
        row.status = "verified"
        row.verified_at = datetime.now(UTC)
        try:
            await self.db.flush()
        except Exception as exc:
            raise AppError(
                "DOMAIN_ALREADY_VERIFIED", "Domain is verified by another organization", 409
            ) from exc
        log.info("org_domain_verified", org_id=org_id, domain=row.domain)
        return row

    async def verified_domains(self, org_id: str) -> set[str]:
        rows = await self.db.execute(
            select(OrgDomain.domain).where(
                OrgDomain.org_id == org_id, OrgDomain.status == "verified"
            )
        )
        return {d for (d,) in rows.all()}

    async def org_for_email_domain(self, email: str) -> str | None:
        """IdP discovery: the single org holding the VERIFIED domain of this
        email, or None. Freemail domains never route."""
        domain = email.rsplit("@", 1)[-1].strip().lower().rstrip(".")
        if not domain or domain in PUBLIC_EMAIL_DOMAINS:
            return None
        row = await self.db.execute(
            select(OrgDomain.org_id).where(
                OrgDomain.domain == domain, OrgDomain.status == "verified"
            )
        )
        return row.scalar_one_or_none()
