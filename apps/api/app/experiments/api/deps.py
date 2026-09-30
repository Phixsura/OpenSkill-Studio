"""Experiments API dependencies (ADR-017).

Platform routes: writes require platform admin; reads require authentication.
Org-scoped operator routes arrive with the domain-integration phase.
"""

from fastapi import Depends

from app.api.deps import get_current_user
from app.exceptions import AppError
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
