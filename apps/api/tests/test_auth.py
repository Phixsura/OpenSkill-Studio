"""Auth endpoint + security tests.

Uses FastAPI TestClient (httpx ASGI transport). Tests that need no DB
run against schema validation and error handling. RBAC tests generate
real JWT tokens to test role enforcement.
"""

import pytest

from app.core.security import create_access_token

# ── Schema validation tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    response = await client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_uppercase(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "alllowercase1",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_digit(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "NoDigitsHere",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_common_password_rejected(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Valid123!",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_display_name(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Valid123!",
            "display_name": "A",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    response = await client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_forgot_password_missing_email(client):
    response = await client.post("/api/v1/auth/forgot-password", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_missing_fields(client):
    response = await client.post("/api/v1/auth/reset-password", json={})
    assert response.status_code == 422


# ── Auth-required endpoint tests ─────────────────────────────


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(client):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sessions_without_token(client):
    response = await client.get("/api/v1/auth/sessions")
    assert response.status_code == 401


# ── Admin endpoint auth tests ────────────────────────────────


@pytest.mark.asyncio
async def test_admin_users_without_token(client):
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_require_role_rejects_student_on_admin():
    """RBAC unit test: require_role(ADMIN) rejects student."""
    from unittest.mock import MagicMock

    from fastapi import HTTPException

    from app.api.deps import require_role
    from app.models.user import UserRole

    checker = require_role(UserRole.ADMIN)
    user = MagicMock()
    user.role = UserRole.STUDENT

    with pytest.raises(HTTPException) as exc_info:
        await checker(user)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_rejects_instructor_on_admin():
    """RBAC unit test: require_role(ADMIN) rejects instructor."""
    from unittest.mock import MagicMock

    from fastapi import HTTPException

    from app.api.deps import require_role
    from app.models.user import UserRole

    checker = require_role(UserRole.ADMIN)
    user = MagicMock()
    user.role = UserRole.INSTRUCTOR

    with pytest.raises(HTTPException) as exc_info:
        await checker(user)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_allows_matching_role():
    """RBAC unit test: require_role(ADMIN) allows admin."""
    from unittest.mock import MagicMock

    from app.api.deps import require_role
    from app.models.user import UserRole

    checker = require_role(UserRole.ADMIN)
    user = MagicMock()
    user.role = UserRole.ADMIN

    result = await checker(user)
    assert result is user


@pytest.mark.asyncio
async def test_refresh_without_cookie(client):
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


# ── Endpoint availability tests ──────────────────────────────


@pytest.mark.asyncio
async def test_verify_email_requires_token_param(client):
    response = await client.get("/api/v1/auth/verify-email")
    assert response.status_code == 422  # Missing query param


@pytest.mark.asyncio
async def test_resend_verification_requires_auth(client):
    response = await client.post("/api/v1/auth/resend-verification")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_requires_auth(client):
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "x", "new_password": "y"},
    )
    assert response.status_code == 401


# ── Security module unit tests ───────────────────────────────


def test_password_hash_and_verify():
    from app.core.security import hash_password, verify_password

    hashed = hash_password("MyPassword123!")
    assert hashed != "MyPassword123!"
    assert verify_password("MyPassword123!", hashed)
    assert not verify_password("WrongPassword1!", hashed)


def test_access_token_roundtrip():
    from app.core.security import decode_token

    token = create_access_token("user123", "test@example.com", "student")
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    # email is NOT included in JWT payload to avoid PII exposure
    assert "email" not in payload
    assert payload["role"] == "student"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    from app.core.security import create_refresh_token, decode_token

    token, jti, _expires_at = create_refresh_token("user123")
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_decode_invalid_token_raises():
    import jwt as pyjwt

    from app.core.security import decode_token

    with pytest.raises(pyjwt.InvalidTokenError):
        decode_token("totally.invalid.token")


def test_common_password_check():
    from app.core.passwords import is_common_password

    assert is_common_password("password")
    assert is_common_password("Password")  # case-insensitive
    assert is_common_password("123456")
    assert is_common_password("qwerty")
    assert not is_common_password("xK9#mL2$pQ7!")


# ── Concurrent-refresh grace window (cross-tab race) ─────────


@pytest.mark.asyncio
async def test_refresh_reuse_within_grace_window_succeeds(client):
    """Two browser tabs share the refresh cookie but dedup per tab: the
    loser presents a just-rotated token. Within the grace window that must
    mint a fresh pair, not force a logout."""
    import uuid as _uuid

    email = f"grace-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Grace"},
    )
    assert r.status_code == 201
    cookie = r.cookies.get("refresh_token")
    assert cookie

    # Tab 1 refreshes (rotates the token)
    client.cookies.set("refresh_token", cookie)
    r1 = await client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200

    # Tab 2 re-presents the ORIGINAL (now-revoked) token within the grace
    # window → fresh pair, not 401
    client.cookies.set("refresh_token", cookie)
    r2 = await client.post("/api/v1/auth/refresh")
    assert r2.status_code == 200, r2.text
    assert r2.json()["access_token"]


@pytest.mark.asyncio
async def test_refresh_reuse_after_grace_window_rejected(client):
    """Outside the grace window, reuse of a rotated token is a revoked
    session (or replay) and must 401."""
    import uuid as _uuid
    from datetime import UTC, datetime, timedelta
    from hashlib import sha256

    from app.core.database import AsyncSessionLocal, engine
    from app.core.security import decode_token
    from app.models.user import RefreshToken

    # Fresh pool: earlier tests in this file leave pooled connections bound
    # to their own (closed) event loops ("attached to a different loop")
    await engine.dispose()

    email = f"grace2-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Grace2"},
    )
    cookie = r.cookies.get("refresh_token")

    client.cookies.set("refresh_token", cookie)
    r1 = await client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200

    # Backdate the revocation beyond the grace window
    jti = decode_token(cookie)["jti"]
    token_hash = sha256(jti.encode()).hexdigest()
    async with AsyncSessionLocal() as db:
        from sqlalchemy import update as sa_update

        await db.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=datetime.now(UTC) - timedelta(seconds=60))
        )
        await db.commit()

    client.cookies.set("refresh_token", cookie)
    r2 = await client.post("/api/v1/auth/refresh")
    assert r2.status_code == 401

    # Leave a fresh pool for the next test file (loop hygiene)
    await engine.dispose()
