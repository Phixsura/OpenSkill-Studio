"""Authentication service — register, login, refresh, logout, password reset, email verify."""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email import get_email_sender
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions import AppError
from app.models.user import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserRole,
    UserStatus,
)

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────────


class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__("INVALID_CREDENTIALS", "Invalid email or password", 401)


class EmailAlreadyExistsError(AppError):
    def __init__(self):
        super().__init__("EMAIL_ALREADY_EXISTS", "An account with this email already exists", 409)


class TokenInvalidError(AppError):
    def __init__(self, detail: str = "Invalid or malformed token"):
        super().__init__("TOKEN_INVALID", detail, 401)


class TokenReuseError(AppError):
    def __init__(self):
        super().__init__("TOKEN_REUSE", "Possible token theft detected", 401)


class AccountSuspendedError(AppError):
    def __init__(self):
        super().__init__("ACCOUNT_SUSPENDED", "Account has been suspended", 403)


# ── DTOs ──────────────────────────────────────────────────────


@dataclass
class AuthResult:
    access_token: str
    refresh_token: str
    user: User


# ── Service ───────────────────────────────────────────────────


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Register ──

    async def register(
        self,
        email: str,
        password: str,
        display_name: str,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> AuthResult:
        email = email.strip().lower()

        # Check uniqueness
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none() is not None:
            raise EmailAlreadyExistsError()

        user = User(
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise EmailAlreadyExistsError() from None

        # Generate email verification token — fire-and-forget so email
        # failure doesn't roll back the user creation. The user can
        # re-request verification via /resend-verification.
        try:
            await self._create_email_verification(user)
        except Exception:
            log.warning("registration_email_failed", user_id=user.id)

        result = await self._create_token_pair(user, ip_address, device_info)

        log.info("auth_register", user_id=user.id)
        return result

    # ── Login ──

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> AuthResult:
        email = email.strip().lower()
        stmt_result = await self.db.execute(select(User).where(User.email == email))
        user = stmt_result.scalar_one_or_none()

        if user is None or not user.has_password:
            # Constant-time: run a dummy bcrypt verify to prevent timing-based
            # user enumeration.  The hash below is a valid bcrypt hash of "dummy".
            verify_password(
                password,
                "$2b$12$LJ3m4ys3Lg2PuxMYNKMsXu3kPBJFHGEPbJDRegqBr0fSE5JOGrFVe",
            )
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):  # type: ignore[arg-type]
            import hashlib

            log.warning(
                "auth_login_failed",
                email_hash=hashlib.sha256(email.encode()).hexdigest()[:12],
                reason="invalid_password",
            )
            raise InvalidCredentialsError()

        if user.status == UserStatus.SUSPENDED:
            raise AccountSuspendedError()

        if user.status == UserStatus.DELETED:
            raise InvalidCredentialsError()

        user.last_login_at = datetime.now(UTC)
        await self.db.flush()

        auth_result = await self._create_token_pair(user, ip_address, device_info)
        log.info("auth_login", user_id=user.id, method="password")
        return auth_result

    # ── Refresh ──

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> AuthResult:
        try:
            payload = decode_token(raw_refresh_token)
        except Exception:
            raise TokenInvalidError("Invalid or expired refresh token") from None

        if payload.get("type") != "refresh":
            raise TokenInvalidError("Not a refresh token")

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise TokenInvalidError("Malformed token payload")

        # Look up token record by hash
        token_hash = sha256(jti.encode()).hexdigest()
        stmt_result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .with_for_update()
        )
        token_record = stmt_result.scalar_one_or_none()

        if token_record is None:
            raise TokenInvalidError("Token not found")

        if token_record.is_revoked:
            # Token was revoked — could be user-initiated session revocation
            # or password change, not necessarily theft. Don't nuke all sessions.
            log.info("auth_revoked_token_used", user_id=user_id, jti=jti)
            raise TokenInvalidError("Session has been revoked. Please log in again.")

        # Revoke old token
        token_record.revoked_at = datetime.now(UTC)

        # Fetch user
        user = await self.db.get(User, user_id)
        if user is None or not user.is_active:
            raise TokenInvalidError("User not found or inactive")

        new_pair = await self._create_token_pair(user, ip_address, device_info)
        await self.db.flush()

        return new_pair

    # ── Logout ──

    async def logout(self, raw_refresh_token: str) -> None:
        try:
            payload = decode_token(raw_refresh_token)
            jti = payload.get("jti")
            if jti:
                token_hash = sha256(jti.encode()).hexdigest()
                stmt_result = await self.db.execute(
                    select(RefreshToken).where(RefreshToken.token_hash == token_hash)
                )
                token_record = stmt_result.scalar_one_or_none()
                if token_record and not token_record.is_revoked:
                    token_record.revoked_at = datetime.now(UTC)
                    await self.db.flush()
        except Exception as exc:
            log.debug("logout_cleanup_failed", error=str(exc))

    # ── Change password ──

    async def change_password(self, user: User, old_password: str, new_password: str) -> None:
        if not user.has_password or not verify_password(
            old_password,
            user.password_hash,  # type: ignore[arg-type]
        ):
            raise InvalidCredentialsError()

        user.password_hash = hash_password(new_password)
        await self._revoke_all_user_tokens(user.id)
        await self.db.flush()
        log.info("auth_password_changed", user_id=user.id)

    # ── Forgot password ──

    async def forgot_password(self, email: str) -> None:
        """Generate a reset token and send email. Always succeeds (no user enumeration)."""
        email = email.strip().lower()
        stmt_result = await self.db.execute(select(User).where(User.email == email))
        user = stmt_result.scalar_one_or_none()

        if user is None:
            # Perform dummy work to equalize timing with the real path,
            # preventing email enumeration via response latency.
            import secrets as _secrets
            from hashlib import sha256 as _sha256

            _secrets.token_urlsafe(32)
            _sha256(_secrets.token_urlsafe(32).encode()).hexdigest()
            return

        # Invalidate any existing reset tokens
        existing = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
        )
        for tok in existing.scalars():
            tok.used_at = datetime.now(UTC)  # Mark as consumed

        # Generate new reset token
        raw_token = secrets.token_urlsafe(32)
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.db.add(token_record)
        await self.db.flush()

        # Send email
        sender = get_email_sender()
        import html as html_mod

        from app.config import settings

        reset_url = f"{settings.frontend_url}/reset-password?token={html_mod.escape(raw_token)}"
        await sender.send(
            to=user.email,
            subject="Reset your OpenSkill Studio password",
            html=f'<p>Click <a href="{html_mod.escape(reset_url)}">here</a> to reset your password. '
            f"This link expires in 1 hour.</p>",
        )

        log.info("auth_password_reset_requested", user_id=user.id)

    # ── Reset password ──

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        """Validate reset token and set new password."""
        token_hash = sha256(raw_token.encode()).hexdigest()
        stmt_result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.token_hash == token_hash)
            .with_for_update()
        )
        token_record = stmt_result.scalar_one_or_none()

        if token_record is None:
            raise TokenInvalidError("Invalid reset token")
        if token_record.used_at is not None:
            raise TokenInvalidError("Reset token already used")
        if token_record.expires_at < datetime.now(UTC):
            raise TokenInvalidError("Reset token expired")

        # Mark token as used
        token_record.used_at = datetime.now(UTC)

        # Update password
        user = await self.db.get(User, token_record.user_id)
        if user is None:
            raise TokenInvalidError("User not found")

        user.password_hash = hash_password(new_password)

        # Revoke all refresh tokens (force re-login)
        await self._revoke_all_user_tokens(user.id)
        await self.db.flush()

        log.info("auth_password_reset_completed", user_id=user.id)

    # ── Email verification ──

    async def verify_email(self, raw_token: str) -> None:
        """Validate verification token and mark email as verified."""
        token_hash = sha256(raw_token.encode()).hexdigest()
        stmt_result = await self.db.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token_hash == token_hash)
            .with_for_update()
        )
        token_record = stmt_result.scalar_one_or_none()

        if token_record is None:
            raise TokenInvalidError("Invalid verification token")
        if token_record.used_at is not None:
            raise TokenInvalidError("Verification token already used")
        if token_record.expires_at < datetime.now(UTC):
            raise TokenInvalidError("Verification token expired")

        token_record.used_at = datetime.now(UTC)

        user = await self.db.get(User, token_record.user_id)
        if user is None:
            raise TokenInvalidError("User not found")

        user.email_verified = True
        await self.db.flush()

        log.info("auth_email_verified", user_id=user.id)

    async def resend_verification(self, user: User) -> None:
        """Resend email verification for the current user."""
        if user.email_verified:
            return

        await self._create_email_verification(user)
        await self.db.flush()

    # ── Sessions ──

    async def list_sessions(self, user_id: str) -> list[RefreshToken]:
        """List active (non-revoked, non-expired) sessions."""
        from sqlalchemy import func

        stmt_result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > func.now(),
            )
            .order_by(RefreshToken.created_at.desc())
        )
        return list(stmt_result.scalars().all())

    async def revoke_session(self, user_id: str, token_id: str) -> None:
        """Revoke a specific session by token ID."""
        token = await self.db.get(RefreshToken, token_id)
        if token is None or token.user_id != user_id:
            raise AppError("NOT_FOUND", "Session not found", 404)
        if token.is_revoked:
            return  # Already revoked

        token.revoked_at = datetime.now(UTC)
        await self.db.flush()

    # ── Helpers ───────────────────────────────────────────────

    async def _create_token_pair(
        self,
        user: User,
        ip_address: str | None = None,
        device_info: str | None = None,
    ) -> AuthResult:
        access = create_access_token(user.id, user.email, user.role.value)
        refresh, jti, expires_at = create_refresh_token(user.id)

        token_record = RefreshToken(
            user_id=user.id,
            token_hash=sha256(jti.encode()).hexdigest(),
            expires_at=expires_at,
            ip_address=ip_address,
            device_info=device_info,
        )
        self.db.add(token_record)

        return AuthResult(
            access_token=access,
            refresh_token=refresh,
            user=user,
        )

    async def _revoke_all_user_tokens(self, user_id: str) -> None:
        stmt_result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        for token in stmt_result.scalars():
            token.revoked_at = datetime.now(UTC)

    async def _create_email_verification(self, user: User) -> None:
        """Generate a verification token and send email."""
        # Invalidate any existing unused verification tokens (same pattern
        # as forgot_password) to prevent stale token accumulation.
        existing = await self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used_at.is_(None),
            )
        )
        for tok in existing.scalars():
            tok.used_at = datetime.now(UTC)

        raw_token = secrets.token_urlsafe(32)
        token_record = EmailVerificationToken(
            user_id=user.id,
            token_hash=sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        self.db.add(token_record)
        await self.db.flush()

        from app.config import settings

        sender = get_email_sender()
        import html as html_mod

        # Points to backend endpoint which verifies and redirects to frontend
        verify_url = f"{settings.frontend_url}/api/v1/auth/verify-email?token={html_mod.escape(raw_token)}"
        await sender.send(
            to=user.email,
            subject="Verify your OpenSkill Studio email",
            html=f'<p>Click <a href="{html_mod.escape(verify_url)}">here</a> to verify your email. '
            f"This link expires in 24 hours.</p>",
        )
