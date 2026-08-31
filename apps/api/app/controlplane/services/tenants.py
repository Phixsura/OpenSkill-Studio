"""Tenant account lifecycle, membership, impersonation (ADR-014 §1)."""

import secrets
from datetime import UTC, datetime, timedelta

import jwt
import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.tenant import (
    TENANT_BLOCKED_STATUSES,
    TENANT_ROLES,
    TENANT_TRANSITIONS,
    SupportImpersonationGrant,
    TenantAccount,
    TenantAccountType,
    TenantMember,
    TenantStatus,
)
from app.controlplane.services.audit import Actor, record_audit
from app.core.security import ALGORITHM
from app.exceptions import AppError
from app.models.organization import Organization
from app.models.user import User, UserRole

log = structlog.get_logger()


# ── Facade helpers ───────────────────────────────────────────


async def get_tenant_for_org(db: AsyncSession, org_id: str) -> TenantAccount:
    """Resolve the owning tenant of an organization."""
    result = await db.execute(
        select(TenantAccount)
        .join(Organization, Organization.tenant_id == TenantAccount.id)
        .where(Organization.id == org_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        # organizations.tenant_id is NOT NULL — this means the org itself is gone
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    return tenant


def require_tenant_active(tenant: TenantAccount) -> None:
    """Block new costed/consuming activity on suspended-class tenants.

    PAST_DUE and TRIAL pass — dunning pressure is billing's concern, and
    trials are working accounts.
    """
    if tenant.status in TENANT_BLOCKED_STATUSES:
        raise AppError(
            "TENANT_SUSPENDED",
            "This account is suspended — contact your administrator",
            403,
        )


# ── Lifecycle ────────────────────────────────────────────────


def _slug_candidate(base: str) -> str:
    return f"{base}-t{secrets.token_hex(2)}"


async def create_tenant(
    db: AsyncSession,
    *,
    name: str,
    slug: str,
    actor: Actor,
    status: TenantStatus = TenantStatus.TRIAL,
    account_type: TenantAccountType = TenantAccountType.DIRECT,
    currency: str = "USD",
    timezone: str = "UTC",
    billing_email: str | None = None,
    country: str | None = None,
    partner_id: str | None = None,
    owner_user_id: str | None = None,
    with_trial: bool = True,
) -> TenantAccount:
    """Create a tenant; retries slug with -tXXXX suffix on collision (×3)."""
    trial_ends = (
        datetime.now(UTC) + timedelta(days=settings.trial_days)
        if (status == TenantStatus.TRIAL and with_trial)
        else None
    )
    last_exc: Exception | None = None
    for candidate in (slug, _slug_candidate(slug), _slug_candidate(slug)):
        exists = await db.execute(
            select(TenantAccount.id).where(TenantAccount.slug == candidate).limit(1)
        )
        if exists.scalar_one_or_none() is not None:
            last_exc = AppError("TENANT_SLUG_TAKEN", "Tenant slug already in use", 409)
            continue
        tenant = TenantAccount(
            name=name,
            slug=candidate,
            status=status,
            trial_ends_at=trial_ends,
            account_type=account_type,
            currency=currency,
            timezone=timezone,
            billing_email=billing_email,
            country=country,
            partner_id=partner_id,
            attributed_at=datetime.now(UTC) if partner_id else None,
            created_by=actor.user_id,
        )
        db.add(tenant)
        await db.flush()
        if owner_user_id:
            db.add(
                TenantMember(
                    tenant_id=tenant.id,
                    user_id=owner_user_id,
                    role="owner",
                    created_by=actor.user_id,
                )
            )
        await record_audit(
            db,
            actor=actor,
            action="tenant.created",
            target_type="tenant",
            target_id=tenant.id,
            tenant_id=tenant.id,
            after={"name": name, "slug": candidate, "status": status.value},
        )
        return tenant
    raise last_exc or AppError("TENANT_SLUG_TAKEN", "Tenant slug already in use", 409)


async def transition_status(
    db: AsyncSession,
    tenant: TenantAccount,
    to_status: TenantStatus,
    *,
    actor: Actor,
    reason: str | None = None,
) -> TenantAccount:
    """Guarded state transition — conditional UPDATE, 0 rows = lost race."""
    from_status = tenant.status
    if to_status not in TENANT_TRANSITIONS.get(from_status, set()):
        raise AppError(
            "TENANT_STATUS_CONFLICT",
            f"Cannot transition tenant from '{from_status.value}' to '{to_status.value}'",
            409,
        )
    values: dict = {"status": to_status}
    if to_status == TenantStatus.SUSPENDED:
        values["suspended_at"] = datetime.now(UTC)
        values["suspension_reason"] = reason
    elif from_status == TenantStatus.SUSPENDED:
        values["suspended_at"] = None
        values["suspension_reason"] = None
    result = await db.execute(
        update(TenantAccount)
        .where(TenantAccount.id == tenant.id, TenantAccount.status == from_status)
        .values(**values)
    )
    if not result.rowcount:
        raise AppError("TENANT_STATUS_CONFLICT", "Tenant status changed concurrently", 409)
    action = {
        TenantStatus.SUSPENDED: "tenant.suspended",
        TenantStatus.ACTIVE: (
            "tenant.reactivated"
            if from_status == TenantStatus.SUSPENDED
            else "tenant.status_changed"
        ),
    }.get(to_status, "tenant.status_changed")
    await record_audit(
        db,
        actor=actor,
        action=action,
        target_type="tenant",
        target_id=tenant.id,
        tenant_id=tenant.id,
        before={"status": from_status.value},
        after={"status": to_status.value},
        reason=reason,
    )
    # Entitlement cache invalidation (P2 wires the cache; safe no-op before)
    from app.controlplane.services.entitlements import invalidate_cache

    await invalidate_cache(tenant.id)
    await db.refresh(tenant)
    return tenant


async def expire_trials(db: AsyncSession) -> int:
    """Worker cron: TRIAL past trial_ends_at with no live paid subscription →
    downgrade to ACTIVE-on-community (or suspend, per settings)."""
    target = (
        TenantStatus.SUSPENDED if settings.trial_expiry_action == "suspend" else TenantStatus.ACTIVE
    )
    rows = (
        (
            await db.execute(
                select(TenantAccount).where(
                    TenantAccount.status == TenantStatus.TRIAL,
                    TenantAccount.trial_ends_at.is_not(None),
                    TenantAccount.trial_ends_at < datetime.now(UTC),
                )
            )
        )
        .scalars()
        .all()
    )
    count = 0
    for tenant in rows:
        # Paid subscription already activated the tenant elsewhere; the guard
        # protects against that race (0 rows → someone else transitioned).
        try:
            await transition_status(
                db,
                tenant,
                target,
                actor=Actor(user_id=None, type="system"),
                reason="trial expired",
            )
            count += 1
        except AppError:
            continue
    return count


# ── Membership ───────────────────────────────────────────────


async def require_tenant_member(
    db: AsyncSession,
    tenant_id: str,
    user: User,
    *roles: str,
) -> TenantMember:
    """Verify tenant exists and user is a member (uniform 404 otherwise).

    UserRole.ADMIN and platform_admin bypass with a virtual owner membership.
    """
    tenant = await db.get(TenantAccount, tenant_id)
    if tenant is None:
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    if await has_platform_role(db, user, "platform_admin"):
        return TenantMember(tenant_id=tenant_id, user_id=user.id, role="owner")
    result = await db.execute(
        select(TenantMember).where(
            TenantMember.tenant_id == tenant_id, TenantMember.user_id == user.id
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        # Uniform 404 — membership check must not become an existence oracle
        raise AppError("TENANT_NOT_FOUND", "Tenant not found", 404)
    if roles and member.role not in roles:
        # Role mismatch is a real 403 — the member already knows the tenant exists
        raise AppError("TENANT_FORBIDDEN", "Insufficient tenant permissions", 403)
    return member


async def has_platform_role(db: AsyncSession, user: User, *roles: str) -> bool:
    """True if user has any of the platform roles (UserRole.ADMIN bootstraps all)."""
    from app.controlplane.models.tenant import PlatformRoleAssignment

    if user.role == UserRole.ADMIN:
        return True
    result = await db.execute(
        select(PlatformRoleAssignment.id)
        .where(
            PlatformRoleAssignment.user_id == user.id,
            PlatformRoleAssignment.role.in_(roles),
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


async def add_tenant_member(
    db: AsyncSession, tenant: TenantAccount, *, user_id: str, role: str, actor: Actor
) -> TenantMember:
    if role not in TENANT_ROLES:
        raise AppError("VALIDATION_ERROR", f"Unknown tenant role '{role}'", 422)
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError("USER_NOT_FOUND", "User not found", 404)
    exists = await db.execute(
        select(TenantMember.id)
        .where(TenantMember.tenant_id == tenant.id, TenantMember.user_id == user_id)
        .limit(1)
    )
    if exists.scalar_one_or_none() is not None:
        raise AppError("TENANT_MEMBER_EXISTS", "User is already a tenant member", 409)
    member = TenantMember(tenant_id=tenant.id, user_id=user_id, role=role, created_by=actor.user_id)
    db.add(member)
    await db.flush()
    return member


async def remove_tenant_member(db: AsyncSession, tenant: TenantAccount, member_id: str) -> None:
    member = await db.get(TenantMember, member_id)
    if member is None or member.tenant_id != tenant.id:
        raise AppError("TENANT_NOT_FOUND", "Tenant member not found", 404)
    if member.role == "owner":
        owners = await db.execute(
            select(func.count(TenantMember.id)).where(
                TenantMember.tenant_id == tenant.id, TenantMember.role == "owner"
            )
        )
        if owners.scalar_one() <= 1:
            raise AppError("LAST_OWNER_REMOVAL", "Cannot remove the last tenant owner", 409)
    await db.delete(member)
    await db.flush()


# ── Impersonation ────────────────────────────────────────────


async def create_impersonation_grant(
    db: AsyncSession,
    *,
    platform_user: User,
    target_user_id: str,
    tenant_id: str | None,
    reason: str,
    expires_in_minutes: int,
    actor: Actor,
) -> SupportImpersonationGrant:
    target = await db.get(User, target_user_id)
    if target is None or not target.is_active:
        raise AppError("USER_NOT_FOUND", "Target user not found", 404)
    # Never impersonate privileged principals.
    if target.role == UserRole.ADMIN or await has_platform_role(
        db, target, "platform_admin", "platform_support", "billing_admin"
    ):
        raise AppError(
            "IMPERSONATION_TARGET_FORBIDDEN",
            "Cannot impersonate platform or admin users",
            422,
        )
    minutes = min(expires_in_minutes, settings.impersonation_max_minutes)
    grant = SupportImpersonationGrant(
        platform_user_id=platform_user.id,
        target_user_id=target_user_id,
        tenant_id=tenant_id,
        reason=reason,
        expires_at=datetime.now(UTC) + timedelta(minutes=minutes),
    )
    db.add(grant)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="impersonation.grant_created",
        target_type="user",
        target_id=target_user_id,
        tenant_id=tenant_id,
        reason=reason,
        after={"grant_id": grant.id, "expires_at": grant.expires_at.isoformat()},
    )
    return grant


async def mint_impersonation_token(
    db: AsyncSession, grant: SupportImpersonationGrant, *, actor: Actor
) -> tuple[str, int]:
    """Mint a short-lived access token carrying imp/imp_grant claims.

    No refresh token is issued — an impersonation session cannot renew itself.
    """
    now = datetime.now(UTC)
    if grant.revoked_at is not None or grant.expires_at <= now:
        raise AppError("IMPERSONATION_EXPIRED", "Impersonation grant expired or revoked", 401)
    target = await db.get(User, grant.target_user_id)
    if target is None or not target.is_active:
        raise AppError("USER_NOT_FOUND", "Target user not found", 404)
    exp = min(grant.expires_at, now + timedelta(minutes=settings.access_token_expire_minutes))
    from ulid import ULID

    payload = {
        "sub": target.id,
        "role": target.role.value,
        "type": "access",
        "iat": now,
        "exp": exp,
        "jti": str(ULID()),
        "imp": grant.platform_user_id,
        "imp_grant": grant.id,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    grant.used_count += 1
    await record_audit(
        db,
        actor=actor,
        action="impersonation.token_minted",
        target_type="user",
        target_id=target.id,
        tenant_id=grant.tenant_id,
        after={"grant_id": grant.id, "used_count": grant.used_count},
    )
    return token, int((exp - now).total_seconds())
