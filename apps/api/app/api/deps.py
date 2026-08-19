"""Shared FastAPI dependencies."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db  # noqa: F401 — re-export
from app.core.security import decode_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the current user from a JWT access token."""
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = await db.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optional auth: returns None when no token is present."""
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


def require_role(*roles: UserRole):
    """Dependency that checks the user has one of the allowed roles."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role.value}' does not have access",
            )
        return user

    return checker


async def require_org_member(
    org_id: str,
    user: User,
    db: AsyncSession,
    *roles,
):
    """Shared helper: verify user is an active org member, optionally with required roles."""
    from sqlalchemy import select

    from app.models.organization import MemberStatus, Organization, OrgMember, OrgStatus

    # Check org exists and is not archived
    org = await db.get(Organization, org_id)
    if org is None or org.status == OrgStatus.ARCHIVED:
        raise HTTPException(status_code=404, detail="Organization not found")

    result = await db.execute(
        select(OrgMember).where(
            OrgMember.org_id == org_id,
            OrgMember.user_id == user.id,
            OrgMember.status == MemberStatus.ACTIVE,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient org permissions")
    return member


async def require_cohort_member(
    cohort_id: str,
    user: User,
    db: AsyncSession,
    *roles,
):
    """Verify user is enrolled in the cohort, optionally with required roles."""
    from sqlalchemy import select

    from app.models.cohort import CohortMember

    result = await db.execute(
        select(CohortMember).where(
            CohortMember.cohort_id == cohort_id,
            CohortMember.user_id == user.id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="Not a member of this cohort")
    if roles and member.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient cohort permissions")
    return member
