"""R278: data-driven PRIVILEGE sweep over every /platform route.

R277 (test_cp_endpoints_nodb) proves every controlplane route rejects the
UNAUTHENTICATED; this file proves every /platform route rejects a valid but
UNPRIVILEGED principal (a plain student token): GET/DELETE must be exactly
403/404 (a 2xx or 500 is a privilege hole; 422 would mean body validation
outran the role gate — impossible for body-less methods), body-carrying
methods additionally admit 422. Enumerated from the live route table, so a
future /platform route missing its role gate fails here the day it lands.
"""

import re

import pytest
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient
from ulid import ULID

from app.core.database import AsyncSessionLocal, engine
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User, UserRole, UserStatus


def _platform_routes():
    found = []

    def walk(r):
        if isinstance(r, APIRoute):
            path = "/api/v1" + r.path
            if path.startswith("/api/v1/platform"):
                concrete = re.sub(r"\{[^}]+\}", "01JFAKEFAKEFAKEFAKEFAKEFAK", path)
                for m in sorted(r.methods - {"HEAD", "OPTIONS"}):
                    found.append((m, concrete))
        for sub in getattr(r, "routes", []) or []:
            walk(sub)
        orig = getattr(r, "original_router", None)
        if orig is not None:
            walk(orig)

    for r in app.routes:
        walk(r)
    return sorted(set(found))


@pytest.mark.asyncio
async def test_every_platform_route_rejects_unprivileged_user():
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        user = User(
            email=f"priv-{ULID()}@test.com",
            email_verified=True,
            password_hash=hash_password("Test1234!"),
            display_name="Priv Sweep",
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        await db.commit()
        token = create_access_token(user.id, user.email, "student")

    routes = _platform_routes()
    assert len(routes) > 50, f"route enumeration broke: {len(routes)}"
    offenders = []
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        for method, path in routes:
            kwargs: dict = {"headers": headers}
            if method in ("POST", "PUT", "PATCH"):
                kwargs["json"] = {}
            r = await c.request(method, path, **kwargs)
            allowed = {403, 404} if method in ("GET", "DELETE") else {403, 404, 422}
            if r.status_code not in allowed:
                offenders.append((method, path, r.status_code))
    await engine.dispose()
    assert offenders == [], offenders


@pytest.mark.asyncio
async def test_every_tenant_route_rejects_foreign_tenant_owner():
    """R279: cross-tenant sweep (the R88 existence-oracle class, data-driven).
    A fully-privileged owner of tenant A hitting every /tenants/{tenant_id}
    route with tenant B's REAL id must get uniform 403/404 — never 2xx
    (cross-tenant read/write hole), never 500, and never a differentiated
    status that leaks B's internal state."""
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.audit import Actor

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        owner_a = User(
            email=f"xta-{ULID()}@test.com", email_verified=True,
            password_hash=hash_password("Test1234!"), display_name="A",
            role=UserRole.STUDENT, status=UserStatus.ACTIVE)
        owner_b = User(
            email=f"xtb-{ULID()}@test.com", email_verified=True,
            password_hash=hash_password("Test1234!"), display_name="B",
            role=UserRole.STUDENT, status=UserStatus.ACTIVE)
        db.add_all([owner_a, owner_b])
        await db.flush()
        await tenant_svc.create_tenant(
            db, name=f"XT-A {ULID()}", slug=f"xta-{str(ULID()).lower()}",
            actor=Actor(user_id=owner_a.id, type="platform"),
            owner_user_id=owner_a.id)
        tenant_b = await tenant_svc.create_tenant(
            db, name=f"XT-B {ULID()}", slug=f"xtb-{str(ULID()).lower()}",
            actor=Actor(user_id=owner_b.id, type="platform"),
            owner_user_id=owner_b.id)
        await db.commit()
        token_a = create_access_token(owner_a.id, owner_a.email, "student")
        tenant_b_id = tenant_b.id

    routes = []

    def walk(r):
        if isinstance(r, APIRoute):
            path = "/api/v1" + r.path
            if path.startswith("/api/v1/tenants/{tenant_id}"):
                concrete = path.replace("{tenant_id}", tenant_b_id)
                concrete = re.sub(r"\{[^}]+\}", "01JFAKEFAKEFAKEFAKEFAKEFAK", concrete)
                for m in sorted(r.methods - {"HEAD", "OPTIONS"}):
                    routes.append((m, concrete))
        for sub in getattr(r, "routes", []) or []:
            walk(sub)
        orig = getattr(r, "original_router", None)
        if orig is not None:
            walk(orig)

    for r in app.routes:
        walk(r)
    routes = sorted(set(routes))
    assert len(routes) > 20, f"route enumeration broke: {len(routes)}"

    offenders = []
    headers = {"Authorization": f"Bearer {token_a}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        for method, path in routes:
            kwargs: dict = {"headers": headers}
            if method in ("POST", "PUT", "PATCH"):
                kwargs["json"] = {}
            r2 = await c.request(method, path, **kwargs)
            allowed = {403, 404} if method in ("GET", "DELETE") else {403, 404, 422}
            if r2.status_code not in allowed:
                offenders.append((method, path, r2.status_code))
    await engine.dispose()
    assert offenders == [], offenders
