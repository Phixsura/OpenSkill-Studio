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


def test_password_over_72_bytes_hashes_and_verifies():
    """R87: bcrypt 5.0.0 RAISES on passwords >72 bytes (it only consumes the
    first 72), but the password policy allows up to 128 characters — so a
    policy-compliant long password crashed hash_password/verify_password with
    an unhandled 500 on register / login / change-password / reset. We
    pre-truncate to 72 bytes so hashing is total and verification is
    consistent."""
    from app.core.security import hash_password, verify_password

    # 93 chars, policy-valid (<=128, has upper+digit), > 72 bytes
    longpw = "Aa1" + "x" * 90
    assert len(longpw.encode()) > 72
    hashed = hash_password(longpw)  # must not raise
    assert verify_password(longpw, hashed)
    # a password differing WITHIN the first 72 bytes must not verify
    assert not verify_password("Aa1" + "y" * 90, hashed)
    # multibyte (emoji) password past 72 bytes also hashes without raising
    emoji_pw = "Aa1" + "😀" * 30  # 3 + 30*4 = 123 bytes
    assert len(emoji_pw.encode()) > 72
    h2 = hash_password(emoji_pw)
    assert verify_password(emoji_pw, h2)


@pytest.mark.asyncio
async def test_register_and_login_long_password_not_500(client):
    """R87 end-to-end: register + login with a >72-byte password must succeed
    (201 / 200), never 500."""
    import uuid as _uuid

    from app.core.database import engine

    # Fresh pool: pooled connections may be bound to a prior test's (closed)
    # event loop — same hygiene the other client-fixture tests in this file use.
    await engine.dispose()

    email = f"pw72-{_uuid.uuid4().hex[:8]}@test.com"
    longpw = "Aa1" + "x" * 90
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": longpw, "display_name": "PW72"},
    )
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": longpw})
    assert r.status_code == 200, r.text
    # wrong password (differs in first 72 bytes) → 401, not 500
    r = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Aa1" + "y" * 90}
    )
    assert r.status_code == 401, r.text

    await engine.dispose()


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


# ── Revoke-session cookie clearing ───────────────────────────


@pytest.mark.asyncio
async def test_revoke_current_session_clears_cookie(client):
    """Revoking the session backing the CURRENT refresh cookie must delete
    the cookie in the response. The session id (RefreshToken.id) and the
    cookie's jti are unrelated ULIDs — the link is sha256(jti) == token_hash,
    so this is a regression test for the always-false jti == token_id guard."""
    import uuid as _uuid

    from app.core.database import engine

    await engine.dispose()

    email = f"revoke-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Revoke"},
    )
    assert r.status_code == 201
    cookie = r.cookies.get("refresh_token")
    access = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # Only one session exists — it backs the current cookie
    sessions = (await client.get("/api/v1/auth/sessions", headers=headers)).json()["data"]
    assert len(sessions) == 1
    session_id = sessions[0]["id"]

    client.cookies.set("refresh_token", cookie)
    r2 = await client.delete(f"/api/v1/auth/sessions/{session_id}", headers=headers)
    assert r2.status_code == 204
    set_cookie = r2.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "max-age=0" in set_cookie.lower() or 'refresh_token=""' in set_cookie

    await engine.dispose()


@pytest.mark.asyncio
async def test_revoke_other_session_keeps_cookie(client):
    """Revoking a DIFFERENT session must NOT touch the current cookie."""
    import uuid as _uuid

    from app.core.database import engine

    await engine.dispose()

    email = f"revoke2-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Revoke2"},
    )
    assert r.status_code == 201
    headers_a = {"Authorization": f"Bearer {r.json()['access_token']}"}

    old_sessions = (await client.get("/api/v1/auth/sessions", headers=headers_a)).json()["data"]
    old_id = old_sessions[0]["id"]

    # Second login → second session, new cookie (the "current" one)
    r_b = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    assert r_b.status_code == 200
    cookie_b = r_b.cookies.get("refresh_token")
    headers_b = {"Authorization": f"Bearer {r_b.json()['access_token']}"}

    # Revoke the OLD session while presenting cookie B → no cookie clear
    client.cookies.set("refresh_token", cookie_b)
    r2 = await client.delete(f"/api/v1/auth/sessions/{old_id}", headers=headers_b)
    assert r2.status_code == 204
    assert "set-cookie" not in r2.headers

    await engine.dispose()


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


