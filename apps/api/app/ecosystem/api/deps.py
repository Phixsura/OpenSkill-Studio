"""Shared auth helpers for ecosystem endpoints.

Reads: any authenticated user. Platform-intelligence mutations: platform
admin only. Analyst-grade actions reuse the same gate for now (single-role
platform ops), org-scoped resources check membership in the router.
"""

from fastapi import Depends, HTTPException

from app.api.deps import get_current_user
from app.models.user import User, UserRole


async def require_platform_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only platform admins can modify ecosystem intelligence")
    return user


async def eco_audit(
    db,
    user: User,
    *,
    action: str,
    target_type: str,
    target_id: str,
    before: dict | None = None,
    after: dict | None = None,
    reason: str | None = None,
) -> None:
    """§14: irreversible ecosystem admin actions land in the immutable
    commercial audit trail (same store the billing actions use). Fail-safe:
    an audit hiccup must never fail the action it describes."""
    try:
        from app.controlplane import facade as cp_facade
        from app.controlplane.services.audit import Actor

        await cp_facade.record_audit(
            db,
            actor=Actor(user_id=user.id, type="platform"),
            action=action,
            target_type=target_type,
            target_id=target_id,
            before=before,
            after=after,
            reason=reason,
        )
    except Exception:  # noqa: BLE001 — audit is additive, never blocking
        import structlog

        structlog.get_logger().warning("eco_audit_failed", action=action, target=target_id)
