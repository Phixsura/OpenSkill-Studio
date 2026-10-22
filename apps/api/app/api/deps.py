"""Shared FastAPI dependencies."""

from fastapi import Depends, HTTPException, Request
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

    # R91: a validly-signed token missing the `sub` claim (e.g. a token minted
    # for another purpose with the same secret, or a tampered payload) must be
    # rejected as unauthorized, not KeyError-500 the request. Also guard against
    # a non-str sub reaching db.get.
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # R59[5]: revoking an impersonation grant must kill already-minted tokens
    # immediately — they otherwise stayed valid for up to 15 minutes, making
    # /revoke a placebo exactly when it matters (support account compromised,
    # session gone rogue). Impersonated sessions are rare, so a per-request
    # grant point-lookup is negligible and needs no cache to invalidate.
    imp_grant = payload.get("imp_grant")
    if imp_grant is not None:
        from datetime import UTC as _UTC
        from datetime import datetime as _dt

        from app.controlplane.models.tenant import SupportImpersonationGrant

        grant = await db.get(SupportImpersonationGrant, imp_grant)
        if grant is None or grant.revoked_at is not None or grant.expires_at <= _dt.now(_UTC):
            raise HTTPException(status_code=401, detail="Impersonation grant revoked")

    user = await db.get(User, sub)
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
    except HTTPException as exc:
        if exc.status_code == 401:
            return None
        raise


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


def require_app_scopes(*required_scopes: str):
    """Factory: return a dependency that accepts JWT or API key auth.

    When authenticated by API key, the key's scopes must include all
    required_scopes. When no scopes are required (empty), API keys are
    rejected — use get_current_user for JWT-only endpoints.
    """

    async def _dep(
        request: Request,
        token: str | None = Depends(oauth2_scheme_optional),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer osk_app_"):
            if not required_scopes:
                raise HTTPException(
                    status_code=403,
                    detail="API key not accepted on this endpoint",
                )
            return await _authenticate_api_key(request, auth_header, db, set(required_scopes))

        # Fall back to JWT auth
        if token is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await get_current_user(token, db)

    return _dep


async def get_current_user_or_app(
    request: Request,
    token: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authenticate via JWT token or app API key (osk_app_ prefix).

    API key auth is read-only — scopes are stored in request.state for
    downstream checking. For write endpoints, use get_current_user (JWT only)
    or require_app_scopes() for explicit scope gating.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer osk_app_"):
        return await _authenticate_api_key(request, auth_header, db)

    # Fall back to JWT auth
    if token is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await get_current_user(token, db)


async def _authenticate_api_key(
    request: Request,
    auth_header: str,
    db: AsyncSession,
    required_scopes: set[str] | None = None,
) -> User:
    """Resolve an API key to its owner user. Optionally enforce scopes."""
    raw_key = auth_header.removeprefix("Bearer ").strip()
    from app.services.developer import authenticate_api_key

    api_key = await authenticate_api_key(db, raw_key)
    if api_key is None:
        raise HTTPException(status_code=401, detail="Invalid or expired API key")

    # Enforce scopes if required
    if required_scopes:
        granted = set(api_key.scopes or [])
        missing = required_scopes - granted
        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"API key missing required scopes: {', '.join(sorted(missing))}",
            )

    # Check the app is in a valid state
    from sqlalchemy import select

    from app.models.developer import AppStatus, DeveloperApp

    app_result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.id == api_key.app_id)
    )
    app = app_result.scalar_one_or_none()
    if not app or app.status in (AppStatus.REVOKED, AppStatus.DEPRECATED):
        raise HTTPException(status_code=401, detail="App is revoked or deprecated")

    # Resolve the app owner as the acting user
    from app.models.developer import DeveloperAccount

    dev_result = await db.execute(
        select(DeveloperAccount).where(DeveloperAccount.id == app.developer_id)
    )
    dev_account = dev_result.scalar_one_or_none()
    if not dev_account:
        raise HTTPException(status_code=401, detail="Developer account not found")

    user = await db.get(User, dev_account.owner_user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Store API key context for scope checking
    request.state.app_api_key = api_key
    request.state.app_scopes = api_key.scopes or []
    return user
