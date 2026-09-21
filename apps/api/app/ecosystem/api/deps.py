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
