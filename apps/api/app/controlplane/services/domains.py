"""Custom domains: normalization, verification adapters, TLS adapters,
site-context resolution (ADR-014 §10.2)."""

import hashlib
import ipaddress
import secrets
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.branding import TenantBranding, TenantDomain
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()

MAX_VERIFY_ATTEMPTS = 3
VERIFY_RECORD_PREFIX = "_openskill-verify"


# ── Normalization + reserved checks (pure; unit-tested) ──────


def normalize_hostname(raw: str) -> str:
    """lowercase, strip scheme/port/trailing dot, IDNA punycode."""
    host = raw.strip().lower()
    for prefix in ("https://", "http://"):
        if host.startswith(prefix):
            host = host[len(prefix) :]
    host = host.split("/")[0].split(":")[0].rstrip(".")
    if not host or len(host) > 253:
        raise AppError("DOMAIN_INVALID", "Invalid hostname", 422)
    try:
        host = host.encode("idna").decode("ascii")
    except (UnicodeError, UnicodeDecodeError) as exc:
        raise AppError("DOMAIN_INVALID", "Hostname cannot be IDNA-encoded", 422) from exc
    labels = host.split(".")
    if len(labels) < 2:
        raise AppError("DOMAIN_INVALID", "Single-label hostnames are not allowed", 422)
    for label in labels:
        if not label or len(label) > 63 or label.startswith("-") or label.endswith("-"):
            raise AppError("DOMAIN_INVALID", "Invalid hostname label", 422)
        if not all(c.isalnum() or c == "-" for c in label):
            raise AppError("DOMAIN_INVALID", "Invalid hostname characters", 422)
    return host


def check_reserved(host: str) -> None:
    """Platform base domains, IP literals, localhost — rejected."""
    try:
        ipaddress.ip_address(host)
        raise AppError("DOMAIN_RESERVED", "IP addresses cannot be custom domains", 422)
    except ValueError:
        pass
    if host == "localhost" or host.endswith(".localhost"):
        raise AppError("DOMAIN_RESERVED", "Reserved hostname", 422)
    for base in settings.platform_base_domains:
        # R79[1]: JSON env parsing preserves whitespace inside entries —
        # ' openskill.app' never matched, silently unreserving the platform
        # apex and every subdomain (takeover of app.openskill.app etc.).
        base = base.strip().lower().lstrip(".")
        if not base:
            continue
        if host == base or host.endswith(f".{base}"):
            raise AppError("DOMAIN_RESERVED", "This domain is reserved by the platform", 422)
    # Punycode homographs: warn + audit-visible, not rejected (legit IDNs exist)
    if any(label.startswith("xn--") for label in host.split(".")):
        log.warning("cp_domain_punycode", host=host)


# ── Verifier adapters ────────────────────────────────────────


class DomainVerifierBase(ABC):
    @abstractmethod
    async def verify(self, hostname: str, raw_token: str) -> bool: ...


class MockDomainVerifier(DomainVerifierBase):
    """dev/test: tokens starting 'ok-' pass. Selected via settings."""

    async def verify(self, hostname: str, raw_token: str) -> bool:
        return raw_token.startswith("ok-")


class DnsTxtVerifier(DomainVerifierBase):
    """TXT record at _openskill-verify.{host} must equal the raw token."""

    async def verify(self, hostname: str, raw_token: str) -> bool:
        import asyncio

        import dns.resolver

        def _lookup() -> bool:
            try:
                answers = dns.resolver.resolve(
                    f"{VERIFY_RECORD_PREFIX}.{hostname}", "TXT", lifetime=5
                )
                for answer in answers:
                    txt = b"".join(answer.strings).decode(errors="replace")
                    if txt == raw_token:
                        return True
            except Exception:  # noqa: BLE001 — NXDOMAIN/timeout = not verified
                return False
            return False

        return await asyncio.get_running_loop().run_in_executor(None, _lookup)


def get_verifier() -> DomainVerifierBase:
    return DnsTxtVerifier() if settings.domain_verifier == "dns" else MockDomainVerifier()


# ── TLS provisioner adapters (real ACME out of scope, issue §7) ──


class TlsProvisionerBase(ABC):
    @abstractmethod
    async def provision(self, hostname: str) -> dict: ...

    @abstractmethod
    async def status(self, hostname: str, ref: str | None) -> str: ...


class NullTlsProvisioner(TlsProvisionerBase):
    """Default: TLS terminates at the deployment proxy — unmanaged."""

    async def provision(self, hostname: str) -> dict:
        return {"tls_status": "unmanaged", "tls_ref": None}

    async def status(self, hostname: str, ref: str | None) -> str:
        return "unmanaged"


class MockTlsProvisioner(TlsProvisionerBase):
    async def provision(self, hostname: str) -> dict:
        return {"tls_status": "active", "tls_ref": f"mock-cert-{hostname}"}

    async def status(self, hostname: str, ref: str | None) -> str:
        return "active"


def get_tls_provisioner() -> TlsProvisionerBase:
    return MockTlsProvisioner() if settings.tls_provisioner == "mock" else NullTlsProvisioner()


# ── Domain lifecycle ─────────────────────────────────────────


