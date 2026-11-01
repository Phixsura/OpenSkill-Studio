"""OAuth2 Authorization Code flow for developer apps."""

import hashlib
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.developer import OAuthTokenResponse
from app.services import developer as dev_svc

router = APIRouter(tags=["OAuth2"])

# In-memory authorization code store (production: use Redis)
_AUTH_CODES: dict[str, dict] = {}
CODE_EXPIRY_SECONDS = 600  # 10 minutes


@router.get(
    "/oauth/authorize",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def authorize(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    response_type: str = "code",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """OAuth2 authorization endpoint — generates an authorization code.

    In a real UI flow, this would render a consent screen. For API-first
    usage, the authenticated user implicitly consents.
    """
    if response_type != "code":
        return DataResponse(
            data={"error": "unsupported_response_type", "state": state}
        )

    # Validate client_id
    app = await dev_svc.get_app_by_client_id(db, client_id)
    if not app:
        return DataResponse(data={"error": "invalid_client", "state": state})

    # Reject revoked/deprecated/draft apps from minting tokens
    from app.models.developer import AppStatus

    allowed_states = {AppStatus.PUBLISHED, AppStatus.APPROVED, AppStatus.TESTING}
    app_status = app.status if isinstance(app.status, AppStatus) else AppStatus(app.status)
    if app_status not in allowed_states:
        return DataResponse(data={"error": "invalid_client", "state": state})

    # Fail closed: redirect_uri must always be registered and match
    if not app.redirect_uris or redirect_uri not in app.redirect_uris:
        return DataResponse(data={"error": "invalid_redirect_uri", "state": state})

    # Validate requested scopes against app's manifest permissions
    requested_scopes = scope.split() if scope else []
    manifest_permissions = (
        app.manifest.get("permissions", []) if app.manifest else []
    )
    if manifest_permissions:
        invalid = [s for s in requested_scopes if s not in manifest_permissions]
        if invalid:
            return DataResponse(
                data={
                    "error": "invalid_scope",
                    "message": f"Scopes not in app manifest: {', '.join(invalid)}",
                    "state": state,
                }
            )

    # Generate authorization code
    code = secrets.token_urlsafe(32)
    _AUTH_CODES[code] = {
        "client_id": client_id,
        "user_id": user.id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "scopes": requested_scopes,
        "app_id": app.id,
        "created_at": datetime.now(UTC),
    }

    return DataResponse(
        data={
            "code": code,
            "state": state,
            "redirect_uri": redirect_uri,
        }
    )


@router.post(
    "/oauth/token",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def token(
    grant_type: str = Form(...),
    code: str | None = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    redirect_uri: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 token endpoint — exchange authorization code for tokens.

    Accepts client credentials via application/x-www-form-urlencoded body.
    """
    # Validate client credentials
    app = await dev_svc.get_app_by_client_id(db, client_id)
    if not app:
        return DataResponse(data={"error": "invalid_client"})

    # Reject revoked/deprecated/draft apps
    from app.models.developer import AppStatus

    allowed_states = {AppStatus.PUBLISHED, AppStatus.APPROVED, AppStatus.TESTING}
    app_status = app.status if isinstance(app.status, AppStatus) else AppStatus(app.status)
    if app_status not in allowed_states:
        return DataResponse(data={"error": "invalid_client"})

    # Verify client secret
    secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
    if secret_hash != app.oauth_client_secret_hash:
        return DataResponse(data={"error": "invalid_client"})

    if grant_type == "authorization_code":
        if not code:
            return DataResponse(
                data={"error": "invalid_request", "message": "code required"}
            )

        # Look up and validate authorization code
        code_data = _AUTH_CODES.pop(code, None)
        if not code_data:
            return DataResponse(data={"error": "invalid_grant"})

        # Check expiry
        elapsed = (datetime.now(UTC) - code_data["created_at"]).total_seconds()
        if elapsed > CODE_EXPIRY_SECONDS:
            return DataResponse(
                data={"error": "invalid_grant", "message": "code expired"}
            )

        # Validate client_id matches
        if code_data["client_id"] != client_id:
            return DataResponse(data={"error": "invalid_grant"})

        # Require redirect_uri match when one was used at /authorize
        if code_data["redirect_uri"] != redirect_uri:
            return DataResponse(data={"error": "invalid_grant"})

        # Generate OAuth access token scoped to user
        # TODO: Extend create_access_token to embed app_id + scopes
        # so auth middleware can enforce scope boundaries per-request
        access_token = create_access_token(
            user_id=code_data["user_id"],
            email="",  # Not needed in JWT payload
            role="user",
        )
        new_refresh_token = secrets.token_urlsafe(48)

        return DataResponse(
            data=OAuthTokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=3600,
                scope=code_data["scope"],
            ).model_dump()
        )

    return DataResponse(data={"error": "unsupported_grant_type"})