@pytest.mark.asyncio
async def test_logout_kills_rotation_predecessor_within_grace(client):
    """R87 session-revival: rotating tok1→tok2 leaves tok1 revoked-by-rotation
    but still inside the grace window. Logging out with the CURRENT token
    (tok2) must also finalize tok1 — otherwise replaying tok1 is graced and
    revives the just-logged-out session. Logout must be final for the whole
    within-grace chain, while other devices' live sessions stay alive."""
    import uuid as _uuid

    from app.core.database import engine

    await engine.dispose()

    email = f"revive-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Revive"},
    )
    tok1 = r.cookies.get("refresh_token")

    # Second device — its own live session must survive the first's logout
    r_b = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    tok_b = r_b.cookies.get("refresh_token")

    # Device 1 rotates tok1 → tok2
    client.cookies.set("refresh_token", tok1)
    r1 = await client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200
    tok2 = r1.cookies.get("refresh_token")

    # Device 1 logs out with the CURRENT token (tok2)
    client.cookies.set("refresh_token", tok2)
    rlo = await client.post("/api/v1/auth/logout")
    assert rlo.status_code == 204

    # Replaying the rotation-predecessor tok1 (still within grace) must NOT be
    # graced back into a session — the revival the fix closes.
    client.cookies.set("refresh_token", tok1)
    rrev = await client.post("/api/v1/auth/refresh")
    assert rrev.status_code == 401, rrev.text

    # Device 2's independent session is untouched.
    client.cookies.set("refresh_token", tok_b)
    rb = await client.post("/api/v1/auth/refresh")
    assert rb.status_code == 200, rb.text

    await engine.dispose()


@pytest.mark.asyncio
async def test_change_password_kills_rotation_predecessor_within_grace(client):
    """R87: change-password revokes all sessions, but a rotation-predecessor
    token revoked seconds ago would still be graced on replay → session
    survives the password change. _revoke_all_user_tokens must finalize
    within-grace tokens too."""
    import uuid as _uuid

    from app.core.database import engine

    await engine.dispose()

    email = f"cpwd-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Cpwd"},
    )
    tok1 = r.cookies.get("refresh_token")
    access = r.json()["access_token"]

    client.cookies.set("refresh_token", tok1)
    r1 = await client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200

    r2 = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "TestPass123!", "new_password": "NewValid456!"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 204, r2.text

    # Replaying the rotation-revoked tok1 after the password change must 401.
    client.cookies.set("refresh_token", tok1)
    r3 = await client.post("/api/v1/auth/refresh")
    assert r3.status_code == 401, r3.text

    await engine.dispose()


# ── R91: validly-signed token with bad/missing `sub` must 401, not 500 ──


@pytest.mark.asyncio
async def test_me_token_missing_sub_is_401_not_500(client):
    """R91: get_current_user read payload["sub"] with a hard subscript. A
    validly-signed access token missing `sub` (or with a non-str sub) KeyError-
    500'd /auth/me instead of returning 401. Reverting the guard fails this."""
    import jwt

    from app.config import settings
    from app.core.security import ALGORITHM

    for label, payload in (
        ("no-sub", {"type": "access"}),
        ("int-sub", {"type": "access", "sub": 12345}),
        ("empty-sub", {"type": "access", "sub": ""}),
        ("null-sub", {"type": "access", "sub": None}),
    ):
        tok = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
        r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 401, f"{label}: expected 401, got {r.status_code}"
