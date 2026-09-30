"""Experiments API dependencies (ADR-017).

Platform routes: writes require platform admin; reads require authentication.
Org-scoped operator routes arrive with the domain-integration phase.
"""

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.exceptions import AppError
from app.models.organization import OrgMember, OrgRole
from app.models.user import User, UserRole


def check_enum(value: str | None, allowed: frozenset[str], name: str) -> None:
    """422 naming the vocabulary — a silently-empty filter is a lie (§106.6)."""
    if value is not None and value not in allowed:
        raise AppError(
            "VALIDATION_ERROR", f"Unknown {name}: {value} (allowed: {sorted(allowed)})", 422
        )


async def require_platform_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise AppError("FORBIDDEN", "Platform admin required", 403)
    return user


class ReadScope:
    """Who may read which experiments (v2 §18 org-admin delegation).

    org_ids is None for platform admins (unrestricted) and the list of orgs
    the user administers otherwise — reads must then be filtered to
    experiments scoped to those orgs, and a non-visible experiment is a
    uniform 404 (R89: no existence oracle on platform experiments)."""

    def __init__(self, user: User, org_ids: list[str] | None):
        self.user = user
        self.org_ids = org_ids


async def experiment_read_scope(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReadScope:
    if user.role == UserRole.ADMIN:
        return ReadScope(user, None)
    org_ids = list(
        (
            await db.execute(
                select(OrgMember.org_id).where(
                    OrgMember.user_id == user.id,
                    OrgMember.role.in_([OrgRole.OWNER, OrgRole.ADMIN]),
                )
            )
        ).scalars()
    )
    if not org_ids:
        raise AppError("FORBIDDEN", "Platform admin or org admin required", 403)
    return ReadScope(user, org_ids)


async def require_self_serve_user(user: User = Depends(get_current_user)) -> User:
    """Self-serve product surfaces (§7): the caller IS the unit — resolve and
    exposure apply to user.id only, so plain authentication is the correct
    gate (no cross-unit probing is possible by construction)."""
    return user
