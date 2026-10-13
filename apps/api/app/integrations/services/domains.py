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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.services.domains import check_reserved, get_verifier, normalize_hostname
from app.exceptions import AppError
from app.integrations.models import PUBLIC_EMAIL_DOMAINS, OrgDomain

log = structlog.get_logger()

MAX_DOMAINS_PER_ORG = 20


def normalized_email_domain(email: str) -> str:
    """R319: an email's domain in the SAME canonical form claim() stores
    (IDNA/UTS46 punycode via normalize_hostname). The claim path encoded
    'школа.рф' as xn--80a..., but every email-domain comparison used a bare
    .lower() — IDN tenants' SSO discovery, the enforce gate and JIT email
    matching all silently un-matched. Tolerant: unparseable -> "" (callers
    treat as no-match, never 500 on a hostile address)."""
    if "@" not in (email or ""):
        return ""
    raw = email.rsplit("@", 1)[-1].strip().lower().rstrip(".")
    if not raw:
        return ""
    if raw.isascii():
        return raw
    try:
        return normalize_hostname(raw)
    except Exception:
        return ""


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
        # R207 (same class as webhook defect #102): the cap COUNT and the
        # duplicate-claim SELECT below are both TOCTOU under concurrency —
        # lock the Org row first so same-org claimers serialize, making the
        # cap exact and the dup check race-free against uq_intg_domain_org
        # (whose unique-violation loser would otherwise 500 and poison the
        # session at the bare flush).
        from app.models.organization import Organization as _Org

        await self.db.execute(select(_Org.id).where(_Org.id == org_id).with_for_update())
        count = len(
            (await self.db.execute(select(OrgDomain.id).where(OrgDomain.org_id == org_id))).all()
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
                select(OrgDomain).where(OrgDomain.org_id == org_id, OrgDomain.domain == domain)
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
        try:
            async with self.db.begin_nested():
                # add INSIDE the savepoint (R111): added-before-nested would
                # survive the rollback and poison the session.
                self.db.add(row)
                await self.db.flush()
        except IntegrityError:
            # uq_intg_domain_org loser (belt to the org-lock braces above):
            # someone claimed it concurrently — idempotent return of theirs.
            dup = (
                await self.db.execute(
                    select(OrgDomain).where(OrgDomain.org_id == org_id, OrgDomain.domain == domain)
                )
            ).scalar_one()
            return dup
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
        # Partial unique index is the authoritative race guard. The flush
        # runs in a SAVEPOINT (R113): a unique-violation loser must not
        # poison the caller's session (bare flush => PendingRollbackError on
        # next use).
        row.status = "verified"
        row.verified_at = datetime.now(UTC)
        try:
            async with self.db.begin_nested():
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

    async def sweep_pending(self, *, expire_days: int = 7) -> int:
        """Worker cron (ADR §5.1): poll pending domains against DNS; verify
        on success, fail after the expiry window. Returns changed count."""

        now = datetime.now(UTC)
        pending = (
            (
                await self.db.execute(
                    select(OrgDomain).where(OrgDomain.status == "pending").limit(200)
                )
            )
            .scalars()
            .all()
        )
        changed = 0
        verifier = get_verifier()
        for row in pending:
            row.last_checked_at = now
            if (now - (row.created_at or now)).days >= expire_days:
                row.status = "failed"
                changed += 1
                continue
            try:
                ok = await verifier.verify(row.domain, row.verification_token)
            except Exception:  # DNS hiccup — try again next sweep
                continue
            if not ok:
                continue
            # R402: PRE-CHECK the partial-unique winner before flipping to
            # verified. Relying on the IntegrityError + savepoint rollback
            # alone poisoned the whole async session when TWO orgs in the
            # SAME sweep batch both verified the same domain (asyncpg marks
            # the transaction failed; the per-row commit then raised
            # PendingRollbackError and aborted the rest of the sweep). The
            # savepoint stays as a belt for the true concurrent race.
            other = (
                await self.db.execute(
                    select(OrgDomain.id).where(
                        OrgDomain.domain == row.domain,
                        OrgDomain.status == "verified",
                        OrgDomain.org_id != row.org_id,
                    )
                )
            ).scalar_one_or_none()
            if other is not None:
                row.status = "failed"
                changed += 1
                await self.db.commit()
                continue
            row.status = "verified"
            row.verified_at = now
            # R428: capture the id BEFORE any rollback — rollback() expires
            # the instance, and `row.id` would then lazy-load synchronously
            # inside the except arm (MissingGreenlet), crashing the very
            # recovery that was supposed to keep the sweep alive.
            row_id = row.id
            try:
                async with self.db.begin_nested():
                    await self.db.flush()
                changed += 1
                await self.db.commit()
            except Exception:
                # True concurrent race (another process verified between the
                # pre-check and the flush) — recover the session, then mark
                # failed in a fresh transaction.
                await self.db.rollback()
                refreshed = await self.db.get(OrgDomain, row_id)
                if refreshed is not None and refreshed.status == "pending":
                    refreshed.status = "failed"
                    await self.db.commit()
        # Trailing writes (failed statuses, last_checked_at) are constraint-
        # free, but guard anyway so one poisoned row can never abort the
        # whole sweep (R113 hardening).
        try:
            async with self.db.begin_nested():
                await self.db.flush()
        except Exception:
            await self.db.rollback()
        return changed

    async def org_for_email_domain(self, email: str) -> str | None:
        """IdP discovery: the single org holding the VERIFIED domain of this
        email, or None. Freemail domains never route."""
        domain = normalized_email_domain(email)  # R319: IDNA-consistent
        if not domain or domain in PUBLIC_EMAIL_DOMAINS:
            return None
        row = await self.db.execute(
            select(OrgDomain.org_id).where(
                OrgDomain.domain == domain, OrgDomain.status == "verified"
            )
        )
        return row.scalar_one_or_none()
