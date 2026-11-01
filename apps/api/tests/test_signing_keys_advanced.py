"""Advanced tests for signing keys and webhook verification."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"sig-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app
    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager
    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _dev(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Sig"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sig-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "Sig Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    return h


@pytest.mark.asyncio
async def test_register_multiple_keys(c):
    h = await _dev(c)
    for i in range(3):
        r = await c.post("/api/v1/developer/signing-keys", json={
            "name": f"Key {i}",
            "public_key": f"ssh-ed25519 AAAA{'ABCDEF'[i]}" + "X" * 38 + f" key{i}@dev",
        }, headers=h)
        assert r.status_code == 200

    r = await c.get("/api/v1/developer/signing-keys", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 3


@pytest.mark.asyncio
async def test_key_fingerprints_unique(c):
    h = await _dev(c)
    fingerprints = []
    for i in range(3):
        r = await c.post("/api/v1/developer/signing-keys", json={
            "name": f"FP Key {i}",
            "public_key": f"ssh-ed25519 AAAA{'GHI'[i]}" + "Y" * 38 + f" fp{i}@dev",
        }, headers=h)
        fingerprints.append(r.json()["data"]["fingerprint"])
    assert len(set(fingerprints)) == 3


@pytest.mark.asyncio
async def test_signing_keys_require_auth(c):
    r = await c.get("/api/v1/developer/signing-keys")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_signing_key_without_dev_account(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "No"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post("/api/v1/developer/signing-keys", json={"name": "Key", "public_key": "key"}, headers=h)
    assert r.status_code == 404  # no dev account


# ── Webhook verification service ─────────────────────────


def test_webhook_sign_verify_roundtrip():
    from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature
    raw, _ = generate_webhook_secret()
    payload = b'{"event": "submission.completed", "data": {"grade": 85}}'
    sig = sign_payload(payload, raw)
    assert verify_signature(payload, sig, raw)
    assert not verify_signature(b"tampered", sig, raw)
    assert not verify_signature(payload, "sha256=wrong", raw)
    assert not verify_signature(payload, "invalid-format", raw)


def test_webhook_secret_uniqueness():
    from app.services.webhook_verify import generate_webhook_secret
    secrets = [generate_webhook_secret()[0] for _ in range(10)]
    assert len(set(secrets)) == 10


def test_webhook_empty_payload():
    from app.services.webhook_verify import sign_payload, verify_signature
    sig = sign_payload(b"", "secret")
    assert verify_signature(b"", sig, "secret")
