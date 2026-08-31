"""Control-plane FastAPI dependencies."""

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.controlplane.services.audit import Actor
from app.controlplane.services.tenants import has_platform_role
from app.exceptions import AppError
from app.models.user import User


def require_platform_role(*roles: str):
    """Dependency: user holds any of the given platform roles.

    UserRole.ADMIN bootstraps every platform role (there must always be a
    way in before the first PlatformRoleAssignment exists).
    """

    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        if not await has_platform_role(db, user, *roles):
            raise AppError(
                "PLATFORM_ROLE_REQUIRED",
                "This operation requires a platform role",
                403,
            )
        return user

    return checker


def make_actor(request: Request, user: User | None, actor_type: str = "platform") -> Actor:
    """Build an audit Actor from the request context."""
    return Actor(
        user_id=user.id if user else None,
        type=actor_type,
        request_id=getattr(request.state, "request_id", None),
    )