async def create_domain(
    db: AsyncSession, *, tenant_id: str, hostname: str, actor: Actor
) -> tuple[TenantDomain, str]:
    """Returns (domain, RAW verification token) — token shown once."""
    host = normalize_hostname(hostname)
    check_reserved(host)
    taken = (
        await db.execute(select(TenantDomain.id).where(TenantDomain.hostname == host).limit(1))
    ).scalar_one_or_none()
    if taken is not None:
        # Uniform message — never reveals WHICH tenant holds it
        raise AppError("DOMAIN_TAKEN", "This domain is already registered", 409)
    # Mock verifier passes tokens prefixed "ok-": issue such tokens in mock
    # mode so the dev/E2E flow can complete without DNS. The sha256-hash
    # equality check still runs first, so forged "ok-" tokens are rejected.
    prefix = "ok-" if settings.domain_verifier == "mock" else "openskill-verify-"
    raw_token = f"{prefix}{secrets.token_urlsafe(24)}"
    domain = TenantDomain(
        tenant_id=tenant_id,
        hostname=host,
        verification_token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        created_by=actor.user_id,
    )
    db.add(domain)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="domain.created",
        target_type="tenant_domain",
        target_id=domain.id,
        tenant_id=tenant_id,
        after={"hostname": host},
    )
    return domain, raw_token


async def verify_domain(
    db: AsyncSession, domain: TenantDomain, raw_token: str, *, actor: Actor
) -> TenantDomain:
    if domain.status not in ("pending_verification", "failed"):
        raise AppError("DOMAIN_STATUS_CONFLICT", "Domain is not awaiting verification", 409)
    if hashlib.sha256(raw_token.encode()).hexdigest() != domain.verification_token_hash:
        raise AppError("DOMAIN_VERIFY_FAILED", "Verification token mismatch", 422)
    verifier = get_verifier()
    ok = await verifier.verify(domain.hostname, raw_token)
    if not ok:
        domain.verify_attempts += 1
        if domain.verify_attempts >= MAX_VERIFY_ATTEMPTS:
            domain.status = "failed"
            domain.failure_reason = "verification failed too many times"
        await db.flush()
        raise AppError(
            "DOMAIN_VERIFY_FAILED",
            f"DNS TXT record {VERIFY_RECORD_PREFIX}.{domain.hostname} not found or mismatched",
            422,
        )
    domain.status = "verified"
    domain.verified_at = datetime.now(UTC)
    domain.failure_reason = None
    await record_audit(
        db,
        actor=actor,
        action="domain.verified",
        target_type="tenant_domain",
        target_id=domain.id,
        tenant_id=domain.tenant_id,
    )
    await db.flush()
    return domain


async def activate_domain(db: AsyncSession, domain: TenantDomain, *, actor: Actor) -> TenantDomain:
    """verified → active (explicit act; requires custom_domain entitlement —
    checked at the endpoint). TLS via adapter."""
    result = await db.execute(
        update(TenantDomain)
        .where(TenantDomain.id == domain.id, TenantDomain.status == "verified")
        .values(status="active", activated_at=datetime.now(UTC))
    )
    if not result.rowcount:
        raise AppError("DOMAIN_STATUS_CONFLICT", "Domain must be verified first", 409)
    tls = await get_tls_provisioner().provision(domain.hostname)
    await db.execute(update(TenantDomain).where(TenantDomain.id == domain.id).values(**tls))
    await record_audit(
        db,
        actor=actor,
        action="domain.activated",
        target_type="tenant_domain",
        target_id=domain.id,
        tenant_id=domain.tenant_id,
        after={"hostname": domain.hostname},
    )
    await db.refresh(domain)
    return domain


async def disable_domain(db: AsyncSession, domain: TenantDomain, *, actor: Actor) -> TenantDomain:
    domain.status = "disabled"
    await record_audit(
        db,
        actor=actor,
        action="domain.disabled",
        target_type="tenant_domain",
        target_id=domain.id,
        tenant_id=domain.tenant_id,
    )
    await db.flush()
    return domain


# ── Site context (white-label resolution) ────────────────────


async def resolve_site_context(db: AsyncSession, host: str) -> dict:
    """EXACT match against ACTIVE domains only. The host arrives as an
    explicit query parameter — the backend never trusts the Host header for
    anything (issue §39). Miss → platform default (tenant_id null)."""
    try:
        normalized = normalize_hostname(host)
    except AppError:
        return {"tenant_id": None}
    domain = (
        await db.execute(
            select(TenantDomain).where(
                TenantDomain.hostname == normalized, TenantDomain.status == "active"
            )
        )
    ).scalar_one_or_none()
    if domain is None:
        return {"tenant_id": None}
    # R83[5]: CANCELLED/ARCHIVED tenants kept their white-label domains
    # resolving FOREVER — a terminated tenant's hostname still returned
    # tenant_id + full branding. Terminal states go dark. SUSPENDED keeps
    # resolving by ADR §10.7 (branding is harmless; consumption is blocked
    # elsewhere), and plan downgrades follow no-eviction (§2.9).
    from app.controlplane.models.tenant import TenantAccount, TenantStatus

    t_status = (
        await db.execute(select(TenantAccount.status).where(TenantAccount.id == domain.tenant_id))
    ).scalar_one_or_none()
    if t_status in (TenantStatus.CANCELLED, TenantStatus.ARCHIVED, None):
        return {"tenant_id": None}
    branding = (
        await db.execute(select(TenantBranding).where(TenantBranding.tenant_id == domain.tenant_id))
    ).scalar_one_or_none()
    return {
        "tenant_id": domain.tenant_id,
        "branding": {
            "product_display_name": branding.product_display_name if branding else None,
            "logo_key": branding.logo_key if branding else None,
            "favicon_key": branding.favicon_key if branding else None,
            "theme_tokens": branding.theme_tokens if branding else {},
            "login_tagline": branding.login_tagline if branding else None,
            "legal_links": branding.legal_links if branding else [],
            "support_email": branding.support_email if branding else None,
            "support_url": branding.support_url if branding else None,
        },
    }
