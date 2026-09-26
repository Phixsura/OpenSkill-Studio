"""Shared auth helpers for ecosystem endpoints.

Reads: any authenticated user. Platform-intelligence mutations: platform
admin only. Analyst-grade actions reuse the same gate for now (single-role
platform ops), org-scoped resources check membership in the router.
"""

from fastapi import Depends, HTTPException, Query

from app.api.deps import get_current_user, oauth2_scheme_optional
from app.api.deps import get_db as _get_db
from app.models.user import User, UserRole


async def get_feed_user(
    bearer: str | None = Depends(oauth2_scheme_optional),
    token: str | None = Query(None, description="Feed token (?token=...)"),
    db=Depends(_get_db),
) -> User:
    """R232: Atom endpoints are consumed by feed readers, which cannot send
    Authorization headers. Accept EITHER a normal Bearer access token OR a
    narrow-scope feed token in the query string. Access tokens are refused
    in the query string on purpose — URLs land in server logs, browser
    history and referrers, and a leaked feed token must only ever grant the
    feed read."""
    from app.core.security import decode_token

    if bearer is not None:
        return await get_current_user(token=bearer, db=db)
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
    if payload.get("type") != "feed":
        raise HTTPException(status_code=401, detail="Invalid token type")
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await db.get(User, sub)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


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
