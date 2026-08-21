from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.config import settings
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SessionResponse,
)
from app.schemas.base import DataResponse
from app.schemas.user import AuthResponse, UpdateProfileRequest, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

COOKIE_OPTS = {
    "key": "refresh_token",
    "httponly": True,
    "secure": settings.app_env != "development",
    "samesite": "lax",
    "max_age": settings.refresh_token_expire_days * 24 * 3600,
    "path": "/",
}


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(value=token, **COOKIE_OPTS)  # type: ignore[arg-type]


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(**{k: v for k, v in COOKIE_OPTS.items() if k != "max_age"})  # type: ignore[arg-type]


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")


# ── Register ──────────────────────────────────────────────


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    dependencies=[Depends(rate_limit(3, 60))],
)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.register(
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        ip_address=_client_ip(request),
        device_info=_user_agent(request),
    )
    await db.commit()

    _set_refresh_cookie(response, result.refresh_token)

    return AuthResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(result.user),
    )


# ── Login ─────────────────────────────────────────────────


@router.post(
    "/login",
    response_model=AuthResponse,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.login(
        email=body.email,
        password=body.password,
        ip_address=_client_ip(request),
        device_info=_user_agent(request),
    )
    await db.commit()

    _set_refresh_cookie(response, result.refresh_token)

    return AuthResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(result.user),
    )


# ── Refresh ───────────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=AuthResponse,
    dependencies=[Depends(rate_limit(30, 60))],
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="No refresh token")

    service = AuthService(db)
    result = await service.refresh_tokens(
        raw_token,
        ip_address=_client_ip(request),
        device_info=_user_agent(request),
    )
    await db.commit()

    _set_refresh_cookie(response, result.refresh_token)

    return AuthResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(result.user),
    )


# ── Logout ────────────────────────────────────────────────


@router.post("/logout", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def logout(
    request: Request,
    response: Response,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        service = AuthService(db)
        await service.logout(raw_token)
        await db.commit()

    _clear_refresh_cookie(response)


# ── Me ────────────────────────────────────────────────────


@router.get("/me", response_model=DataResponse[UserResponse], dependencies=[Depends(rate_limit(60, 60))])
async def get_me(user: User = Depends(get_current_user)):
    return DataResponse(data=UserResponse.model_validate(user))


@router.put("/me", response_model=DataResponse[UserResponse], dependencies=[Depends(rate_limit(10, 60))])
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url

    await db.commit()
    await db.refresh(user)
    return DataResponse(data=UserResponse.model_validate(user))


# ── Change password ───────────────────────────────────────


@router.post("/change-password", status_code=204, dependencies=[Depends(rate_limit(5, 60))])
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.change_password(
        user=user,
        old_password=body.old_password,
        new_password=body.new_password,
    )
    await db.commit()


# ── Forgot password ───────────────────────────────────────


@router.post(
    "/forgot-password",
    status_code=200,
    dependencies=[Depends(rate_limit(3, 900))],
)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Always returns 200 — never reveals whether the email exists."""
    service = AuthService(db)
    await service.forgot_password(body.email)
    await db.commit()
    return {"message": "If an account exists, a reset link has been sent."}


# ── Reset password ────────────────────────────────────────


@router.post(
    "/reset-password",
    status_code=200,
    dependencies=[Depends(rate_limit(5, 900))],
)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.reset_password(body.token, body.new_password)
    await db.commit()
    return {"message": "Password has been reset. Please log in."}


# ── Email verification ───────────────────────────────────


@router.get("/verify-email", dependencies=[Depends(rate_limit(10, 900))])
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import RedirectResponse

    service = AuthService(db)
    await service.verify_email(token)
    await db.commit()
    return RedirectResponse(url=f"{settings.frontend_url}/login?verified=true")


@router.post(
    "/resend-verification",
    status_code=200,
    dependencies=[Depends(rate_limit(3, 900))],
)
async def resend_verification(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.resend_verification(user)
    await db.commit()
    return {"message": "Verification email sent."}


# ── Sessions ──────────────────────────────────────────────


@router.get("/sessions", response_model=DataResponse[list[SessionResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.list_sessions(user.id)
    return DataResponse(data=[SessionResponse.model_validate(t) for t in tokens])


@router.delete("/sessions/{token_id}", status_code=204, dependencies=[Depends(rate_limit(10, 60))])
async def revoke_session(
    token_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.revoke_session(user.id, token_id)
    await db.commit()
